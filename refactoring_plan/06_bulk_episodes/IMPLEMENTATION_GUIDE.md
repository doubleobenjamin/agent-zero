# Bulk Episode Processing Implementation Guide
## Step-by-Step Integration Instructions

**Version:** 1.0  
**Date:** 2025-06-17  
**Objective:** Implement `add_episode_bulk` functionality in the existing Graphiti backend

---

## 🎯 Quick Start

### Prerequisites Checklist
- [ ] Existing memory abstraction layer is working
- [ ] Graphiti backend is properly configured
- [ ] Neo4j database is running
- [ ] OpenAI API key is configured
- [ ] Python 3.10+ with required dependencies

### Estimated Implementation Time
- **Core Implementation**: 4-6 hours
- **Testing & Validation**: 2-3 hours
- **Integration & Documentation**: 1-2 hours
- **Total**: 7-11 hours

---

## 📋 Implementation Steps

### Step 1: Update GraphitiBackend with Bulk Processing

#### 1.1 Add Required Imports

**File:** `python/helpers/memory_graphiti_backend.py`

Add to the imports section:
```python
from graphiti_core.schemas import RawEpisode
import json
```

#### 1.2 Add Bulk Configuration to __init__

Add to the `__init__` method:
```python
def __init__(self):
    # ... existing initialization ...
    self.bulk_batch_size: int = 100
    self.bulk_timeout: int = 300
```

#### 1.3 Update initialize Method

Add bulk configuration parsing to the `initialize` method:
```python
async def initialize(self, config: MemoryConfig) -> None:
    # ... existing initialization ...
    
    # Bulk processing configuration
    self.bulk_batch_size = int(graphiti_config.get("bulk_batch_size", 100))
    self.bulk_timeout = int(graphiti_config.get("bulk_timeout", 300))
```

#### 1.4 Add Bulk Processing Methods

Add these methods to the `GraphitiBackend` class:

```python
async def add_episode_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
    """Add multiple episodes efficiently using Graphiti's bulk API"""
    if not self.client:
        raise RuntimeError("Graphiti client not initialized")

    if not episodes:
        return []

    # Convert to RawEpisode format
    raw_episodes = []
    for episode_data in episodes:
        # Determine episode type
        source = episode_data.get("source", EpisodeType.text)
        if isinstance(source, str):
            source = getattr(EpisodeType, source.upper(), EpisodeType.text)

        # Handle content based on type
        content = episode_data["content"]
        if isinstance(content, dict):
            content = json.dumps(content)

        raw_episode = RawEpisode(
            name=episode_data.get("name", "Bulk Episode"),
            content=content,
            source=source,
            source_description=episode_data.get("source_description", "agent-zero-bulk"),
            reference_time=self._parse_reference_time(episode_data.get("reference_time"))
        )
        raw_episodes.append(raw_episode)

    # Process in batches
    all_uuids = []
    for i in range(0, len(raw_episodes), self.bulk_batch_size):
        batch = raw_episodes[i:i + self.bulk_batch_size]
        try:
            batch_uuids = await self.client.add_episode_bulk(batch)
            all_uuids.extend([str(uuid) for uuid in batch_uuids])
        except Exception as e:
            print(f"Bulk processing failed for batch {i//self.bulk_batch_size + 1}: {e}")
            # Fallback to individual processing
            batch_uuids = await self._process_episodes_individually(batch)
            all_uuids.extend(batch_uuids)

    return all_uuids

async def insert_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
    """Insert multiple knowledge documents with entity extraction"""
    if not self.client:
        raise RuntimeError("Graphiti client not initialized")

    if not documents:
        return []

    # Convert documents to episodes for bulk processing
    episodes_data = []
    for doc in documents:
        episode_data = {
            "name": doc.get("name", f"Knowledge Document: {doc.get('metadata', {}).get('filename', 'Unknown')}"),
            "content": doc["content"],
            "source": EpisodeType.json if isinstance(doc["content"], dict) else EpisodeType.text,
            "source_description": doc.get("source_description",
                                        f"agent-zero-knowledge-{doc.get('metadata', {}).get('area', 'main')}"),
            "reference_time": doc.get("reference_time")
        }
        episodes_data.append(episode_data)

    return await self.add_episode_bulk(episodes_data)

def _parse_reference_time(self, reference_time: Any) -> datetime:
    """Parse reference time from various formats"""
    if reference_time and isinstance(reference_time, str):
        return datetime.fromisoformat(reference_time.replace("Z", "+00:00"))
    elif isinstance(reference_time, datetime):
        return reference_time
    else:
        return datetime.now(timezone.utc)

async def _process_episodes_individually(self, raw_episodes: List[RawEpisode]) -> List[str]:
    """Fallback method to process episodes individually"""
    uuids = []
    for raw_episode in raw_episodes:
        try:
            episode_uuid = await self.client.add_episode(
                name=raw_episode.name,
                episode_body=raw_episode.content,
                source=raw_episode.source,
                source_description=raw_episode.source_description,
                reference_time=raw_episode.reference_time,
                embedding_text=raw_episode.content,
                embedding_model=self.embeddings_model_name
            )
            uuids.append(str(episode_uuid))
        except Exception as e:
            print(f"Failed to process individual episode '{raw_episode.name}': {e}")
            continue
    return uuids
```

