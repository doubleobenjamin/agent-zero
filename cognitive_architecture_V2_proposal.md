### **Project Plan: Agent-Zero Upgrade to "Skill-Based Cognitive Architecture"**


**Objective:** To fundamentally re-architect `agent-zero` around the concept of "Skills." The agent will maintain a manifest of its skills, be able to propose and learn new skills dynamically, and use a targeted DGM-based "Training Ground" to measurably improve and level up its competencies over time, as directed by user tasks or explicit user commands.


---


### **Core Pillar 1: The Skill Manifest**


This is the agent's "character sheet." It's a persistent file that defines the agent's identity and capabilities.


**1.1. Create the Skill Manifest (New File)**

*   **File:** `src/agent_zero/knowledge/skill_manifest.json`

*   **Action:** This file will store an array of Skill objects. It's the central repository of what the agent knows how to do.

*   **Structure of a "Skill" Object:**

    ```json

    {

      "skill_id": "unique_skill_identifier_e.g.,_api_development_flask",

      "skill_name": "API Development (Flask)",

      "description": "The ability to design, code, test, and document RESTful APIs using the Flask framework.",

      "level": 1,

      "experience_points": 0,

      "metrics": {

        "success_rate": {

          "description": "Percentage of tasks completed successfully.",

          "value": 0.0

        },

        "efficiency_seconds": {

          "description": "Average time to complete a related task.",

          "value": null

        },

        "code_quality_score": {

          "description": "Average score from linters and static analysis.",

          "value": 0.0

        },

        "test_coverage_percent": {

          "description": "Percentage of code covered by generated unit tests.",

          "value": 0.0

        }

      },

      "training_history": [

        {

          "date": "YYYY-MM-DD",

          "event": "Skill acquired in response to user request for a Flask API.",

          "xp_gained": 100

        }

      ],

      "associated_playbook_ids": ["flask_api_best_practices"]

    }

    ```


---


### **Core Pillar 2: The Skill Orchestrator**


This replaces the `TaskOrchestrator`. It's the "conscious mind" of the agent that analyzes tasks and decides *how* to approach them based on its skills.


**2.1. Refactor the Orchestrator**

*   **File:** `src/agent_zero/orchestrator.py`

*   **Action:** Rewrite it to be skill-aware.


**Workflow of the New `SkillOrchestrator.run()` method:**

1.  **Analyze Request:** Receive the user's prompt (e.g., `"Summarize this 2-hour YouTube video"`).

2.  **Consult Skill Manifest:** Compare the request against the `skill_manifest.json`. The orchestrator uses an LLM to determine the required skills. *"Does this task require `video_transcription`? Does it require `long_text_summarization`?"*

3.  **Identify Skill Gap:** The agent determines it has `long_text_summarization` at Level 5, but it has no skill for `video_transcription`. This is a skill gap.

4.  **Propose New Skill Acquisition (The Dynamic Learning Trigger):**

    *   The orchestrator pauses and reports back to the user (or an automated supervisor): `"To complete this task, I need to learn a new skill: 'Video Transcription'. This involves using libraries like Whisper or AssemblyAI to extract text from video URLs. Do I have permission to define this skill and research the methods to learn it?"`

5.  **Define the New Skill:**

    *   Upon approval, the agent performs research. It identifies key metrics for success (e.g., "word error rate," "transcription speed").

    *   It creates a new entry in `skill_manifest.json` for "Video Transcription" at Level 1, populates the metrics (with initial null values), and creates an initial "playbook" for it.

6.  **Delegate to a "Skill Agent":**

    *   The orchestrator now has the required skills. It instantiates **specialized, temporary sub-agents** whose entire persona is built from the skill definition.

    *   *Sub-Agent 1 (Video Transcription, Lvl 1):* "I am an AI expert in transcribing video content. I use my knowledge of Whisper to extract text from video sources."

    *   *Sub-Agent 2 (Summarization, Lvl 5):* "I am a master of summarization. I can condense vast amounts of text into concise, coherent summaries, paying close attention to nuance and key points."

7.  **Execute and Evaluate:** The sub-agents perform their tasks in a chain. After completion, the orchestrator evaluates their performance against the skill metrics (e.g., it took 300 seconds, the summary was coherent).

8.  **Grant Experience Points (XP) and Level Up:** Based on the evaluation, it updates the `experience_points` for the used skills. If a skill's XP crosses a threshold, its `level` increases, and a new entry is added to its `training_history`.


---


### **Core Pillar 3: The Training Ground (DGM Repurposed)**


The DGM is no longer a general optimizer. It's now the targeted training environment.


**3.1. Create a "train_skill" API Endpoint**

*   **File:** `src/agent_zero/main.py`

*   **Action:** Add a new endpoint, `/train-skill`.

*   **Request Body:** `{"skill_id": "api_development_flask"}`


**3.2. Implement the Training Logic**

*   **When the `/train-skill` endpoint is called:**

    1.  The system retrieves the target skill from the `skill_manifest.json`.

    2.  It loads a **skill-specific benchmark suite** from a new directory, e.g., `benchmarks/api_development_flask/`. This suite contains numerous tasks that specifically test this one skill.

    3.  It activates the DGM loop (`run_dgm.py`).

    4.  The `MetaAgent`'s goal is now highly focused: "Propose a change to a playbook or a custom tool that will increase the benchmark score for the `api_development_flask` skill."

    5.  The DGM runs for a set number of cycles, constantly trying to improve performance against this specific benchmark.

    6.  Each time it finds a provable improvement and "switches," it's considered a successful training session, and the skill gains a significant amount of XP.


### **How this Solves the Generalization Problem**


*   **Core Prompts are Stable:** The agent's core identity and prompts are rarely, if ever, touched. They are general-purpose coordinators.

*   **Knowledge is Externalized:** All specific, hard-won knowledge is stored in the `skill_manifest.json` and its associated playbooks.

*   **Training is Focused:** When the DGM runs, it's not trying to make the agent "better" in a vague sense. It's trying to make it better at **one specific thing**. This allows for deep specialization without causing regression in other areas.

*   **Emergent Specialization:** Over time, by looking at the `skill_manifest.json`, the user (and the agent itself) can see a clear picture of its strengths and weaknesses. It might see `Python Development` at Level 12 but `Creative Writing` at Level 2, giving it a true sense of its own identity.


This plan transforms Agent Zero from a program that improves into a cognitive system that **masters competencies**. It's a far more robust, scalable, and intuitive model for artificial general intelligence. 
# Analysis and Enhancement of Agent Zero's Context and Memory System


## Current Architecture Analysis


Agent Zero's memory system currently uses a vector database approach with summarization techniques:


````python path=python\helpers\memory.py mode=EXCERPT

@staticmethod

async def get(agent: Agent):

    memory_subdir = agent.config.memory_subdir or "default"

    if Memory.index.get(memory_subdir) is None:

        log_item = agent.context.log.log(

            type="util",

            heading=f"Initializing VectorDB in '/{memory_subdir}'",

        )

        db, created = Memory.initialize(

            log_item,

            agent.config.embeddings_model,

            memory_subdir,

            False,

        )

        Memory.index[memory_subdir] = db

        wrap = Memory(agent, db, memory_subdir=memory_subdir)

        if agent.config.knowledge_subdirs:

            await wrap.preload_knowledge(

                log_item, agent.config.knowledge_subdirs, memory_subdir

            )

        return wrap

````


The context management uses a summarization approach:


```` path=docs\architecture.md mode=EXCERPT

- **Message Summaries**: Individual messages are summarized using a structured format that captures key information while reducing token usage.

- **Dynamic Compression**: The system employs an intelligent compression strategy:

  - Recent messages remain in their original form for immediate context.

  - Older messages are gradually compressed into more concise summaries.

  - Multiple compression levels allow for efficient context window usage.

  - Original messages are preserved separately from summaries.

````


Memory fragments are captured through a post-processing extension:


````python path=python\extensions\monologue_end\_50_memorize_fragments.py mode=EXCERPT

async def memorize(self, loop_data: LoopData, log_item: LogItem, **kwargs):

    # get system message and chat history for util llm

    system = self.agent.read_prompt("memory.memories_sum.sys.md")

    msgs_text = self.agent.concat_messages(self.agent.history)


    # call util llm to find info in history

    memories_json = await self.agent.call_utility_model(

        system=system,

        message=msgs_text,

        callback=log_callback,

        background=True,

    )

````


## Proposed Enhancements


### 1. Graph-based Knowledge Representation


#### Integration Approach


Create a new `GraphMemory` class that extends the current vector-based memory system:


````python path=python\helpers\graph_memory.py mode=EDIT

from python.helpers.memory import Memory

import networkx as nx

from typing import Dict, List, Tuple, Any


