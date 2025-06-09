"""
Qdrant Vector Database Client for Enhanced Memory System
Replaces FAISS with production-ready vector database
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, 
    MatchValue, SearchRequest, CollectionInfo
)
from langchain_core.documents import Document
from python.helpers.database_manager import get_database_manager
from python.helpers.print_style import PrintStyle
import models
from agent import Agent


class QdrantVectorDB:
    """Qdrant vector database client for agent memory"""
    
    def __init__(self, agent: Agent, collection_name: str):
        self.agent = agent
        self.collection_name = collection_name
        self.db_manager = get_database_manager()
        self.client = self.db_manager.qdrant_client
        
        # Get embedding model
        self.embedding_model = models.get_model(
            models.ModelType.EMBEDDING,
            agent.config.embeddings_model.provider,
            agent.config.embeddings_model.name,
            **agent.config.embeddings_model.kwargs,
        )
        
        # Initialize collection
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Get embedding dimension
                sample_embedding = self.embedding_model.embed_query("sample")
                vector_size = len(sample_embedding)
                
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                PrintStyle.standard(f"Created Qdrant collection: {self.collection_name}")
            else:
                PrintStyle.standard(f"Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            PrintStyle.error(f"Failed to ensure collection exists: {e}")
            raise
    
    async def insert_text(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Insert text with metadata into vector database"""
        if metadata is None:
            metadata = {}
        
        # Generate unique ID
        doc_id = str(uuid.uuid4())
        
        # Add timestamp and ID to metadata
        metadata.update({
            "id": doc_id,
            "timestamp": datetime.now().isoformat(),
            "text": text
        })
        
        # Rate limiting
        await self.agent.rate_limiter(
            model_config=self.agent.config.embeddings_model, 
            input=text
        )
        
        # Generate embedding
        embedding = self.embedding_model.embed_query(text)
        
        # Create point
        point = PointStruct(
            id=doc_id,
            vector=embedding,
            payload=metadata
        )
        
        # Insert into Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        PrintStyle.standard(f"Inserted document {doc_id} into {self.collection_name}")
        return doc_id
    
    async def insert_documents(self, docs: List[Document]) -> List[str]:
        """Insert multiple documents into vector database"""
        if not docs:
            return []
        
        points = []
        doc_ids = []
        
        # Prepare text for rate limiting
        texts = [doc.page_content for doc in docs]
        combined_text = "\n".join(texts)
        
        # Rate limiting
        await self.agent.rate_limiter(
            model_config=self.agent.config.embeddings_model,
            input=combined_text
        )
        
        # Generate embeddings and points
        embeddings = self.embedding_model.embed_documents(texts)
        
        for doc, embedding in zip(docs, embeddings):
            doc_id = str(uuid.uuid4())
            doc_ids.append(doc_id)
            
            # Prepare metadata
            metadata = dict(doc.metadata)
            metadata.update({
                "id": doc_id,
                "timestamp": datetime.now().isoformat(),
                "text": doc.page_content
            })
            
            # Create point
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload=metadata
            )
            points.append(point)
        
        # Batch insert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        PrintStyle.standard(f"Inserted {len(docs)} documents into {self.collection_name}")
        return doc_ids
    
    async def search_similarity(self, query: str, limit: int = 10, 
                              threshold: float = 0.7, filter_dict: Dict = None) -> List[Document]:
        """Search for similar documents"""
        # Rate limiting
        await self.agent.rate_limiter(
            model_config=self.agent.config.embeddings_model,
            input=query
        )
        
        # Generate query embedding
        query_embedding = self.embedding_model.embed_query(query)
        
        # Prepare filter
        query_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            if conditions:
                query_filter = Filter(must=conditions)
        
        # Search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=threshold,
            query_filter=query_filter
        )
        
        # Convert to Documents
        documents = []
        for scored_point in search_result:
            payload = scored_point.payload
            text = payload.pop("text", "")
            
            doc = Document(
                page_content=text,
                metadata=payload
            )
            documents.append(doc)
        
        PrintStyle.standard(f"Found {len(documents)} similar documents")
        return documents
    
    async def delete_by_ids(self, ids: List[str]) -> int:
        """Delete documents by IDs"""
        if not ids:
            return 0
        
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
        
        PrintStyle.standard(f"Deleted {len(ids)} documents from {self.collection_name}")
        return len(ids)
    
    def get_collection_info(self) -> Optional[CollectionInfo]:
        """Get collection information"""
        try:
            return self.client.get_collection(self.collection_name)
        except Exception as e:
            PrintStyle.error(f"Failed to get collection info: {e}")
            return None