### Step 2: Update Memory Abstraction Layer

#### 2.1 Add Bulk Methods to MemoryBackend Interface

**File:** `python/helpers/memory_abstraction.py`

Add these abstract methods to the `MemoryBackend` class:

```python
@abstractmethod
async def add_episode_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
    """Add multiple episodes efficiently"""
    pass

@abstractmethod
async def insert_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
    """Insert multiple knowledge documents with entity extraction"""
    pass
```

#### 2.2 Add Bulk Processing to EnhancedMemoryAbstractionLayer

Add these methods to the `EnhancedMemoryAbstractionLayer` class:

```python
async def add_episodes_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
    """Add multiple episodes efficiently"""
    await self._ensure_initialized()

    if not self.config.bulk_processing_enabled or not self.backend.supports_bulk_processing():
        return await self._process_episodes_individually(episodes)

    return await self.backend.add_episode_bulk(episodes)

async def process_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
    """Process multiple knowledge documents efficiently with entity extraction"""
    await self._ensure_initialized()

    if not documents:
        return []

    # Prepare documents for bulk processing
    prepared_docs = []
    for doc in documents:
        if "content" not in doc:
            continue

        metadata = doc.get("metadata", {})
        prepared_doc = {
            "name": metadata.get("name", f"Knowledge Document: {metadata.get('filename', 'Unknown')}"),
            "content": doc["content"],
            "source": "json" if isinstance(doc["content"], dict) else "text",
            "source_description": metadata.get("source_description",
                                             f"agent-zero-knowledge-{metadata.get('area', 'main')}"),
            "reference_time": metadata.get("timestamp"),
            "metadata": {k: v for k, v in metadata.items()
                       if k not in ["name", "timestamp", "source_description"]}
        }
        prepared_docs.append(prepared_doc)

    # Use bulk processing if available
    if (self.config.bulk_processing_enabled and
        self.backend.supports_bulk_processing() and
        hasattr(self.backend, 'insert_knowledge_documents_bulk')):
        return await self.backend.insert_knowledge_documents_bulk(prepared_docs)
    else:
        # Fallback to individual processing
        doc_ids = []
        for doc in prepared_docs:
            doc_id = await self.backend.insert_knowledge_document(
                doc["content"],
                doc.get("metadata", {})
            )
            doc_ids.append(doc_id)
        return doc_ids

def backend_supports_bulk(self) -> bool:
    """Check if the current backend supports bulk processing"""
    return (self.backend is not None and
            hasattr(self.backend, 'supports_bulk_processing') and
            self.backend.supports_bulk_processing() and
            self.config.bulk_processing_enabled)
```

### Step 3: Update FAISS Backend for Compatibility

#### 3.1 Add Bulk Methods to FaissBackend

**File:** `python/helpers/memory_faiss_backend.py`

Add these methods to the `FaissBackend` class:

```python
async def add_episode_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
    """Add multiple episodes (fallback to individual processing for FAISS)"""
    await self._ensure_legacy_initialized()

    doc_ids = []
    for episode in episodes:
        try:
            content = episode["content"]
            metadata = episode.get("metadata", {})
            area = metadata.get("area", LegacyMemory.Area.MAIN.value)

            doc_id = await self.legacy_memory.insert_text_area(
                text=content,
                area=area,
                metadata=metadata
            )
            doc_ids.append(doc_id)
        except Exception as e:
            print(f"Failed to process episode in FAISS batch: {e}")
            continue

    return doc_ids

async def insert_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
    """Insert multiple knowledge documents (fallback to individual processing)"""
    await self._ensure_legacy_initialized()

    doc_ids = []
    for doc in documents:
        try:
            doc_id = await self.insert_knowledge_document(doc["content"], doc.get("metadata", {}))
            doc_ids.append(doc_id)
        except Exception as e:
            print(f"Failed to process knowledge document in FAISS batch: {e}")
            continue

    return doc_ids

def supports_bulk_processing(self) -> bool:
    """FAISS backend supports bulk processing via fallback"""
    return True
```

### Step 4: Configuration Setup

#### 4.1 Environment Variables

Add to your `.env` file:

```bash
# Bulk processing configuration
MEMORY_BULK_PROCESSING_ENABLED=true
GRAPHITI_BULK_BATCH_SIZE=100
GRAPHITI_BULK_TIMEOUT=300

# Graphiti configuration (if using Graphiti backend)
MEMORY_BACKEND=graphiti
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GRAPHITI_GROUP_ID=agent-zero-default
GRAPHITI_EMBEDDINGS_MODEL=text-embedding-ada-002
```

#### 4.2 Update MemoryConfig

**File:** `python/helpers/memory_abstraction.py`