class GraphMemory(Memory):

    def __init__(self, agent, db, memory_subdir="default"):

        super().__init__(agent, db, memory_subdir)

        self.knowledge_graph = nx.DiGraph()

        self.load_graph()

    

    def load_graph(self):

        """Load existing graph from disk or initialize new one"""

        graph_path = f"memory/{self.memory_subdir}/knowledge_graph.gpickle"

        try:

            self.knowledge_graph = nx.read_gpickle(graph_path)

        except:

            self.knowledge_graph = nx.DiGraph()

    

    def save_graph(self):

        """Save graph to disk"""

        graph_path = f"memory/{self.memory_subdir}/knowledge_graph.gpickle"

        nx.write_gpickle(self.knowledge_graph, graph_path)

    

    async def extract_entities_and_relations(self, text):

        """Extract entities and relations from text using utility model"""

        system = self.agent.read_prompt("memory.graph_extraction.sys.md")

        result = await self.agent.call_utility_model(

            system=system,

            message=text,

            background=True

        )

        # Parse JSON result with entities and relations

        return result

    

    async def add_to_graph(self, text):

        """Process text and add extracted knowledge to graph"""

        extraction = await self.extract_entities_and_relations(text)

        

        # Add entities and relations to graph

        for entity in extraction.get("entities", []):

            if not self.knowledge_graph.has_node(entity["id"]):

                self.knowledge_graph.add_node(entity["id"], **entity)

        

        for relation in extraction.get("relations", []):

            self.knowledge_graph.add_edge(

                relation["source"], 

                relation["target"], 

                type=relation["type"],

                confidence=relation.get("confidence", 1.0)

            )

        

        self.save_graph()

        return len(extraction.get("entities", [])), len(extraction.get("relations", []))

    

    async def query_graph(self, query, max_hops=2):

        """Query the knowledge graph based on semantic similarity and graph traversal"""

        # Find entry points using vector similarity

        entry_nodes = await self.find_similar_nodes(query)

        

        # Traverse graph from entry points

        subgraph = self.extract_subgraph(entry_nodes, max_hops)

        

        # Format results

        return self.format_graph_results(subgraph)

````


Create a new prompt template for entity extraction:


````markdown path=prompts\default\memory.graph_extraction.sys.md mode=EDIT

# Entity and Relation Extraction


You are an expert in knowledge extraction. Your task is to identify entities and their relationships from the provided text.


Extract:

1. Entities (people, concepts, objects, events, etc.)

2. Relationships between these entities


Format your response as JSON with the following structure:

```json

{

  "entities": [

    {"id": "unique_id", "type": "person|concept|object|event", "name": "Entity Name", "attributes": {"key": "value"}},

    ...

  ],

  "relations": [

    {"source": "entity1_id", "target": "entity2_id", "type": "relationship_type", "confidence": 0.95},

    ...

  ]

}

```


Be precise and comprehensive. Use clear relationship types that describe how entities are connected.

````


Modify the memory tool to support graph queries:


````markdown path=prompts\default\agent.system.tool.memory.md mode=EDIT

### memory_graph_query

query the knowledge graph for entities and relationships

- query: natural language query to find relevant entities

- max_hops: maximum number of relationship hops (default: 2)

- focus_entity: optional entity ID to center the query around


usage:

~~~json

{

    "thoughts": [

        "I need to understand the relationships between concepts in my memory",

    ],

    "tool_name": "memory_graph_query",

    "tool_args": {

        "query": "What do I know about machine learning frameworks?",

        "max_hops": 3,

        "focus_entity": "tensorflow"

    }

}

~~~

````


#### Benefits and Challenges


**Benefits:**

- Explicit representation of relationships between concepts

- Better reasoning about complex relationships

- Support for multi-hop queries

- Improved context understanding


**Challenges:**

- Computational overhead for large graphs

- Accurate entity and relation extraction

- Graph storage and serialization

- Integration with existing vector retrieval


#### Evaluation Metrics

- Relationship accuracy (precision/recall of extracted relationships)

- Query relevance compared to vector-only retrieval

- Context coherence in agent responses

- Knowledge graph growth rate and connectivity


### 2. Hybrid RAG Approaches


#### Integration Approach


Create a new `HybridRetriever` class that combines multiple retrieval strategies:


````python path=python\helpers\hybrid_retriever.py mode=EDIT

from python.helpers.memory import Memory

from typing import List, Dict, Any, Tuple

import numpy as np


class HybridRetriever:

    def __init__(self, agent):

        self.agent = agent

        self.memory = Memory.get(agent)

        self.graph_memory = GraphMemory.get(agent) if hasattr(agent.context, "graph_memory") else None

    

    async def retrieve(self, query, strategies=None, weights=None, limit=5):

        """

        Perform hybrid retrieval using multiple strategies

        

        strategies: List of retrieval strategies to use ["vector", "graph", "keyword", "reranking"]

        weights: Weights for each strategy (must match strategies length)

        limit: Maximum number of results to return

        """

        strategies = strategies or ["vector", "reranking"]

        weights = weights or [0.6, 0.4]

        

        all_results = []

        

        # Vector retrieval

        if "vector" in strategies:

            vector_results = await self.memory.search(query, limit=limit*2)

            all_results.extend([(r, "vector") for r in vector_results])

        

        # Graph-based retrieval

        if "graph" in strategies and self.graph_memory:

            graph_results = await self.graph_memory.query_graph(query, max_hops=2)

            all_results.extend([(r, "graph") for r in graph_results])

        

        # Keyword-based retrieval

        if "keyword" in strategies:

            keyword_results = await self.keyword_search(query, limit=limit*2)

            all_results.extend([(r, "keyword") for r in keyword_results])

        

        # Rerank results if requested

        if "reranking" in strategies:

            reranked_results = await self.rerank_results(query, all_results, limit*2)

            return reranked_results[:limit]

        

        # Otherwise just return top results

        return sorted(all_results, key=lambda x: x[0].get("score", 0), reverse=True)[:limit]

    

    async def rerank_results(self, query, results, limit=10):

        """Rerank results using cross-encoder approach with utility model"""

        if not results:

            return []

            

        # Prepare pairs for reranking

        pairs = [(query, r[0].get("content", "")) for r in results]

        

        # Call utility model for reranking

        system = self.agent.read_prompt("memory.reranking.sys.md")

        rerank_input = {

            "query": query,

            "documents": [r[0].get("content", "") for r in results],

            "document_ids": [i for i in range(len(results))]

        }

        

        rerank_result = await self.agent.call_utility_model(

            system=system,

            message=str(rerank_input),

            background=True

        )

        

        # Parse reranking scores

        try:

            reranked_ids = rerank_result.get("ranked_ids", [])

            reranked = [results[id] for id in reranked_ids[:limit]]

            return reranked

        except:

            # Fallback to original order

            return results[:limit]

````


Create a reranking prompt:


````markdown path=prompts\default\memory.reranking.sys.md mode=EDIT

# Document Reranking System


You are a document reranking system. Your task is to rerank a set of documents based on their relevance to a query.


You will receive:

1. A query

2. A list of documents

3. Document IDs


Analyze each document's relevance to the query considering:

- Semantic relevance

- Information completeness

- Factual accuracy

- Recency (if time information is available)


Return a JSON object with the following structure:

```json

{

  "ranked_ids": [0, 3, 1, 2, 4]

}

```


The ranked_ids array should contain the document IDs sorted by relevance (most relevant first).

````


Modify the memory tool to support hybrid retrieval:


````markdown path=prompts\default\agent.system.tool.memory.md mode=EDIT

### memory_hybrid_load

load memories using hybrid retrieval strategies

- query: search query

- strategies: list of strategies to use ["vector", "graph", "keyword", "reranking"]

- weights: optional weights for each strategy

- limit: max results (default=5)


usage:

~~~json

{

    "thoughts": [

        "I need comprehensive information about a topic",

    ],

    "tool_name": "memory_hybrid_load",

    "tool_args": {

        "query": "What do I know about reinforcement learning?",

        "strategies": ["vector", "graph", "reranking"],

        "limit": 7

    }

}

~~~

````


#### Benefits and Challenges


**Benefits:**

- More comprehensive and accurate retrieval

- Reduced dependency on embedding quality

- Better handling of complex queries

- Improved context relevance


**Challenges:**

- Increased computational complexity

- Balancing different retrieval methods

- Determining optimal strategy weights

- Managing increased latency


#### Evaluation Metrics

- Retrieval precision and recall

- Query response time

- Relevance of retrieved context

- User satisfaction with responses


### 3. Contextual Embeddings and Multi-Vector Retrieval


#### Integration Approach


Enhance the Memory class to support multi-vector representations:


````python path=python\helpers\multi_vector_memory.py mode=EDIT

from python.helpers.memory import Memory, MyFaiss

import numpy as np

from typing import List, Dict, Any


class MultiVectorMemory(Memory):

    def __init__(self, agent, db, memory_subdir="default"):

        super().__init__(agent, db, memory_subdir)

        self.chunk_db = self._initialize_chunk_db()

    

    def _initialize_chunk_db(self):

        """Initialize database for chunk-level embeddings"""

        chunk_db_path = f"memory/{self.memory_subdir}/chunk_vectors"

        return MyFaiss.load_local(

            self.agent.config.embeddings_model,

            chunk_db_path,

            create_if_missing=True

        )

    

    async def store_with_chunks(self, content, metadata=None):

        """Store content with both document and chunk-level embeddings"""

        # Store document-level embedding

        doc_id = await self.store(content, metadata)

        

        # Generate chunks

        chunks = self._generate_chunks(content)

        

        # Store chunk embeddings with reference to parent document

        chunk_metadata = metadata.copy() if metadata else {}

        chunk_metadata["parent_id"] = doc_id

        

        for i, chunk in enumerate(chunks):

            chunk_metadata["chunk_id"] = i

            chunk_metadata["chunk_text"] = chunk

            await self._store_chunk(chunk, chunk_metadata)

        

        return doc_id

    

    async def _store_chunk(self, chunk_text, metadata):

        """Store a single chunk with its embedding"""

        embedding = await self._get_embedding(chunk_text)

        return self.chunk_db.add(embedding, metadata)

    

    def _generate_chunks(self, content, chunk_size=200, overlap=50):

        """Split content into overlapping chunks"""

        words = content.split()

        chunks = []

        

        for i in range(0, len(words), chunk_size - overlap):

            chunk = " ".join(words[i:i + chunk_size])

            if chunk:

                chunks.append(chunk)

        

        return chunks

    

    async def search_with_chunks(self, query, limit=5, threshold=0.6):

        """Search using both document and chunk-level embeddings"""

        # Get document-level results

        doc_results = await self.search(query, limit=limit, threshold=threshold)

        

        # Get chunk-level results

        chunk_results = await self._search_chunks(query, limit=limit*2, threshold=threshold)

        

        # Merge results, prioritizing documents with multiple matching chunks

        merged_results = self._merge_search_results(doc_results, chunk_results, limit)

        

        return merged_results

    

    async def _search_chunks(self, query, limit=10, threshold=0.6):

        """Search chunk-level embeddings"""

        embedding = await self._get_embedding(query)

        return self.chunk_db.search(embedding, limit=limit, threshold=threshold)

    

    def _merge_search_results(self, doc_results, chunk_results, limit=5):

        """Merge document and chunk results, removing duplicates and prioritizing by relevance"""

        # Group chunk results by parent document

        parent_docs = {}

        for chunk in chunk_results:

            parent_id = chunk.get("metadata", {}).get("parent_id")

            if parent_id:

                if parent_id not in parent_docs:

                    parent_docs[parent_id] = {"chunks": [], "max_score": 0}

                parent_docs[parent_id]["chunks"].append(chunk)

                parent_docs[parent_id]["max_score"] = max(

                    parent_docs[parent_id]["max_score"], 

                    chunk.get("score", 0)

                )

        

        # Combine with document results

        all_docs = {}

        

        # Add document results

        for doc in doc_results:

            doc_id = doc.get("id")

            if doc_id:

                all_docs[doc_id] = {

                    "document": doc,

                    "chunks": parent_docs.get(doc_id, {}).get("chunks", []),

                    "score": doc.get("score", 0),

                    "chunk_score": parent_docs.get(doc_id, {}).get("max_score", 0)

                }

        

        # Add documents from chunks that weren't in doc results

        for parent_id, parent_data in parent_docs.items():

            if parent_id not in all_docs:

                # Need to fetch the parent document

                parent_doc = self.db.get_by_id(parent_id)

                if parent_doc:

                    all_docs[parent_id] = {

                        "document": parent_doc,

                        "chunks": parent_data["chunks"],

                        "score": 0,

                        "chunk_score": parent_data["max_score"]

                    }

        

        # Sort by combined score (document score + chunk score)

        sorted_results = sorted(

            all_docs.values(),

            key=lambda x: (x["score"] + x["chunk_score"]) / 2,

            reverse=True

        )

        

        # Format results

        final_results = []

        for result in sorted_results[:limit]:

            doc = result["document"]

            # Add matching chunks to the result

            doc["matching_chunks"] = [

                {

                    "text": c.get("metadata", {}).get("chunk_text", ""),

                    "score": c.get("score", 0)

                }

                for c in result["chunks"]

            ]

            final_results.append(doc)

        

        return final_results

````


Add a new memory tool for multi-vector retrieval:


````markdown path=prompts\default\agent.system.tool.memory.md mode=EDIT

### memory_chunk_load

load memories with chunk-level precision

- query: search query

- limit: max results (default=5)

- threshold: similarity threshold (default=0.6)


usage:

~~~json

{

    "thoughts": [

        "I need to find specific details within documents",

    ],

    "tool_name": "memory_chunk_load",

    "tool_args": {

        "query": "What was the specific algorithm used for image classification?",

        "limit": 3,

        "threshold": 0.7

    }

}

~~~

````


# Continuing Analysis and Enhancement of Agent Zero's Context and Memory System


## 3. Contextual Embeddings and Multi-Vector Retrieval (continued)


#### Benefits and Challenges


**Benefits:**

- Finer-grained retrieval at chunk level

- Better handling of long documents

- Improved precision for specific queries

- Context-aware document representation

- Higher recall for relevant information


**Challenges:**

- Increased storage requirements

- Higher computational cost for indexing

- More complex retrieval logic

- Balancing chunk size and overlap


#### Evaluation Metrics

- Precision at different retrieval levels (chunk vs document)

- Recall improvement over single-vector approach

- Query specificity handling

- Storage efficiency

- Retrieval latency


### 4. Structured Memory Hierarchies


#### Integration Approach


Implement a hierarchical memory system with distinct memory types:


````python path=python\helpers\hierarchical_memory.py mode=EDIT

from python.helpers.memory import Memory

from enum import Enum

import time

from typing import Dict, List, Any, Optional


class MemoryType(Enum):

    WORKING = "working"      # Short-term, active context

    EPISODIC = "episodic"    # Specific experiences/conversations

    SEMANTIC = "semantic"    # General knowledge, facts, concepts

    PROCEDURAL = "procedural"  # How to do things, solutions


class HierarchicalMemory:

    def __init__(self, agent):

        self.agent = agent

        self.memory_types = {}

        self.initialize_memory_types()

        

    async def initialize_memory_types(self):

        """Initialize different memory stores"""

        base_memory = await Memory.get(self.agent)

        

        # Working memory is in-memory only (not persisted)

        self.memory_types[MemoryType.WORKING] = {

            "items": [],

            "max_items": 20,

            "ttl": 3600  # 1 hour time-to-live

        }

        

        # Episodic memory uses the base memory system with specific area

        self.memory_types[MemoryType.EPISODIC] = {

            "store": base_memory,

            "area": Memory.Area.FRAGMENTS.value,

            "retention": 0.8  # Higher retention rate

        }

        

        # Semantic memory for facts and concepts

        self.memory_types[MemoryType.SEMANTIC] = {

            "store": base_memory,

            "area": Memory.Area.MAIN.value,

            "retention": 0.9  # Highest retention rate

        }

        

        # Procedural memory for solutions

        self.memory_types[MemoryType.PROCEDURAL] = {

            "store": base_memory,

            "area": Memory.Area.SOLUTIONS.value,

            "retention": 0.85

        }

    

    async def add_to_working_memory(self, content, metadata=None):

        """Add item to working memory"""

        metadata = metadata or {}

        metadata["timestamp"] = time.time()

        

        self.memory_types[MemoryType.WORKING]["items"].append({

            "content": content,

            "metadata": metadata

        })

        

        # Trim if exceeding max items

        max_items = self.memory_types[MemoryType.WORKING]["max_items"]

        if len(self.memory_types[MemoryType.WORKING]["items"]) > max_items:

            self.memory_types[MemoryType.WORKING]["items"] = \

                self.memory_types[MemoryType.WORKING]["items"][-max_items:]

        

        return True

    

    async def store(self, content, memory_type: MemoryType, metadata=None):

        """Store content in specified memory type"""

        if memory_type == MemoryType.WORKING:

            return await self.add_to_working_memory(content, metadata)

        

        # For other memory types, use the base memory store

        memory_config = self.memory_types[memory_type]

        metadata = metadata or {}

        metadata["area"] = memory_config["area"]

        metadata["memory_type"] = memory_type.value

        metadata["retention"] = memory_config["retention"]

        

        return await memory_config["store"].store(content, metadata)

    

    async def search(self, query, memory_types=None, limit=5):

        """Search across specified memory types"""

        memory_types = memory_types or list(MemoryType)

        all_results = []

        

        # Search working memory first (in-memory)

        if MemoryType.WORKING in memory_types:

            working_results = self._search_working_memory(query)

            all_results.extend(working_results)

        

        # Search other memory types

        for memory_type in memory_types:

            if memory_type == MemoryType.WORKING:

                continue  # Already handled

                

            memory_config = self.memory_types[memory_type]

            type_results = await memory_config["store"].search(

                query, 

                limit=limit,

                filter=f"area == '{memory_config['area']}'"

            )

            

            # Add memory type to results

            for result in type_results:

                result["memory_type"] = memory_type.value

                all_results.append(result)

        

        # Sort by relevance and limit

        sorted_results = sorted(all_results, key=lambda x: x.get("score", 0), reverse=True)

        return sorted_results[:limit]

    

    def _search_working_memory(self, query):

        """Search working memory items"""

        # Simple keyword matching for working memory

        # In a real implementation, use embeddings for better matching

        results = []

        for item in self.memory_types[MemoryType.WORKING]["items"]:

            # Check if expired

            timestamp = item["metadata"].get("timestamp", 0)

            ttl = self.memory_types[MemoryType.WORKING]["ttl"]

            if time.time() - timestamp > ttl:

                continue

                

            # Simple relevance score based on keyword matching

            content = item["content"]

            query_words = set(query.lower().split())

            content_words = set(content.lower().split())

            common_words = query_words.intersection(content_words)

            

            if common_words:

                score = len(common_words) / len(query_words)

                results.append({

                    "content": content,

                    "metadata": item["metadata"],

                    "score": score,

                    "memory_type": MemoryType.WORKING.value

                })

        

        return sorted(results, key=lambda x: x["score"], reverse=True)

    

    async def consolidate_working_memory(self):

        """Move important items from working memory to long-term memory"""

        if not self.memory_types[MemoryType.WORKING]["items"]:

            return 0

            

        # Prepare working memory items for consolidation

        items_text = "\n\n".join([

            f"Content: {item['content']}\nMetadata: {item['metadata']}"

            for item in self.memory_types[MemoryType.WORKING]["items"]

        ])

        

        # Call utility model to determine what to consolidate and where

        system = self.agent.read_prompt("memory.consolidation.sys.md")

        consolidation_result = await self.agent.call_utility_model(

            system=system,

            message=items_text,

            background=True

        )

        

        # Process consolidation decisions

        consolidated = 0

        for item in consolidation_result.get("items_to_consolidate", []):

            content = item.get("content")

            memory_type_str = item.get("target_memory")

            importance = item.get("importance", 0.5)

            

            if not content or not memory_type_str:

                continue

                

            try:

                memory_type = MemoryType(memory_type_str)

                metadata = {"importance": importance}

                await self.store(content, memory_type, metadata)

                consolidated += 1

            except:

                continue

        

        # Clear working memory after consolidation

        self.memory_types[MemoryType.WORKING]["items"] = []

        

        return consolidated