Update the `MemoryConfig` dataclass:

```python
@dataclass
class MemoryConfig:
    """Memory backend configuration with bulk processing support"""
    backend_type: str
    memory_subdir: str
    embeddings_model: Any
    graphiti_config: Optional[Dict[str, str]] = None
    # Bulk processing configuration
    bulk_processing_enabled: bool = True
    bulk_batch_size: int = 100
    bulk_timeout: int = 300
```

---

## 🧪 Testing & Validation

### Step 5: Run Validation Tests

Execute the validation script:

```bash
cd refactoring_plan/06_bulk_episodes
python BULK_EPISODE_VALIDATION.py
```

### Step 6: Manual Testing

Test bulk processing manually:

```python
# Example usage
from python.helpers.memory_abstraction import EnhancedMemoryAbstractionLayer

# Initialize memory layer
memory_layer = EnhancedMemoryAbstractionLayer(agent)
await memory_layer.initialize()

# Test bulk episode processing
episodes = [
    {
        "name": "Test Episode 1",
        "content": "This is test content 1",
        "source": "text",
        "metadata": {"test": True}
    },
    {
        "name": "Test Episode 2",
        "content": "This is test content 2",
        "source": "text",
        "metadata": {"test": True}
    }
]

episode_ids = await memory_layer.add_episodes_bulk(episodes)
print(f"Created {len(episode_ids)} episodes: {episode_ids}")

# Test bulk knowledge document processing
documents = [
    {
        "content": "Knowledge content 1",
        "metadata": {
            "filename": "doc1.txt",
            "area": "knowledge"
        }
    },
    {
        "content": "Knowledge content 2",
        "metadata": {
            "filename": "doc2.txt",
            "area": "knowledge"
        }
    }
]

doc_ids = await memory_layer.process_knowledge_documents_bulk(documents)
print(f"Processed {len(doc_ids)} knowledge documents: {doc_ids}")
```

---

## ✅ Implementation Checklist

### Core Implementation
- [ ] Add `RawEpisode` import to GraphitiBackend
- [ ] Implement `add_episode_bulk` in GraphitiBackend
- [ ] Implement `insert_knowledge_documents_bulk` in GraphitiBackend
- [ ] Add `_parse_reference_time` helper method
- [ ] Add `_process_episodes_individually` fallback method
- [ ] Update MemoryBackend interface with bulk methods
- [ ] Add bulk methods to EnhancedMemoryAbstractionLayer
- [ ] Add bulk methods to FaissBackend (with fallback)
- [ ] Update MemoryConfig with bulk processing options

### Configuration
- [ ] Add environment variables for bulk processing
- [ ] Update configuration parsing in backends
- [ ] Test configuration validation

### Testing
- [ ] Run bulk episode validation script
- [ ] Test with small batches (10-20 episodes)
- [ ] Test with large batches (100+ episodes)
- [ ] Test error handling and fallback scenarios
- [ ] Test performance comparison (bulk vs individual)
- [ ] Test mixed content processing

### Integration
- [ ] Integrate with knowledge document ingestion pipeline
- [ ] Test backend switching (Graphiti ↔ FAISS)
- [ ] Validate backward compatibility
- [ ] Test with existing memory tools and extensions

---

## 🚨 Common Issues & Solutions

### Issue: ImportError for RawEpisode
**Solution:** Ensure `graphiti-core` is installed with the correct version:
```bash
pip install "graphiti-core[anthropic,groq,google-genai]" --upgrade
```

### Issue: Bulk processing falls back to individual
**Solution:** Check configuration:
- Verify `MEMORY_BULK_PROCESSING_ENABLED=true`
- Ensure Graphiti backend is properly initialized
- Check Neo4j connection

### Issue: Performance not improved with bulk processing
**Solution:**
- Increase batch size: `GRAPHITI_BULK_BATCH_SIZE=200`
- Check network latency to Neo4j
- Monitor memory usage during processing

### Issue: Partial failures in bulk processing
**Solution:** The implementation includes automatic fallback to individual processing for failed batches. Check logs for specific error messages.

---

## 📊 Expected Results

After successful implementation:

### Performance Improvements
- **5-10x faster** processing for batches of 50+ episodes
- **Reduced API calls** to Graphiti/Neo4j
- **Better memory efficiency** for large document sets

### Functional Capabilities
- **Bulk episode creation** with all episode types (text, message, json)
- **Bulk knowledge document processing** with entity extraction
- **Automatic fallback** to individual processing when bulk fails
- **Configuration-controlled** bulk processing behavior

### Backward Compatibility
- **All existing APIs** work unchanged
- **Seamless backend switching** between Graphiti and FAISS
- **No breaking changes** to existing memory operations

---

**🎉 Ready to implement efficient bulk episode processing! Follow the steps above for a successful integration.**

<function_calls>
<invoke name="view">
<parameter name="path">refactoring_plan/06_bulk_episodes/ENHANCED_GRAPHITI_BACKEND.py