````


Create a memory consolidation prompt:


````markdown path=prompts\default\memory.consolidation.sys.md mode=EDIT

# Memory Consolidation System


You are a memory consolidation system. Your task is to analyze working memory items and determine which should be consolidated into long-term memory.


## Memory Types

- EPISODIC: Specific experiences, conversations, or events

- SEMANTIC: General knowledge, facts, concepts, or principles

- PROCEDURAL: How to do things, solutions to problems, or processes


## Your Task

For each working memory item, determine:

1. If it should be consolidated into long-term memory

2. Which memory type it belongs to

3. Its importance (0.0-1.0)


Consider these factors:

- Uniqueness: Is this information novel or repetitive?

- Utility: How useful is this for future tasks?

- Generalizability: Does it apply to multiple situations?

- Emotional significance: Does it have emotional importance?


## Output Format

Return a JSON object with the following structure:

```json

{

  "items_to_consolidate": [

    {

      "content": "The user's name is John Smith",

      "target_memory": "semantic",

      "importance": 0.8,

      "reason": "Personal information about the user that will be useful in future interactions"

    },

    {

      "content": "To solve the Python error, we need to import the missing module",

      "target_memory": "procedural",

      "importance": 0.7,

      "reason": "Solution to a common problem that may recur"

    }

  ],

  "items_to_discard": [

    {

      "content": "The current time is 2:30 PM",

      "reason": "Temporary information with no long-term value"

    }

  ]

}

```

````


Add memory tools for hierarchical memory:


````markdown path=prompts\default\agent.system.tool.memory.md mode=EDIT

### memory_hierarchical_store

store information in the appropriate memory type

- content: text content to store

- memory_type: "working", "episodic", "semantic", or "procedural"

- metadata: optional key-value pairs


usage:

~~~json

{

    "thoughts": [

        "I should store this important fact about the user",

    ],

    "tool_name": "memory_hierarchical_store",

    "tool_args": {

        "content": "User John prefers Python over JavaScript for data analysis",

        "memory_type": "semantic",

        "metadata": {"source": "user_preference", "confidence": 0.9}

    }

}

~~~


### memory_hierarchical_load

search across different memory types

- query: search query

- memory_types: list of types to search ["working", "episodic", "semantic", "procedural"]

- limit: max results (default=5)


usage:

~~~json

{

    "thoughts": [

        "I need to recall information about user preferences",

    ],

    "tool_name": "memory_hierarchical_load",

    "tool_args": {

        "query": "User programming preferences",

        "memory_types": ["semantic", "episodic"],

        "limit": 3

    }

}

~~~


### memory_consolidate

trigger working memory consolidation

moves important items from working memory to long-term memory


usage:

~~~json

{

    "thoughts": [

        "This conversation has important information I should remember long-term",

    ],

    "tool_name": "memory_consolidate",

    "tool_args": {}

}

~~~

````


#### Benefits and Challenges


**Benefits:**

- More human-like memory organization

- Appropriate retention policies for different information types

- Efficient working memory for immediate context

- Better information retrieval based on memory type

- Improved forgetting mechanisms for less important information


**Challenges:**

- Complexity in determining appropriate memory type

- Balancing working memory size and consolidation frequency

- Ensuring consistent memory access across types

- Implementing effective consolidation strategies


#### Evaluation Metrics

- Memory type classification accuracy

- Working memory utilization

- Consolidation effectiveness

- Retrieval speed by memory type

- Context relevance in responses


### 5. Self-Reflection and Memory Consolidation Mechanisms


#### Integration Approach


Implement a self-reflection system that periodically reviews and improves memory:


````python path=python\helpers\reflection.py mode=EDIT

from python.helpers.memory import Memory

import time

import asyncio

from typing import Dict, List, Any


class ReflectionSystem:

    def __init__(self, agent):

        self.agent = agent

        self.last_reflection = 0

        self.reflection_interval = 3600  # 1 hour

        self.reflection_in_progress = False

        self.reflection_queue = []

        

    async def schedule_reflection(self, force=False):

        """Schedule a reflection if enough time has passed"""

        current_time = time.time()

        if force or (current_time - self.last_reflection > self.reflection_interval):

            if not self.reflection_in_progress:

                self.reflection_in_progress = True

                try:

                    await self.perform_reflection()

                finally:

                    self.reflection_in_progress = False

                    self.last_reflection = time.time()

                return True

        return False

    

    async def queue_for_reflection(self, content, importance=0.5):

        """Add content to reflection queue"""

        self.reflection_queue.append({

            "content": content,

            "timestamp": time.time(),

            "importance": importance

        })

        

        # Limit queue size

        if len(self.reflection_queue) > 100:

            # Sort by importance and keep most important

            self.reflection_queue.sort(key=lambda x: x["importance"], reverse=True)

            self.reflection_queue = self.reflection_queue[:50]

        

        # Schedule reflection if queue is getting full

        if len(self.reflection_queue) >= 20:

            asyncio.create_task(self.schedule_reflection())

    

    async def perform_reflection(self):

        """Perform reflection on recent memories and queued items"""

        if not self.reflection_queue:

            return

            

        # Get memory system

        memory = await Memory.get(self.agent)

        

        # Get recent memories for context

        recent_memories = await memory.search(

            "recent important memories",

            limit=10,

            filter=f"timestamp > '{time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))}'"  # Last 24h

        )

        

        # Prepare reflection input

        reflection_items = "\n\n".join([

            f"QUEUED ITEM {i+1}:\n{item['content']}\nImportance: {item['importance']}"

            for i, item in enumerate(self.reflection_queue)

        ])

        

        recent_context = "\n\n".join([

            f"RECENT MEMORY {i+1}:\n{memory.get('content', '')}"

            for i, memory in enumerate(recent_memories)

        ])

        

        reflection_input = f"QUEUED ITEMS FOR REFLECTION:\n{reflection_items}\n\nRECENT CONTEXT:\n{recent_context}"

        

        # Call utility model for reflection

        system = self.agent.read_prompt("memory.reflection.sys.md")

        reflection_result = await self.agent.call_utility_model(

            system=system,

            message=reflection_input,

            background=True

        )

        

        # Process reflection results

        insights = reflection_result.get("insights", [])

        connections = reflection_result.get("connections", [])

        contradictions = reflection_result.get("contradictions", [])

        

        # Store insights

        for insight in insights:

            await memory.store(

                insight["content"],

                metadata={

                    "area": Memory.Area.MAIN.value,

                    "type": "insight",

                    "importance": insight.get("importance", 0.7)

                }

            )

        

        # Store connections

        for connection in connections:

            await memory.store(

                connection["content"],

                metadata={

                    "area": Memory.Area.MAIN.value,

                    "type": "connection",

                    "importance": connection.get("importance", 0.8)

                }

            )

        

        # Handle contradictions

        for contradiction in contradictions:

            # Find the conflicting memories

            conflict_query = contradiction.get("query", "")

            if conflict_query:

                conflicting_memories = await memory.search(

                    conflict_query,

                    limit=5,

                    threshold=0.7

                )

                

                # Store resolution

                await memory.store(

                    contradiction["resolution"],

                    metadata={

                        "area": Memory.Area.MAIN.value,

                        "type": "resolution",

                        "importance": contradiction.get("importance", 0.9),

                        "conflicting_ids": [m.get("id") for m in conflicting_memories]

                    }

                )

        

        # Clear reflection queue

        self.reflection_queue = []

        

        return {

            "insights": len(insights),

            "connections": len(connections),

            "contradictions": len(contradictions)

        }

````


Create a reflection prompt:


````markdown path=prompts\default\memory.reflection.sys.md mode=EDIT

# Memory Reflection System


You are a memory reflection system. Your task is to analyze queued items and recent memories to generate insights, identify connections, and resolve contradictions.


## Your Tasks


1. **Generate Insights**: Identify patterns, principles, or conclusions from the provided information.

2. **Identify Connections**: Find relationships between different pieces of information.

3. **Resolve Contradictions**: Identify and resolve conflicting information.


## Guidelines


- Focus on generating high-quality insights rather than quantity

- Look for non-obvious connections between seemingly unrelated information

- When resolving contradictions, consider recency, source reliability, and consistency with other knowledge

- Assign importance scores (0.0-1.0) based on utility, uniqueness, and generalizability


## Output Format


Return a JSON object with the following structure:

```json

{

  "insights": [

    {

      "content": "The user consistently prefers visual explanations over text-based ones",

      "importance": 0.8,

      "basis": "Items 3, 7, and Recent Memory 2"

    }

  ],

  "connections": [

    {

      "content": "The user's interest in machine learning is specifically focused on NLP applications",

      "importance": 0.7,

      "items_connected": [1, 4, "Recent Memory 3"]

    }

  ],

  "contradictions": [

    {

      "query": "user programming language preference",

      "conflict": "Item 2 indicates Python preference while Recent Memory 5 suggests JavaScript",

      "resolution": "The user prefers Python for data analysis but JavaScript for web development",

      "importance": 0.9

    }

  ]

}

```

````


Add reflection tools:


````markdown path=prompts\default\agent.system.tool.memory.md mode=EDIT

### memory_reflect

trigger reflection on recent memories

analyzes patterns, connections, and contradictions


usage:

~~~json

{

    "thoughts": [

        "I should reflect on what I've learned in this conversation",

    ],

    "tool_name": "memory_reflect",

    "tool_args": {

        "force": true

    }

}

~~~


### memory_queue_for_reflection

add important information to reflection queue

- content: text to reflect on later

- importance: priority score (0.0-1.0)


usage:

~~~json

{

    "thoughts": [

        "This insight should be analyzed during reflection",

    ],

    "tool_name": "memory_queue_for_reflection",

    "tool_args": {

        "content": "User seems to have contradictory requirements for the project",

        "importance": 0.8

    }

}

~~~

````


Create an extension to trigger periodic reflection:


````python path=python\extensions\monologue_end\_55_trigger_reflection.py mode=EDIT

import asyncio

from python.helpers.extension import Extension

from python.helpers.reflection import ReflectionSystem

from agent import LoopData

from python.helpers.log import LogItem



class TriggerReflection(Extension):

    REFLECTION_INTERVAL = 5  # Every 5 iterations


    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):

        # Only run every REFLECTION_INTERVAL iterations

        if loop_data.iteration % self.REFLECTION_INTERVAL != 0:

            return


        # Get or create reflection system

        reflection_system = getattr(self.agent, "reflection_system", None)

        if not reflection_system:

            reflection_system = ReflectionSystem(self.agent)

            setattr(self.agent, "reflection_system", reflection_system)


        # Schedule reflection in background

        asyncio.create_task(self._run_reflection(reflection_system))


    async def _run_reflection(self, reflection_system):

        # Show log message

        log_item = self.agent.context.log.log(

            type="util",

            heading="Reflecting on memories...",

        )


        # Run reflection

        try:

            result = await reflection_system.schedule_reflection()

            if result:

                log_item.update(

                    heading="Memory reflection complete",

                    result=f"Generated {result.get('insights', 0)} insights, " +

                           f"{result.get('connections', 0)} connections, and " +

                           f"resolved {result.get('contradictions', 0)} contradictions."

                )

            else:

                log_item.update(

                    heading="Memory reflection skipped",

                    result="Not enough time has passed since last reflection."

                )

        except Exception as e:

            log_item.update(

                heading="Memory reflection failed",

                result=f"Error: {str(e)}"

            )

````


#### Benefits and Challenges


**Benefits:**

- Continuous knowledge refinement

- Identification of patterns and connections

- Resolution of contradictory information

- Higher-order insights from existing memories

- More coherent mental model over time


**Challenges:**

- Computational overhead of reflection processes

- Determining optimal reflection frequency

- Balancing reflection depth with performance

- Ensuring reflection insights are accurate

- Integrating reflection results into agent behavior


#### Evaluation Metrics

- Quality of generated insights

- Contradiction resolution accuracy

- Connection relevance and novelty

- Impact on agent response quality over time

- Computational efficiency of reflection process


## Implementation Strategy


To implement these enhancements in a phased approach:


1. **Phase 1: Foundation**

   - Implement multi-vector retrieval for immediate retrieval improvements

   - Add basic working memory for short-term context


2. **Phase 2: Advanced Retrieval**

   - Implement hybrid RAG approach

   - Add graph-based knowledge representation


3. **Phase 3: Cognitive Architecture**

   - Implement full hierarchical memory system

   - Add reflection and consolidation mechanisms


````python path=python\extensions\message_loop_start\_15_initialize_memory_systems.py mode=EDIT

from python.helpers.extension import Extension

from python.helpers.memory import Memory

from python.helpers.multi_vector_memory import MultiVectorMemory

from python.helpers.graph_memory import GraphMemory

from python.helpers.hierarchical_memory import HierarchicalMemory

from python.helpers.reflection import ReflectionSystem

from agent import LoopData


class InitializeMemorySystems(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):

        # Initialize base memory if not already done

        if not hasattr(self.agent, "memory"):

            self.agent.memory = await Memory.get(self.agent)

        

        # Initialize enhanced memory systems based on config

        config = self.agent.config

        

        # Multi-vector memory (chunk-level retrieval)

        if config.get("use_multi_vector_memory", True):

            if not hasattr(self.agent, "multi_vector_memory"):

                self.agent.multi_vector_memory = MultiVectorMemory(

                    self.agent, 

                    self.agent.memory.db, 

                    self.agent.memory.memory_subdir

                )

        

        # Graph memory

        if config.get("use_graph_memory", True):

            if not hasattr(self.agent, "graph_memory"):

                self.agent.graph_memory = GraphMemory(

                    self.agent, 

                    self.agent.memory.db, 

                    self.agent.memory.memory_subdir

                )

        

        # Hierarchical memory

        if config.get("use_hierarchical_memory", True):

            if not hasattr(self.agent, "hierarchical_memory"):

                self.agent.hierarchical_memory = HierarchicalMemory(self.agent)

        

        # Reflection system

        if config.get("use_reflection", True):

            if not hasattr(self.agent, "reflection_system"):

                self.agent.reflection_system = ReflectionSystem(self.agent)

````


## Conclusion


The proposed enhancements to Agent Zero's memory system would transform it from a basic vector-based retrieval system to a cognitively-inspired architecture with multiple memory types, advanced retrieval mechanisms, and self-improvement capabilities. These improvements would enable:


1. More precise and relevant information retrieval

2. Better understanding of relationships between concepts

3. Human-like memory organization with appropriate forgetting mechanisms

4. Continuous knowledge refinement through reflection

5. More coherent and contextually appropriate responses


By implementing these enhancements, Agent Zero would move closer to a truly cognitive architecture that can maintain context, build cumulative knowledge, and provide more helpful and contextually appropriate assistance over time. 

# Optimizing Agent Zero's Cognitive Architecture for Efficiency


To improve efficiency in the newly designed cognitive architecture, we need to implement dynamic resource allocation based on task requirements. This ensures Agent Zero uses only the memory techniques necessary for each specific task.


## Dynamic Memory System Selection


````python path=python\helpers\memory_orchestrator.py mode=EDIT

from enum import Enum

from typing import Dict, List, Set, Optional

import time

import asyncio


class TaskComplexity(Enum):

    SIMPLE = "simple"       # Quick, factual responses

    MODERATE = "moderate"   # Multi-step reasoning, some context

    COMPLEX = "complex"     # Deep reasoning, extensive context


class MemorySystem(Enum):

    BASE = "base"                   # Basic vector retrieval

    MULTI_VECTOR = "multi_vector"   # Chunk-level retrieval

    GRAPH = "graph"                 # Relationship-based retrieval

    HIERARCHICAL = "hierarchical"   # Multi-type memory organization

    REFLECTION = "reflection"       # Self-improvement mechanisms


class MemoryOrchestrator:

    def __init__(self, agent):

        self.agent = agent

        self.active_systems = {MemorySystem.BASE}  # Base system always active

        self.system_usage_stats = {system: {"calls": 0, "latency": 0} for system in MemorySystem}

        self.task_complexity = TaskComplexity.MODERATE  # Default assumption

        

    async def analyze_task_complexity(self, query: str) -> TaskComplexity:

        """Determine task complexity based on query analysis"""

        # Use utility model to analyze query complexity

        system_prompt = self.agent.read_prompt("memory.task_analyzer.sys.md")

        result = await self.agent.call_utility_model(

            system=system_prompt,

            message=query,

            background=True

        )

        

        complexity = result.get("complexity", "moderate")

        try:

            return TaskComplexity(complexity)

        except ValueError:

            return TaskComplexity.MODERATE

    

    def get_recommended_systems(self, complexity: TaskComplexity) -> Set[MemorySystem]:

        """Get recommended memory systems based on task complexity"""

        if complexity == TaskComplexity.SIMPLE:

            return {MemorySystem.BASE}

        elif complexity == TaskComplexity.MODERATE:

            return {MemorySystem.BASE, MemorySystem.MULTI_VECTOR}

        else:  # COMPLEX

            return {MemorySystem.BASE, MemorySystem.MULTI_VECTOR, 

                   MemorySystem.GRAPH, MemorySystem.HIERARCHICAL}

    

    async def optimize_for_task(self, query: str):

        """Optimize active memory systems for the current task"""

        # Analyze task complexity

        complexity = await self.analyze_task_complexity(query)

        self.task_complexity = complexity

        

        # Get recommended systems

        recommended = self.get_recommended_systems(complexity)

        

        # Update active systems

        self.active_systems = recommended

        

        # Initialize systems if needed

        await self._ensure_systems_initialized()

        

        return {

            "complexity": complexity.value,

            "active_systems": [system.value for system in self.active_systems]

        }

    

    async def _ensure_systems_initialized(self):

        """Ensure all active memory systems are initialized"""

        for system in self.active_systems:

            if system == MemorySystem.BASE:

                if not hasattr(self.agent, "memory"):

                    self.agent.memory = await Memory.get(self.agent)

            

            elif system == MemorySystem.MULTI_VECTOR:

                if not hasattr(self.agent, "multi_vector_memory"):

                    self.agent.multi_vector_memory = MultiVectorMemory(

                        self.agent, 

                        self.agent.memory.db, 

                        self.agent.memory.memory_subdir

                    )

            

            elif system == MemorySystem.GRAPH:

                if not hasattr(self.agent, "graph_memory"):

                    self.agent.graph_memory = GraphMemory(

                        self.agent, 

                        self.agent.memory.db, 

                        self.agent.memory.memory_subdir

                    )

            

            elif system == MemorySystem.HIERARCHICAL:

                if not hasattr(self.agent, "hierarchical_memory"):

                    self.agent.hierarchical_memory = HierarchicalMemory(self.agent)

            

            elif system == MemorySystem.REFLECTION:

                if not hasattr(self.agent, "reflection_system"):

                    self.agent.reflection_system = ReflectionSystem(self.agent)

    

    async def search(self, query: str, limit: int = 5, **kwargs):

        """Search across active memory systems with smart routing"""

        start_time = time.time()

        results = []

        

        # Always search base memory

        base_results = await self.agent.memory.search_similarity_threshold(

            query=query, 

            limit=limit, 

            threshold=0.6

        )

        results.extend(base_results)

        

        # Search other active systems based on task complexity

        search_tasks = []

        

        if MemorySystem.MULTI_VECTOR in self.active_systems:

            search_tasks.append(self.agent.multi_vector_memory.search(query, limit=limit))

            

        if MemorySystem.GRAPH in self.active_systems and self.task_complexity == TaskComplexity.COMPLEX:

            search_tasks.append(self.agent.graph_memory.search(query, limit=limit))

            

        if MemorySystem.HIERARCHICAL in self.active_systems:

            # For hierarchical, determine which memory types to search based on query

            memory_types = self._determine_memory_types(query)

            search_tasks.append(self.agent.hierarchical_memory.search(query, memory_types=memory_types, limit=limit))

        

        # Run searches in parallel

        if search_tasks:

            additional_results = await asyncio.gather(*search_tasks)

            for result_set in additional_results:

                results.extend(result_set)

        

        # Deduplicate and rank results

        unique_results = self._deduplicate_results(results)

        ranked_results = self._rank_results(unique_results, query)

        

        # Update usage statistics

        elapsed = time.time() - start_time

        for system in self.active_systems:

            self.system_usage_stats[system]["calls"] += 1

            self.system_usage_stats[system]["latency"] += elapsed / len(self.active_systems)

        

        return ranked_results[:limit]

    

    def _determine_memory_types(self, query: str) -> List[str]:

        """Determine which memory types to search based on query"""

        memory_types = ["working"]  # Always include working memory

        

        # Simple heuristics for memory type selection

        query_lower = query.lower()

        

        if any(word in query_lower for word in ["remember", "recall", "happened", "conversation", "said"]):

            memory_types.append("episodic")

            

        if any(word in query_lower for word in ["know", "fact", "information", "concept", "definition"]):

            memory_types.append("semantic")

            

        if any(word in query_lower for word in ["how to", "solve", "solution", "procedure", "steps"]):

            memory_types.append("procedural")

        

        # If no specific types matched, search all types

        if len(memory_types) == 1:

            memory_types.extend(["episodic", "semantic", "procedural"])

            

        return memory_types

    

    def _deduplicate_results(self, results):

        """Remove duplicate results based on content similarity"""

        seen_ids = set()

        unique_results = []

        

        for result in results:

            result_id = result.metadata.get("id", "")

            if result_id and result_id in seen_ids:

                continue

                

            seen_ids.add(result_id)

            unique_results.append(result)

            

        return unique_results

    

    def _rank_results(self, results, query):

        """Rank results based on relevance and source system"""

        # This could be enhanced with a more sophisticated ranking algorithm

        # For now, we'll use a simple scoring approach

        for result in results:

            base_score = result.metadata.get("score", 0.5)

            

            # Adjust score based on memory system

            system = result.metadata.get("system", "base")

            if system == "multi_vector" and self.task_complexity != TaskComplexity.SIMPLE:

                base_score *= 1.2

            elif system == "graph" and self.task_complexity == TaskComplexity.COMPLEX:

                base_score *= 1.3

            elif system == "hierarchical":

                memory_type = result.metadata.get("memory_type", "")

                if memory_type == "working":

                    base_score *= 1.5  # Prioritize working memory

                elif memory_type == "procedural" and "how to" in query.lower():

                    base_score *= 1.4  # Prioritize procedural for how-to queries

            

            # Adjust for recency

            timestamp = result.metadata.get("timestamp", "")

            if timestamp:

                try:

                    # Boost recent memories

                    time_diff = time.time() - float(timestamp)

                    recency_boost = max(0.8, 1.0 - (time_diff / (7 * 24 * 3600)))  # Decay over a week

                    base_score *= recency_boost

                except:

                    pass

            

            result.metadata["adjusted_score"] = base_score

            

        # Sort by adjusted score

        return sorted(results, key=lambda x: x.metadata.get("adjusted_score", 0), reverse=True)

    

    def get_performance_metrics(self):

        """Get performance metrics for memory systems"""

        return {

            "active_systems": [system.value for system in self.active_systems],

            "task_complexity": self.task_complexity.value,

            "system_stats": {system.value: stats for system, stats in self.system_usage_stats.items()}

        }

````


Create a task analyzer prompt:


````markdown path=prompts\default\memory.task_analyzer.sys.md mode=EDIT

# Task Complexity Analyzer


You are a task complexity analyzer for Agent Zero's memory system. Your job is to analyze user queries and determine their complexity level to optimize memory system usage.


## Complexity Levels


1. **Simple**

   - Straightforward factual questions

   - Simple clarifications

   - Basic commands

   - Minimal context needed

   - Example: "What's the capital of France?"


2. **Moderate**

   - Multi-step reasoning

   - Some context required

   - Moderate domain knowledge

   - Example: "Explain how to implement a basic sorting algorithm in Python"


3. **Complex**

   - Deep reasoning chains

   - Extensive context needed

   - Relationship understanding required

   - Multiple domains or concepts

   - Example: "Compare different architectural patterns for a microservice system and recommend one for my e-commerce platform"


## Your Task


Analyze the provided query and determine its complexity level.


## Output Format


Return a JSON object with the following structure:

```json

{

  "complexity": "simple|moderate|complex",

  "reasoning": "Brief explanation of why this complexity level was chosen",

  "memory_systems_needed": ["base", "multi_vector", "graph", "hierarchical"]

}

```

````


## Adaptive Memory Extension


````python path=python\extensions\message_loop_start\_10_adaptive_memory.py mode=EDIT

from python.helpers.extension import Extension

from python.helpers.memory_orchestrator import MemoryOrchestrator

from agent import LoopData


class AdaptiveMemory(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):

        # Initialize memory orchestrator if not already done

        if not hasattr(self.agent, "memory_orchestrator"):

            self.agent.memory_orchestrator = MemoryOrchestrator(self.agent)

        

        # Get user message

        user_message = loop_data.user_message

        if not user_message:

            return

            

        # Optimize memory systems for this task

        log_item = self.agent.context.log.log(

            type="util",

            heading="Optimizing memory systems...",

        )

        

        try:

            result = await self.agent.memory_orchestrator.optimize_for_task(user_message)

            

            log_item.update(

                heading="Memory systems optimized",

                result=f"Task complexity: {result['complexity']}\n" +

                       f"Active systems: {', '.join(result['active_systems'])}"

            )

        except Exception as e:

            log_item.update(

                heading="Memory optimization failed",

                result=f"Error: {str(e)}"

            )

````


## Memory Tool Adapter


````python path=python\tools\memory_adaptive.py mode=EDIT

from python.helpers.tool import Tool, Response


class MemoryAdaptive(Tool):

    async def execute(self, query="", limit=5, **kwargs):

        # Use memory orchestrator if available, otherwise fall back to regular memory

        if hasattr(self.agent, "memory_orchestrator"):

            results = await self.agent.memory_orchestrator.search(

                query=query, 

                limit=limit, 

                **kwargs

            )

        else:

            # Fall back to regular memory search

            db = await Memory.get(self.agent)

            results = await db.search_similarity_threshold(

                query=query, 

                limit=limit, 

                threshold=0.6

            )

            

        if len(results) == 0:

            result = self.agent.read_prompt("fw.memories_not_found.md", query=query)

        else:

            text = "\n\n".join(Memory.format_docs_plain(results))

            result = str(text)

            

        # Include memory system info

        if hasattr(self.agent, "memory_orchestrator"):

            metrics = self.agent.memory_orchestrator.get_performance_metrics()

            result += f"\n\n[Memory systems used: {', '.join(metrics['active_systems'])}]"


        return Response(message=result, break_loop=False)

````


## Key Efficiency Improvements


### 1. Task-Based Memory Selection


The `MemoryOrchestrator` analyzes each task and activates only the necessary memory systems:


- **Simple tasks**: Use only basic vector retrieval

- **Moderate tasks**: Add multi-vector retrieval for better precision

- **Complex tasks**: Activate graph and hierarchical memory for deeper context


### 2. Smart Memory Type Routing


For hierarchical memory, the system intelligently selects which memory types to query:


- **Episodic memory**: For questions about past conversations or events

- **Semantic memory**: For factual knowledge queries

- **Procedural memory**: For how-to questions and solutions

- **Working memory**: Always checked for immediate context


### 3. Parallel Retrieval with Early Termination


````python path=python\helpers\memory_orchestrator.py mode=EDIT

async def search_with_timeout(self, query: str, limit: int = 5, timeout: float = 0.5, **kwargs):

    """Search with timeout to prevent slow retrievals"""

    # Create tasks for each memory system

    search_tasks = []

    for system in self.active_systems:

        if system == MemorySystem.BASE:

            search_tasks.append(self._search_base(query, limit))

        elif system == MemorySystem.MULTI_VECTOR:

            search_tasks.append(self._search_multi_vector(query, limit))

        elif system == MemorySystem.GRAPH:

            search_tasks.append(self._search_graph(query, limit))

        elif system == MemorySystem.HIERARCHICAL:

            memory_types = self._determine_memory_types(query)

            search_tasks.append(self._search_hierarchical(query, memory_types, limit))

    

    # Run with timeout

    results = []

    try:

        # Return as soon as first result is available

        for task in asyncio.as_completed(search_tasks, timeout=timeout):

            result_set = await task

            if result_set:

                results.extend(result_set)

                # If we have enough results, we can stop waiting

                if len(results) >= limit:

                    break

    except asyncio.TimeoutError:

        # If timeout occurs, use whatever results we have

        pass

    

    # Deduplicate and rank

    unique_results = self._deduplicate_results(results)

    ranked_results = self._rank_results(unique_results, query)

    

    return ranked_results[:limit]

````


### 4. Adaptive Reflection Scheduling


````python path=python\helpers\reflection.py mode=EDIT

async def should_reflect(self):

    """Determine if reflection is needed based on queue and timing"""

    # Always reflect if queue is large

    if len(self.reflection_queue) >= 20:

        return True

        

    # Reflect if enough time has passed and queue isn't empty

    current_time = time.time()

    if (current_time - self.last_reflection > self.reflection_interval) and self.reflection_queue:

        return True

        

    # Check for contradictions that need resolution

    if any(item.get("type") == "contradiction" for item in self.reflection_queue):

        return True

        

    return False

````


### 5. Memory Usage Monitoring and Auto-Scaling


````python path=python\helpers\memory_orchestrator.py mode=EDIT

def adjust_for_resource_constraints(self):

    """Adjust memory systems based on resource usage"""

    # Get current memory usage

    memory_usage = self._get_memory_usage()

    cpu_usage = self._get_cpu_usage()

    

    # If resources are constrained, reduce active systems

    if memory_usage > 80 or cpu_usage > 80:

        # Downgrade to simpler configuration

        if self.task_complexity == TaskComplexity.COMPLEX:

            self.task_complexity = TaskComplexity.MODERATE

        elif self.task_complexity == TaskComplexity.MODERATE:

            self.task_complexity = TaskComplexity.SIMPLE

            

        # Update active systems

        self.active_systems = self.get_recommended_systems(self.task_complexity)

        return True

        

    return False

    

def _get_memory_usage(self):

    """Get current memory usage percentage"""

    try:

        import psutil

        return psutil.virtual_memory().percent

    except:

        return 50  # Default assumption if psutil not available

        

def _get_cpu_usage(self):

    """Get current CPU usage percentage"""

    try:

        import psutil

        return psutil.cpu_percent(interval=0.1)

    except:

        return 50  # Default assumption if psutil not available

````


## Benefits of Adaptive Memory Architecture


1. **Resource Efficiency**: Only activates memory systems needed for the current task

2. **Reduced Latency**: Simpler tasks use lighter memory systems for faster responses

3. **Graceful Degradation**: Automatically scales down under resource constraints

4. **Optimized Retrieval**: Routes queries to the most appropriate memory systems

5. **Balanced Performance**: Maintains high-quality responses while minimizing resource usage


## Implementation Strategy


1. **Start with the Orchestrator**: Implement the memory orchestrator first to manage existing systems

2. **Add Task Analysis**: Integrate task complexity analysis to guide system selection

3. **Optimize Retrieval Logic**: Implement parallel retrieval with early termination

4. **Add Resource Monitoring**: Integrate resource usage monitoring and auto-scaling


## Implementation Strategy (continued)


5. **Implement Metrics Collection**: Add performance tracking to identify bottlenecks

6. **Create Feedback Loop**: Use performance data to continuously optimize system selection

7. **Add Graceful Fallbacks**: Ensure system can operate with minimal resources when needed


## Evaluation Framework


To ensure the adaptive memory system is working efficiently, implement these evaluation metrics:


````python path=python\helpers\memory_metrics.py mode=EDIT

import time

from typing import Dict, List, Any

import json

import os

from datetime import datetime


class MemoryMetrics:

    def __init__(self, agent):

        self.agent = agent

        self.metrics = {

            "queries": [],

            "system_usage": {},

            "latency": {},

            "relevance_scores": [],

            "resource_usage": []

        }

        self.metrics_dir = os.path.join(agent.memory.memory_subdir, "metrics")

        os.makedirs(self.metrics_dir, exist_ok=True)

        

    def record_query(self, query: str, complexity: str, systems_used: List[str], 

                    latency: float, result_count: int):

        """Record metrics for a memory query"""

        self.metrics["queries"].append({

            "timestamp": time.time(),

            "query": query,

            "complexity": complexity,

            "systems_used": systems_used,

            "latency": latency,

            "result_count": result_count

        })

        

        # Update system usage stats

        for system in systems_used:

            if system not in self.metrics["system_usage"]:

                self.metrics["system_usage"][system] = 0

            self.metrics["system_usage"][system] += 1

            

        # Update latency stats

        if complexity not in self.metrics["latency"]:

            self.metrics["latency"][complexity] = []

        self.metrics["latency"][complexity].append(latency)

        

    def record_relevance_feedback(self, query_id: int, relevance_score: float):

        """Record relevance feedback for query results"""

        if query_id < len(self.metrics["queries"]):

            self.metrics["relevance_scores"].append({

                "query_id": query_id,

                "relevance_score": relevance_score,

                "timestamp": time.time()

            })

            

    def record_resource_usage(self, memory_percent: float, cpu_percent: float):

        """Record system resource usage"""

        self.metrics["resource_usage"].append({

            "timestamp": time.time(),

            "memory_percent": memory_percent,

            "cpu_percent": cpu_percent

        })

        

    def get_system_efficiency(self) -> Dict[str, Any]:

        """Calculate efficiency metrics for memory systems"""

        if not self.metrics["queries"]:

            return {"status": "No data available"}

            

        # Calculate average latency by complexity

        avg_latency = {}

        for complexity, latencies in self.metrics["latency"].items():

            if latencies:

                avg_latency[complexity] = sum(latencies) / len(latencies)

                

        # Calculate system usage distribution

        total_queries = len(self.metrics["queries"])

        system_distribution = {}

        for system, count in self.metrics["system_usage"].items():

            system_distribution[system] = count / total_queries

            

        # Calculate average relevance score if available

        avg_relevance = None

        if self.metrics["relevance_scores"]:

            scores = [item["relevance_score"] for item in self.metrics["relevance_scores"]]

            avg_relevance = sum(scores) / len(scores)

            

        return {

            "avg_latency_by_complexity": avg_latency,

            "system_usage_distribution": system_distribution,

            "avg_relevance_score": avg_relevance,

            "total_queries": total_queries

        }

        

    def get_optimization_recommendations(self) -> List[str]:

        """Generate recommendations for memory system optimization"""

        recommendations = []

        efficiency = self.get_system_efficiency()

        

        # Check if we have enough data

        if efficiency.get("status") == "No data available":

            return ["Insufficient data for recommendations"]

            

        # Analyze latency by complexity

        latency_by_complexity = efficiency.get("avg_latency_by_complexity", {})

        for complexity, latency in latency_by_complexity.items():

            if complexity == "simple" and latency > 0.2:

                recommendations.append(f"Simple queries are taking too long ({latency:.2f}s). Consider optimizing base memory retrieval.")

            elif complexity == "moderate" and latency > 0.5:

                recommendations.append(f"Moderate queries are taking too long ({latency:.2f}s). Consider optimizing multi-vector retrieval.")

            elif complexity == "complex" and latency > 1.0:

                recommendations.append(f"Complex queries are taking too long ({latency:.2f}s). Consider parallel retrieval optimizations.")

                

        # Analyze system usage distribution

        system_distribution = efficiency.get("system_usage_distribution", {})

        if system_distribution.get("graph", 0) > 0.5:

            recommendations.append("Graph memory is being used frequently. Consider optimizing graph construction and query algorithms.")

            

        if system_distribution.get("hierarchical", 0) > 0.7:

            recommendations.append("Hierarchical memory is being used very frequently. Consider caching common queries.")

            

        # Analyze relevance

        avg_relevance = efficiency.get("avg_relevance_score")

        if avg_relevance is not None and avg_relevance < 0.7:

            recommendations.append(f"Average relevance score is low ({avg_relevance:.2f}). Consider improving embedding quality or retrieval logic.")

            

        return recommendations

        

    def save_metrics(self):

        """Save metrics to disk"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"memory_metrics_{timestamp}.json"

        filepath = os.path.join(self.metrics_dir, filename)

        

        with open(filepath, 'w') as f:

            json.dump(self.metrics, f, indent=2)

            

        return filepath

````


## Adaptive Memory Tool for User Control


````python path=python\tools\memory_configure.py mode=EDIT

from python.helpers.tool import Tool, Response

from python.helpers.memory_orchestrator import MemorySystem, TaskComplexity


class MemoryConfigure(Tool):

    async def execute(self, mode="auto", systems=None, **kwargs):

        """

        Configure memory systems manually or get current configuration

        

        Args:

            mode: "auto" for automatic selection, "manual" to specify systems

            systems: List of systems to activate when in manual mode

                     ["base", "multi_vector", "graph", "hierarchical", "reflection"]

        """

        if not hasattr(self.agent, "memory_orchestrator"):

            return Response(

                message="Memory orchestrator not initialized", 

                break_loop=False

            )

            

        orchestrator = self.agent.memory_orchestrator

        

        if mode == "auto":

            # Reset to automatic mode

            complexity = orchestrator.task_complexity

            orchestrator.active_systems = orchestrator.get_recommended_systems(complexity)

            message = f"Memory systems set to AUTO mode based on task complexity: {complexity.value}"

            

        elif mode == "manual" and systems:

            # Set specific systems

            active_systems = set()

            for system_name in systems:

                try:

                    system = MemorySystem(system_name)

                    active_systems.add(system)

                except ValueError:

                    pass

                    

            # Base system is always required

            active_systems.add(MemorySystem.BASE)

            

            # Update active systems

            orchestrator.active_systems = active_systems

            message = f"Memory systems manually set to: {', '.join([s.value for s in active_systems])}"

            

        else:

            # Just report current configuration

            active_systems = [s.value for s in orchestrator.active_systems]

            complexity = orchestrator.task_complexity.value

            metrics = orchestrator.get_performance_metrics()

            

            message = f"Current memory configuration:\n" \

                     f"- Mode: {'AUTO' if mode == 'auto' else 'MANUAL'}\n" \

                     f"- Task complexity: {complexity}\n" \

                     f"- Active systems: {', '.join(active_systems)}\n" \

                     f"- System stats: {metrics['system_stats']}"

            

        return Response(message=message, break_loop=False)

````


## Practical Optimization Techniques


### 1. Progressive Loading


````python path=python\helpers\memory_orchestrator.py mode=EDIT

async def progressive_search(self, query: str, limit: int = 5):

    """Progressive search that starts with simpler systems and escalates if needed"""

    # Start with base memory (fastest)

    results = await self._search_base(query, limit)

    

    # Check if results are sufficient

    if self._are_results_sufficient(results, query):

        return results[:limit]

    

    # If not, try multi-vector if active

    if MemorySystem.MULTI_VECTOR in self.active_systems:

        mv_results = await self._search_multi_vector(query, limit)

        results.extend(mv_results)

        

        # Deduplicate and check again

        unique_results = self._deduplicate_results(results)

        if self._are_results_sufficient(unique_results, query):

            return self._rank_results(unique_results, query)[:limit]

    

    # If still insufficient and complex task, try graph and hierarchical

    if self.task_complexity == TaskComplexity.COMPLEX:

        additional_tasks = []

        

        if MemorySystem.GRAPH in self.active_systems:

            additional_tasks.append(self._search_graph(query, limit))

            

        if MemorySystem.HIERARCHICAL in self.active_systems:

            memory_types = self._determine_memory_types(query)

            additional_tasks.append(self._search_hierarchical(query, memory_types, limit))

            

        if additional_tasks:

            additional_results = await asyncio.gather(*additional_tasks)

            for result_set in additional_results:

                results.extend(result_set)

    

    # Final deduplication and ranking

    unique_results = self._deduplicate_results(results)

    return self._rank_results(unique_results, query)[:limit]

    

def _are_results_sufficient(self, results, query):

    """Determine if results are sufficient to answer the query"""

    if not results:

        return False

        

    # Check result count

    if len(results) < 2:

        return False

        

    # Check relevance scores

    avg_score = sum(r.metadata.get("score", 0) for r in results) / len(results)

    if avg_score < 0.7:

        return False

        

    # Check if results contain query terms

    query_terms = set(query.lower().split())

    result_text = " ".join([r.page_content.lower() for r in results])

    matching_terms = sum(1 for term in query_terms if term in result_text)

    term_coverage = matching_terms / len(query_terms) if query_terms else 0

    

    return term_coverage > 0.6

````


### 2. Caching Frequent Queries


````python path=python\helpers\memory_orchestrator.py mode=EDIT

def __init__(self, agent):

    # ... existing initialization ...

    self.query_cache = {}

    self.cache_ttl = 300  # 5 minutes

    self.cache_size = 100  # Maximum cache entries


async def search(self, query: str, limit: int = 5, **kwargs):

    """Search with caching for frequent queries"""

    # Normalize query for caching

    cache_key = self._normalize_for_cache(query)

    

    # Check cache

    cached = self._get_from_cache(cache_key, limit)

    if cached:

        return cached

    

    # Perform actual search

    results = await self.progressive_search(query, limit)

    

    # Cache results

    self._add_to_cache(cache_key, results)

    

    return results


def _normalize_for_cache(self, query: str):

    """Normalize query for cache lookup"""

    # Simple normalization: lowercase, remove extra spaces

    return " ".join(query.lower().split())

    

def _get_from_cache(self, cache_key: str, limit: int):

    """Get results from cache if available and fresh"""

    if cache_key in self.query_cache:

        entry = self.query_cache[cache_key]

        if time.time() - entry["timestamp"] < self.cache_ttl:

            # Update access time

            entry["last_accessed"] = time.time()

            entry["access_count"] += 1

            return entry["results"][:limit]

    return None

    

def _add_to_cache(self, cache_key: str, results):

    """Add results to cache"""

    # Check if cache is full

    if len(self.query_cache) >= self.cache_size:

        # Remove least recently used entry

        lru_key = min(self.query_cache.keys(), 

                     key=lambda k: self.query_cache[k]["last_accessed"])

        del self.query_cache[lru_key]

    

    # Add to cache

    self.query_cache[cache_key] = {

        "results": results,

        "timestamp": time.time(),

        "last_accessed": time.time(),

        "access_count": 1

    }

````


### 3. Lazy Initialization


````python path=python\helpers\memory_orchestrator.py mode=EDIT

async def _ensure_system_initialized(self, system: MemorySystem):

    """Lazily initialize a memory system only when needed"""

    if system == MemorySystem.BASE:

        if not hasattr(self.agent, "memory"):

            self.agent.memory = await Memory.get(self.agent)

        return self.agent.memory

        

    elif system == MemorySystem.MULTI_VECTOR:

        if not hasattr(self.agent, "multi_vector_memory"):

            # Initialize only when first needed

            self.agent.multi_vector_memory = MultiVectorMemory(

                self.agent, 

                self.agent.memory.db, 

                self.agent.memory.memory_subdir

            )

        return self.agent.multi_vector_memory

        

    elif system == MemorySystem.GRAPH:

        if not hasattr(self.agent, "graph_memory"):

            self.agent.graph_memory = GraphMemory(

                self.agent, 

                self.agent.memory.db, 

                self.agent.memory.memory_subdir

            )

        return self.agent.graph_memory

        

    elif system == MemorySystem.HIERARCHICAL:

        if not hasattr(self.agent, "hierarchical_memory"):

            self.agent.hierarchical_memory = HierarchicalMemory(self.agent)

        return self.agent.hierarchical_memory

        

    elif system == MemorySystem.REFLECTION:

        if not hasattr(self.agent, "reflection_system"):

            self.agent.reflection_system = ReflectionSystem(self.agent)

        return self.agent.reflection_system

        

    return None

````


## Conclusion: Balancing Capability and Efficiency


The optimized cognitive architecture for Agent Zero achieves an ideal balance between capability and efficiency through:


1. **Dynamic Resource Allocation**: Only activates memory systems needed for the current task

2. **Progressive Loading**: Starts with simpler systems and escalates only when necessary

3. **Intelligent Caching**: Remembers frequent queries to reduce computational overhead

4. **Lazy Initialization**: Loads memory systems only when they're actually needed

5. **Resource Monitoring**: Automatically scales down under system constraints

6. **Performance Metrics**: Continuously evaluates and optimizes memory system usage


This approach ensures Agent Zero uses the optimal amount of memory techniques for each task, maximizing performance while minimizing resource usage. The system is also flexible enough to adapt to different deployment environments, from resource-constrained edge devices to powerful cloud servers. 