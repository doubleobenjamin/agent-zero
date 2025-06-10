# Agno LLM Framework - Complete Documentation

**Source:** https://docs.agno.com/llms-full.txt  
**Category:** Agno Agent Orchestration  
**Crawled:** 2025-06-09T19:20:51.635504  

---

# Agent API
Source: https://docs.agno.com/agent-api/introduction

A robust, production-ready application for serving Agents as an API.

Welcome to the Simple Agent API: a robust, production-ready application for serving Agents as an API. It includes:

* A FastAPI server for handling API requests.
* A PostgreSQL database for storing Agent sessions, knowledge, and memories.
* A set of pre-built Agents to use as a starting point.

<Snippet file="simple-agent-api-setup.mdx" />

<Snippet file="create-simple-agent-api-codebase.mdx" />

<Snippet file="simple-agent-api-dependency-management.mdx" />

<Snippet file="simple-agent-api-production.mdx" />

## Additional Information

Congratulations on running your Agent API.

* Read how to [use workspaces with your Agent API](/workspaces/introduction)

# A beautiful UI for your Agents
Source: https://docs.agno.com/agent-ui/introduction

A beautiful, open-source interface for interacting with AI agents

<Frame>
 <img height="200" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/images/agent-ui.png" style={{ borderRadius: '8px' }} />
</Frame>

Agno provides a beautiful UI for interacting with your agents, completely open source, free to use and build on top of. It's a simple interface that allows you to chat with your agents, view their memory, knowledge, and more.

<Note>
 No data is sent to [agno.com](https://app.agno.com), all agent data is stored locally in your sqlite database.
</Note>

The Open Source Agent UI is built with Next.js and TypeScript. After the success of the [Agent Playground](/introduction/playground), the community asked for a self-hosted alternative and we delivered!

# Get Started with Agent UI

To clone the Agent UI, run the following command in your terminal:

```bash
npx create-agent-ui@latest
```

Enter `y` to create a new project, install dependencies, then run the agent-ui using:

```bash
cd agent-ui && npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the Agent UI, but remember to connect to your local agents.

<Frame>
 <img height="200" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/images/agent-ui-homepage.png" style={{ borderRadius: '8px' }} />
</Frame>

<br />

<Accordion title="Clone the repository manually" icon="github">
 You can also clone the repository manually

 ```bash
 git clone https://github.com/agno-agi/agent-ui.git
 ```

 And run the agent-ui using

 ```bash
 cd agent-ui && pnpm install && pnpm dev
 ```
</Accordion>

## Connect to Local Agents

The Agent UI needs to connect to a playground server, which you can run locally or on any cloud provider.

Let's start with a local playground server. Create a file `playground.py`

```python playground.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

agent_storage: str = "tmp/agents.db"

web_agent = Agent(
 name="Web Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 instructions=["Always include sources"],
 # Store the agent sessions in a sqlite database
 storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
 # Adds the current date and time to the instructions
 add_datetime_to_instructions=True,
 # Adds the history of the conversation to the messages
 add_history_to_messages=True,
 # Number of history responses to add to the messages
 num_history_responses=5,
 # Adds markdown formatting to the messages
 markdown=True,
)

finance_agent = Agent(
 name="Finance Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
 instructions=["Always use tables to display data"],
 storage=SqliteStorage(table_name="finance_agent", db_file=agent_storage),
 add_datetime_to_instructions=True,
 add_history_to_messages=True,
 num_history_responses=5,
 markdown=True,
)

app = Playground(agents=[web_agent, finance_agent]).get_app()

if __name__ == "__main__":
 serve_playground_app("playground:app", reload=True)
```

In another terminal, run the playground server:

<Steps>
 <Step title="Setup your virtual environment">
 <CodeGroup>
 ```bash Mac
 python3 -m venv .venv
 source .venv/bin/activate
 ```

 ```bash Windows
 python3 -m venv aienv
 aienv/scripts/activate
 ```
 </CodeGroup>
 </Step>

 <Step title="Install dependencies">
 <CodeGroup>
 ```bash Mac
 pip install -U openai duckduckgo-search yfinance sqlalchemy 'fastapi[standard]' agno
 ```

 ```bash Windows
 pip install -U openai duckduckgo-search yfinance sqlalchemy 'fastapi[standard]' agno
 ```
 </CodeGroup>
 </Step>

 <Step title="Export your OpenAI key">
 <CodeGroup>
 ```bash Mac
 export OPENAI_API_KEY=sk-***
 ```

 ```bash Windows
 setx OPENAI_API_KEY sk-***
 ```
 </CodeGroup>
 </Step>

 <Step title="Run the Playground">
 ```shell
 python playground.py
 ```
 </Step>
</Steps>

<Tip>Make sure the `serve_playground_app()` points to the file containing your `Playground` app.</Tip>

## View the playground

* Open [http://localhost:3000](http://localhost:3000) to view the Agent UI
* Select the `localhost:7777` endpoint and start chatting with your agents!

<video autoPlay muted controls className="w-full aspect-video" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/videos/agent-ui-demo.mp4" />

# Agent Context
Source: https://docs.agno.com/agents/context

Agent Context is another amazing feature of Agno. `context` is a dictionary that contains a set of functions (or dependencies) that are resolved before the agent runs.

<Note>
 Context is a way to inject dependencies into the description and instructions of the agent.

 You can use context to inject memories, dynamic few-shot examples, "retrieved" documents, etc.
</Note>

```python agent_context.py
import json
from textwrap import dedent

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_top_hackernews_stories(num_stories: int = 5) -> str:
 """Fetch and return the top stories from HackerNews.

 Args:
 num_stories: Number of top stories to retrieve (default: 5)
 Returns:
 JSON string containing story details (title, url, score, etc.)
 """
 # Get top stories
 stories = [
 {
 k: v
 for k, v in httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
 )
 .json()
 .items()
 if k != "kids" # Exclude discussion threads
 }
 for id in httpx.get(
 "https://hacker-news.firebaseio.com/v0/topstories.json"
 ).json()[:num_stories]
 ]
 return json.dumps(stories, indent=4)

# Create a Context-Aware Agent that can access real-time HackerNews data
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 # Each function in the context is evaluated when the agent is run,
 # think of it as dependency injection for Agents
 context={"top_hackernews_stories": get_top_hackernews_stories},
 # Alternatively, you can manually add the context to the instructions
 instructions=dedent("""\
 You are an insightful tech trend observer! 📰

 Here are the top stories on HackerNews:
 {top_hackernews_stories}\
 """),
 # add_state_in_messages will make the `top_hackernews_stories` variable
 # available in the instructions
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response(
 "Summarize the top stories on HackerNews and identify any interesting trends.",
 stream=True,
)
```

## Adding the entire context to the user message

Set `add_context=True` to add the entire context to the user message. This way you don't have to manually add the context to the instructions.

```python agent_context_instructions.py
import json
from textwrap import dedent

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_top_hackernews_stories(num_stories: int = 5) -> str:
 """Fetch and return the top stories from HackerNews.

 Args:
 num_stories: Number of top stories to retrieve (default: 5)
 Returns:
 JSON string containing story details (title, url, score, etc.)
 """
 # Get top stories
 stories = [
 {
 k: v
 for k, v in httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
 )
 .json()
 .items()
 if k != "kids" # Exclude discussion threads
 }
 for id in httpx.get(
 "https://hacker-news.firebaseio.com/v0/topstories.json"
 ).json()[:num_stories]
 ]
 return json.dumps(stories, indent=4)

# Create a Context-Aware Agent that can access real-time HackerNews data
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 # Each function in the context is resolved when the agent is run,
 # think of it as dependency injection for Agents
 context={"top_hackernews_stories": get_top_hackernews_stories},
 # We can add the entire context dictionary to the instructions
 add_context=True,
 markdown=True,
)

# Example usage
agent.print_response(
 "Summarize the top stories on HackerNews and identify any interesting trends.",
 stream=True,
)
```

# What are Agents?
Source: https://docs.agno.com/agents/introduction

Learn about Agno Agents and how they work.

**Agents** are AI programs that operate autonomously. Traditional software follows a pre-programmed sequence of steps. Agents dynamically determine their course of action using a machine learning **model**.

The core of an Agent is the **model**, **tools** and **instructions**:

* **Model:** controls the flow of execution. It decides whether to reason, act or respond.
* **Tools:** enable an Agent to take actions and interact with external systems.
* **Instructions:** are how we program the Agent, teaching it how to use tools and respond.

Agents also have **memory**, **knowledge**, **storage** and the ability to **reason**:

* **Reasoning:** enables Agents to "think" before responding and "analyze" the results of their actions (i.e. tool calls), this improves reliability and quality of responses.
* **Knowledge:** is domain-specific information that the Agent can **search at runtime** to make better decisions and provide accurate responses (RAG). Knowledge is stored in a vector database and this **search at runtime** pattern is known as Agentic RAG/Agentic Search.
* **Storage:** is used by Agents to save session history and state in a database. Model APIs are stateless and storage enables us to continue conversations from where they left off. This makes Agents stateful, enabling multi-turn, long-term conversations.
* **Memory:** gives Agents the ability to store and recall information from previous interactions, allowing them to learn user preferences and personalize their responses.

<img height="200" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/images/agent.png" style={{ borderRadius: "8px" }} />

<Check>
 If this is your first time building agents, [follow these examples](/introduction/agents#basic-agent) before diving into advanced concepts.
</Check>

## Example: Research Agent

Let's build a research agent using Exa to showcase how to guide the Agent to produce the report in a specific format. In advanced cases, we should use [Structured Outputs](/agents/structured-output) instead.

<Note>
 The description and instructions are converted to the system message and the
 input is passed as the user message. Set `debug_mode=True` to view logs behind
 the scenes.
</Note>

<Steps>
 <Step title="Create Research Agent">
 Create a file `research_agent.py`

 ```python research_agent.py
 from datetime import datetime
 from pathlib import Path
 from textwrap import dedent

 from agno.agent import Agent
 from agno.models.openai import OpenAIChat
 from agno.tools.exa import ExaTools

 today = datetime.now().strftime("%Y-%m-%d")

 agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[ExaTools(start_published_date=today, type="keyword")],
 description=dedent("""\
 You are Professor X-1000, a distinguished AI research scientist with expertise
 in analyzing and synthesizing complex information. Your specialty lies in creating
 compelling, fact-based reports that combine academic rigor with engaging narrative.

 Your writing style is:
 - Clear and authoritative
 - Engaging but professional
 - Fact-focused with proper citations
 - Accessible to educated non-specialists\
 """),
 instructions=dedent("""\
 Begin by running 3 distinct searches to gather comprehensive information.
 Analyze and cross-reference sources for accuracy and relevance.
 Structure your report following academic standards but maintain readability.
 Include only verifiable facts with proper citations.
 Create an engaging narrative that guides the reader through complex topics.
 End with actionable takeaways and future implications.\
 """),
 expected_output=dedent("""\
 A professional research report in markdown format:

 # {Compelling Title That Captures the Topic's Essence}

 ## Executive Summary
 {Brief overview of key findings and significance}

 ## Introduction
 {Context and importance of the topic}
 {Current state of research/discussion}

 ## Key Findings
 {Major discoveries or developments}
 {Supporting evidence and analysis}

 ## Implications
 {Impact on field/society}
 {Future directions}

 ## Key Takeaways
 - {Bullet point 1}
 - {Bullet point 2}
 - {Bullet point 3}

 ## References
 - [Source 1](link) - Key finding/quote
 - [Source 2](link) - Key finding/quote
 - [Source 3](link) - Key finding/quote

 ---
 Report generated by Professor X-1000
 Advanced Research Systems Division
 Date: {current_date}\
 """),
 markdown=True,
 show_tool_calls=True,
 add_datetime_to_instructions=True,
 )

 # Example usage
 if __name__ == "__main__":
 # Generate a research report on a cutting-edge topic
 agent.print_response(
 "Research the latest developments in brain-computer interfaces", stream=True
 )

 # More example prompts to try:
 """
 Try these research topics:
 1. "Analyze the current state of solid-state batteries"
 2. "Research recent breakthroughs in CRISPR gene editing"
 3. "Investigate the development of autonomous vehicles"
 4. "Explore advances in quantum machine learning"
 5. "Study the impact of artificial intelligence on healthcare"
 """
 ```
 </Step>

 <Step title="Run the agent">
 Install libraries

 ```shell
 pip install openai exa-py agno
 ```

 Run the agent

 ```shell
 python research_agent.py
 ```
 </Step>
</Steps>

# Knowledge
Source: https://docs.agno.com/agents/knowledge

**Knowledge** is domain-specific information that the Agent can **search** at runtime to make better decisions (dynamic few-shot learning) and provide accurate responses (agentic RAG). Knowledge is stored in a vector db and this **searching on demand** pattern is called Agentic RAG.

<Accordion title="Dynamic Few-Shot Learning: Text2Sql Agent" icon="database">
 Example: If we're building a Text2Sql Agent, we'll need to give the table schemas, column names, data types, example queries, common "gotchas" to help it generate the best-possible SQL query.

 We're obviously not going to put this all in the system prompt, instead we store this information in a vector database and let the Agent query it at runtime.

 Using this information, the Agent can then generate the best-possible SQL query. This is called dynamic few-shot learning.
</Accordion>

**Agno Agents use Agentic RAG** by default, meaning when we provide `knowledge` to an Agent, it will search this knowledge base, at runtime, for the specific information it needs to achieve its task.

The pseudo steps for adding knowledge to an Agent are:

```python
from agno.agent import Agent, AgentKnowledge

# Create a knowledge base for the Agent
knowledge_base = AgentKnowledge(vector_db=...)

# Add information to the knowledge base
knowledge_base.load_text("The sky is blue")

# Add the knowledge base to the Agent and
# give it a tool to search the knowledge base as needed
agent = Agent(knowledge=knowledge_base, search_knowledge=True)
```

We can give our agent access to the knowledge base in the following ways:

* We can set `search_knowledge=True` to add a `search_knowledge_base()` tool to the Agent. `search_knowledge` is `True` **by default** if you add `knowledge` to an Agent.
* We can set `add_references=True` to automatically add references from the knowledge base to the Agent's prompt. This is the traditional 2023 RAG approach.

<Tip>
 If you need complete control over the knowledge base search, you can pass your own `retriever` function with the following signature:

 ```python
 def retriever(agent: Agent, query: str, num_documents: Optional[int], **kwargs) -> Optional[list[dict]]:
 ...
 ```

 This function is called during `search_knowledge_base()` and is used by the Agent to retrieve references from the knowledge base.
</Tip>

## Vector Databases

While any type of storage can act as a knowledge base, vector databases offer the best solution for retrieving relevant results from dense information quickly. Here's how vector databases are used with Agents:

<Steps>
 <Step title="Chunk the information">
 Break down the knowledge into smaller chunks to ensure our search query
 returns only relevant results.
 </Step>

 <Step title="Load the knowledge base">
 Convert the chunks into embedding vectors and store them in a vector
 database.
 </Step>

 <Step title="Search the knowledge base">
 When the user sends a message, we convert the input message into an
 embedding and "search" for nearest neighbors in the vector database.
 </Step>
</Steps>

<Note>
 Knowledge filters are currently supported on the following knowledge base types: <b>PDF</b>, <b>PDF\_URL</b>, <b>Text</b>, <b>JSON</b>, and <b>DOCX</b>.
 For more details, see the [Knowledge Filters documentation](/filters/introduction).
</Note>

## Example: RAG Agent with a PDF Knowledge Base

Let's build a **RAG Agent** that answers questions from a PDF.

### Step 1: Run PgVector

Let's use `PgVector` as our vector db as it can also provide storage for our Agents.

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **PgVector** on port **5532** using:

```bash
docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
```

### Step 2: Traditional RAG

Retrieval Augmented Generation (RAG) means **"stuffing the prompt with relevant information"** to improve the model's response. This is a 2 step process:

1. Retrieve relevant information from the knowledge base.
2. Augment the prompt to provide context to the model.

Let's build a **traditional RAG** Agent that answers questions from a PDF of recipes.

<Steps>
 <Step title="Install libraries">
 Install the required libraries using pip

 <CodeGroup>
 ```bash Mac
 pip install -U pgvector pypdf "psycopg[binary]" sqlalchemy
 ```

 ```bash Windows
 pip install -U pgvector pypdf "psycopg[binary]" sqlalchemy
 ```
 </CodeGroup>
 </Step>

 <Step title="Create a Traditional RAG Agent">
 Create a file `traditional_rag.py` with the following contents

 ```python traditional_rag.py
 from agno.agent import Agent
 from agno.models.openai import OpenAIChat
 from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
 from agno.vectordb.pgvector import PgVector, SearchType

 db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
 knowledge_base = PDFUrlKnowledgeBase(
 # Read PDF from this URL
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Store embeddings in the `ai.recipes` table
 vector_db=PgVector(table_name="recipes", db_url=db_url, search_type=SearchType.hybrid),
 )
 # Load the knowledge base: Comment after first run
 knowledge_base.load(upsert=True)

 agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Enable RAG by adding references from AgentKnowledge to the user prompt.
 add_references=True,
 # Set as False because Agents default to `search_knowledge=True`
 search_knowledge=False,
 markdown=True,
 # debug_mode=True,
 )
 agent.print_response("How do I make chicken and galangal in coconut milk soup")
 ```
 </Step>

 <Step title="Run the agent">
 Run the agent (it takes a few seconds to load the knowledge base).

 <CodeGroup>
 ```bash Mac
 python traditional_rag.py
 ```

 ```bash Windows
 python traditional_rag.py
 ```
 </CodeGroup>

 <br />
 </Step>
</Steps>

<Accordion title="How to use local PDFs" icon="file-pdf" iconType="duotone">
 If you want to use local PDFs, use a `PDFKnowledgeBase` instead

 ```python agent.py
 from agno.knowledge.pdf import PDFKnowledgeBase

 ...
 knowledge_base = PDFKnowledgeBase(
 path="data/pdfs",
 vector_db=PgVector(
 table_name="pdf_documents",
 db_url=db_url,
 ),
 )
 ...
 ```
</Accordion>

### Step 3: Agentic RAG

With traditional RAG above, `add_references=True` always adds information from the knowledge base to the prompt, regardless of whether it is relevant to the question or helpful.

With Agentic RAG, we let the Agent decide **if** it needs to access the knowledge base and what search parameters it needs to query the knowledge base.

Set `search_knowledge=True` and `read_chat_history=True`, giving the Agent tools to search its knowledge and chat history on demand.

<Steps>
 <Step title="Create an Agentic RAG Agent">
 Create a file `agentic_rag.py` with the following contents

 ```python agentic_rag.py
 from agno.agent import Agent
 from agno.models.openai import OpenAIChat
 from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
 from agno.vectordb.pgvector import PgVector, SearchType

 db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
 knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url, search_type=SearchType.hybrid),
 )
 # Load the knowledge base: Comment out after first run
 knowledge_base.load(upsert=True)

 agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Add a tool to search the knowledge base which enables agentic RAG.
 search_knowledge=True,
 # Add a tool to read chat history.
 read_chat_history=True,
 show_tool_calls=True,
 markdown=True,
 # debug_mode=True,
 )
 agent.print_response("How do I make chicken and galangal in coconut milk soup", stream=True)
 agent.print_response("What was my last question?", markdown=True)
 ```
 </Step>

 <Step title="Run the agent">
 Run the agent

 <CodeGroup>
 ```bash Mac
 python agentic_rag.py
 ```

 ```bash Windows
 python agentic_rag.py
 ```
 </CodeGroup>

 <Note>
 Notice how it searches the knowledge base and chat history when needed
 </Note>
 </Step>
</Steps>

## Attributes

| Parameter | Type | Default | Description |
| -------------------------- | ------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `knowledge` | `AgentKnowledge` | `None` | Provides the knowledge base used by the agent. |
| `search_knowledge` | `bool` | `True` | Adds a tool that allows the Model to search the knowledge base (aka Agentic RAG). Enabled by default when `knowledge` is provided. |
| `add_references` | `bool` | `False` | Enable RAG by adding references from AgentKnowledge to the user prompt. |
| `retriever` | `Callable[..., Optional[list[dict]]]` | `None` | Function to get context to add to the user message. This function is called when add\_references is True. |
| `context_format` | `Literal['json', 'yaml']` | `json` | Specifies the format for RAG, either "json" or "yaml". |
| `add_context_instructions` | `bool` | `False` | If True, add instructions for using the context to the system prompt (if knowledge is also provided). For example: add an instruction to prefer information from the knowledge base over its training data. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/tree/main/cookbook/agent_concepts/knowledge)

# Memory
Source: https://docs.agno.com/agents/memory

Memory gives an Agent the ability to recall relavant information. Memory is a part of the Agent's context that helps it provide the best, most personalized response.

<Check>
 If the user tells the Agent they like to ski, then future responses can reference this information to provide a more personalized experience.
</Check>

In Agno, Memory covers chat history, user preferences and any supplemental information about the task at hand. **Agno supports 3 types of memory out of the box:**

1. **Session Storage (chat history and session state):** Session storage saves an Agent's sessions in a database and enables Agents to have multi-turn conversations. Session storage also holds the session state, which is persisted across runs because it is saved to the database after each run. Session storage is a form of short-term memory **called "Storage" in Agno**.

2. **User Memories (user preferences):** The Agent can store insights and facts about the user that it learns through conversation. This helps the agents personalize its response to the user it is interacting with. Think of this as adding "ChatGPT like memory" to your agent. **This is called "Memory" in Agno**.

3. **Session Summaries (chat summary):** The Agent can store a condensed representations of the session, useful when chat histories gets too long. **This is called "Summary" in Agno**.

<Note>
 It is relatively easy to use your own memory implementation using `Agent.context`.
</Note>

To become an expert in Agentic Memory, you need ot learn about:

1. [Default, built-in Memory](/agents/memory#default-memory)
2. [Session Storage](/agents/memory#session-storage)
3. [User Memories](/agents/memory#user-memories)
4. [Session Summaries](/agents/memory#session-summaries)

## Show me the code: Memory & Storage in Action

Here's a simple but complete example of using Memory and Storage in an Agent.

```python memory_demo.py
from agno.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from rich.pretty import pprint

# UserId for the memories
user_id = "ava"
# Database file for memory and storage
db_file = "tmp/agent.db"

# Initialize memory.v2
memory = Memory(
 # Use any model for creating memories
 model=OpenAIChat(id="gpt-4.1"),
 db=SqliteMemoryDb(table_name="user_memories", db_file=db_file),
)
# Initialize storage
storage = SqliteStorage(table_name="agent_sessions", db_file=db_file)

# Initialize Agent
memory_agent = Agent(
 model=OpenAIChat(id="gpt-4.1"),
 # Store memories in a database
 memory=memory,
 # Give the Agent the ability to update memories
 enable_agentic_memory=True,
 # OR - Run the MemoryManager after each response
 enable_user_memories=True,
 # Store the chat history in the database
 storage=storage,
 # Add the chat history to the messages
 add_history_to_messages=True,
 # Number of history runs
 num_history_runs=3,
 markdown=True,
)

memory.clear()
memory_agent.print_response(
 "My name is Ava and I like to ski.",
 user_id=user_id,
 stream=True,
 stream_intermediate_steps=True,
)
print("Memories about Ava:")
pprint(memory.get_user_memories(user_id=user_id))

memory_agent.print_response(
 "I live in san francisco, where should i move within a 4 hour drive?",
 user_id=user_id,
 stream=True,
 stream_intermediate_steps=True,
)
print("Memories about Ava:")
pprint(memory.get_user_memories(user_id=user_id))
```

### Notes

* `enable_agentic_memory=True` gives the Agent a tool to manage memories of the user, this tool passes the task to the `MemoryManager` class. You may also set `enable_user_memories=True` which always runs the `MemoryManager` after each user message.
* `add_history_to_messages=True` adds the chat history to the messages sent to the Model, the `num_history_runs` determines how many runs to add.
* `read_chat_history=True` adds a tool to the Agent that allows it to read chat history, as it may be larger than what's included in the `num_history_runs`.

## Default Memory

Every Agent comes with built-in memory which keeps track of the messages in the session i.e. the chat history.

You can access these messages using `agent.get_messages_for_session()`.

We can give the Agent access to the chat history in the following ways:

* We can set `add_history_to_messages=True` and `num_history_runs=5` to add the messages from the last 5 runs automatically to every message sent to the agent.
* We can set `read_chat_history=True` to provide a `get_chat_history()` tool to your agent allowing it to read any message in the entire chat history.
* **We recommend setting all 3: `add_history_to_messages=True`, `num_history_runs=3` and `read_chat_history=True` for the best experience.**
* We can also set `read_tool_call_history=True` to provide a `get_tool_call_history()` tool to your agent allowing it to read tool calls in reverse chronological order.

<Note>
 The default memory is not persisted across execution cycles. So after the script finishes running, or the request is over, the built-in default memory is lost.

 You can persist this memory in a database by adding a `storage` driver to the Agent.
</Note>

<Steps>
 <Step title="Built-in memory example">
 ```python agent_memory.py
 from agno.agent import Agent
 from agno.models.google.gemini import Gemini
 from rich.pretty import pprint

 agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
 add_history_to_messages=True,
 # Number of historical responses to add to the messages.
 num_history_responses=3,
 description="You are a helpful assistant that always responds in a polite, upbeat and positive manner.",
 )

 # -*- Create a run
 agent.print_response("Share a 2 sentence horror story", stream=True)
 # -*- Print the messages in the memory
 pprint([m.model_dump(include={"role", "content"}) for m in agent.get_messages_for_session()])

 # -*- Ask a follow up question that continues the conversation
 agent.print_response("What was my first message?", stream=True)
 # -*- Print the messages in the memory
 pprint([m.model_dump(include={"role", "content"}) for m in agent.get_messages_for_session()])
 ```
 </Step>

 <Step title="Run the example">
 Install libraries

 ```shell
 pip install google-genai agno
 ```

 Export your key

 ```shell
 export GOOGLE_API_KEY=xxx
 ```

 Run the example

 ```shell
 python agent_memory.py
 ```
 </Step>
</Steps>

## Session Storage

The built-in memory is only available during the current execution cycle. Once the script ends, or the request is over, the built-in memory is lost.

**Storage** help us save Agent sessions and state to a database or file.

Adding storage to an Agent is as simple as providing a `storage` driver and Agno handles the rest. You can use Sqlite, Postgres, Mongo or any other database you want.

Here's a simple example that demostrates persistence across execution cycles:

```python storage.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from rich.pretty import pprint

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Fix the session id to continue the same session across execution cycles
 session_id="fixed_id_for_demo",
 storage=SqliteStorage(table_name="agent_sessions", db_file="tmp/data.db"),
 add_history_to_messages=True,
 num_history_runs=3,
)
agent.print_response("What was my last question?")
agent.print_response("What is the capital of France?")
agent.print_response("What was my last question?")
pprint(agent.get_messages_for_session())
```

The first time you run this, the answer to "What was my last question?" will not be available. But run it again and the Agent will able to answer properly. Because we have fixed the session id, the Agent will continue from the same session every time you run the script.

Read more in the [storage](/agents/storage) section.

## User Memories

Along with storing session history and state, Agents can also create user memories based on the conversation history.

To enable user memories, give your Agent a `Memory` object and set `enable_agentic_memory=True`.

<Note>
 Enabling agentic memory will also add all existing user memories to the agent's system prompt.
</Note>

<Steps>
 <Step title="User memory example">
 ```python user_memory.py
 from agno.agent import Agent
 from agno.memory.v2.db.sqlite import SqliteMemoryDb
 from agno.memory.v2.memory import Memory
 from agno.models.google.gemini import Gemini

 memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
 memory = Memory(db=memory_db)

 john_doe_id = "john_doe@example.com"

 agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory=memory,
 enable_agentic_memory=True,
 )

 # The agent can add new memories to the user's memory
 agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=john_doe_id,
 )

 agent.print_response("What are my hobbies?", stream=True, user_id=john_doe_id)

 # The agent can also remove all memories from the user's memory
 agent.print_response(
 "Remove all existing memories of me. Completely clear the DB.",
 stream=True,
 user_id=john_doe_id,
 )

 agent.print_response(
 "My name is John Doe and I like to paint.", stream=True, user_id=john_doe_id
 )

 # The agent can remove specific memories from the user's memory
 agent.print_response("Remove any memory of my name.", stream=True, user_id=john_doe_id)

 ```
 </Step>

 <Step title="Run the example">
 Install libraries

 ```shell
 pip install google-genai agno
 ```

 Export your key

 ```shell
 export GOOGLE_API_KEY=xxx
 ```

 Run the example

 ```shell
 python user_memory.py
 ```
 </Step>
</Steps>

User memories are stored in the `Memory` object and persisted in the `SqliteMemoryDb` to be used across multiple users and multiple sessions.

## Session Summaries

To enable session summaries, set `enable_session_summaries=True` on the `Agent`.

<Steps>
 <Step title="Session summary example">
 ```python session_summary.py
 from agno.agent import Agent
 from agno.memory.v2.db.sqlite import SqliteMemoryDb
 from agno.memory.v2.memory import Memory
 from agno.models.google.gemini import Gemini

 memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
 memory = Memory(db=memory_db)

 user_id = "jon_hamm@example.com"
 session_id = "1001"

 agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory=memory,
 enable_session_summaries=True,
 )

 agent.print_response(
 "What can you tell me about quantum computing?",
 stream=True,
 user_id=user_id,
 session_id=session_id,
 )

 agent.print_response(
 "I would also like to know about LLMs?",
 stream=True,
 user_id=user_id,
 session_id=session_id
 )

 session_summary = memory.get_session_summary(
 user_id=user_id, session_id=session_id
 )
 print(f"Session summary: {session_summary.summary}\n")
 ```
 </Step>

 <Step title="Run the example">
 Install libraries

 ```shell
 pip install google-genai agno
 ```

 Export your key

 ```shell
 export GOOGLE_API_KEY=xxx
 ```

 Run the example

 ```shell
 python session_summary.py
 ```
 </Step>
</Steps>

## Attributes

| Parameter | Type | Default | Description |
| -------------------------- | -------- | ---------- | --------------------------------------------------------------------------------------------------------------- |
| `memory` | `Memory` | `Memory()` | Agent's memory object used for storing and retrieving information. |
| `add_history_to_messages` | `bool` | `False` | If true, adds the chat history to the messages sent to the Model. Also known as `add_chat_history_to_messages`. |
| `num_history_runs` | `int` | `3` | Number of historical responses to add to the messages. |
| `enable_user_memories` | `bool` | `False` | If true, create and store personalized memories for the user. |
| `enable_session_summaries` | `bool` | `False` | If true, create and store session summaries. |
| `enable_agentic_memory` | `bool` | `False` | If true, enables the agent to manage the user's memory. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/tree/main/cookbook/agent_concepts/memory)
* View [Examples](/examples/concepts/memory)

# Metrics
Source: https://docs.agno.com/agents/metrics

Understanding agent run and session metrics in Agno

## Overview

When you run an agent in Agno, the response you get (**RunResponse**) includes detailed metrics about the run. These metrics help you understand resource usage (like **token usage** and **time**), performance, and other aspects of the model and tool calls.

Metrics are available at multiple levels:

* **Per-message**: Each message (assistant, tool, etc.) has its own metrics.
* **Per-tool call**: Each tool execution has its own metrics.
* **Aggregated**: The `RunResponse` aggregates metrics across all messages in the run.

<Note>
 Where Metrics Live

 * `RunResponse.metrics`: Aggregated metrics for the whole run, as a dictionary.
 * `ToolExecution.metrics`: Metrics for each tool call.
 * `Message.metrics`: Metrics for each message (assistant, tool, etc.).
</Note>

## Example Usage

Suppose you have an agent that performs some tasks and you want to analyze the metrics after running it. Here's how you can access and print the metrics:

You run the following code to create an agent and run it with the following configuration:

```python
from typing import Iterator

from agno.agent import Agent, RunResponse
from agno.models.google import Gemini
from agno.tools.yfinance import YFinanceTools
from rich.pretty import pprint

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-001"),
 tools=[YFinanceTools(stock_price=True)],
 markdown=True,
 show_tool_calls=True,
)

agent.print_response(
 "What is the stock price of NVDA", stream=True
)

# Print metrics per message
if agent.run_response.messages:
 for message in agent.run_response.messages:
 if message.role == "assistant":
 if message.content:
 print(f"Message: {message.content}")
 elif message.tool_calls:
 print(f"Tool calls: {message.tool_calls}")
 print("---" * 5, "Metrics", "---" * 5)
 pprint(message.metrics)
 print("---" * 20)

# Print the aggregated metrics for the whole run
print("---" * 5, "Collected Metrics", "---" * 5)
pprint(agent.run_response.metrics)
# Print the aggregated metrics for the whole session
print("---" * 5, "Session Metrics", "---" * 5)
pprint(agent.session_metrics)
```

You'd see the outputs with following information:

### Tool Execution Metrics

This section provides metrics for each tool execution. It includes details about the resource usage and performance of individual tool calls.

![Tool Run Message Metrics](https://mintlify.s3.us-west-1.amazonaws.com/agno/images/tools-run-message-metrics.png)

### Message Metrics

Here, you can see the metrics for each message response from the agent. All "assistant" responses will have metrics like this, helping you understand the performance and resource usage at the message level.

![Agent Run Message Metrics](https://mintlify.s3.us-west-1.amazonaws.com/agno/images/agent-run-message-metrics.png)

### Aggregated Run Metrics

The aggregated metrics provide a comprehensive view of the entire run. This includes a summary of all messages and tool calls, giving you an overall picture of the agent's performance and resource usage.

![Aggregated Run Metrics](https://mintlify.s3.us-west-1.amazonaws.com/agno/images/agent-run-aggregated-metrics.png)

Similarly for the session metrics, you can see the aggregated metrics across all runs in the session, providing insights into the overall performance and resource usage of the agent across multiple runs.

## How Metrics Are Aggregated

* **Per-message**: Each message (assistant, tool, etc.) has its own metrics object.
* **Run-level**: RunResponse.metrics is a dictionary where each key (e.g., input\_tokens) maps to a list of values from all assistant messages in the run.
* **Session-level**: `SessionMetrics` (see `agent.session_metrics`) aggregates metrics across all runs in the session.

## `MessageMetrics` Params

<Snippet file="message_metrics_params.mdx" />

# Multimodal Agents
Source: https://docs.agno.com/agents/multimodal

Agno agents support text, image, audio and video inputs and can generate text, image, audio and video outputs. For a complete overview, please checkout the [compatibility matrix](/models/compatibility).

## Multimodal inputs to an agent

Let's create an agent that can understand images and make tool calls as needed

### Image Agent

```python image_agent.py
from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

agent.print_response(
 "Tell me about this image and give me the latest news about it.",
 images=[
 Image(
 url="https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg"
 )
 ],
 stream=True,
)
```

Run the agent:

```shell
python image_agent.py
```

Similar to images, you can also use audio and video as an input.

### Audio Agent

```python audio_agent.py
import base64

import requests
from agno.agent import Agent, RunResponse # noqa
from agno.media import Audio
from agno.models.openai import OpenAIChat

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content

agent = Agent(
 model=OpenAIChat(id="gpt-4o-audio-preview", modalities=["text"]),
 markdown=True,
)
agent.print_response(
 "What is in this audio?", audio=[Audio(content=wav_data, format="wav")]
)
```

### Video Agent

<Note>Currently Agno only supports video as an input for Gemini models.</Note>

```python video_agent.py
from pathlib import Path

from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

# Please download "GreatRedSpot.mp4" using
# wget https://storage.googleapis.com/generativeai-downloads/images/GreatRedSpot.mp4
video_path = Path(__file__).parent.joinpath("GreatRedSpot.mp4")

agent.print_response("Tell me about this video", videos=[Video(filepath=video_path)])
```

## Multimodal outputs from an agent

Similar to providing multimodal inputs, you can also get multimodal outputs from an agent.

### Image Generation

The following example demonstrates how to generate an image using DALL-E with an agent.

```python image_agent.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.dalle import DalleTools

image_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DalleTools()],
 description="You are an AI agent that can generate images using DALL-E.",
 instructions="When the user asks you to create an image, use the `create_image` tool to create the image.",
 markdown=True,
 show_tool_calls=True,
)

image_agent.print_response("Generate an image of a white siamese cat")

images = image_agent.get_images()
if images and isinstance(images, list):
 for image_response in images:
 image_url = image_response.url
 print(image_url)
```

### Audio Response

The following example demonstrates how to obtain both text and audio responses from an agent. The agent will respond with text and audio bytes that can be saved to a file.

```python audio_agent.py
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "wav"},
 ),
 markdown=True,
)
response: RunResponse = agent.run("Tell me a 5 second scary story")

# Save the response audio to a file
if response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.content, filename="tmp/scary_story.wav"
 )
```

## Multimodal inputs and outputs together

You can create Agents that can take multimodal inputs and return multimodal outputs. The following example demonstrates how to provide a combination of audio and text inputs to an agent and obtain both text and audio outputs.

### Audio input and Audio output

```python audio_agent.py
import base64

import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content

agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "wav"},
 ),
 markdown=True,
)

agent.run("What's in these recording?", audio=[Audio(content=wav_data, format="wav")])

if agent.run_response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.content, filename="tmp/result.wav"
 )
```

# Prompts
Source: https://docs.agno.com/agents/prompts

We prompt Agents using `description` and `instructions` and a number of other settings. These settings are used to build the **system** message that is sent to the language model.

Understanding how these prompts are created will help you build better Agents.

The 2 key parameters are:

1. **Description**: A description that guides the overall behaviour of the agent.
2. **Instructions**: A list of precise, task-specific instructions on how to achieve its goal.

<Note>
 Description and instructions only provide a formatting benefit, we do not alter or abstract any information and you can always set the `system_message` to provide your own system prompt.
</Note>

## System message

The system message is created using `description`, `instructions` and a number of other settings. The `description` is added to the start of the system message and `instructions` are added as a list after `Instructions`. For example:

```python instructions.py
from agno.agent import Agent

agent = Agent(
 description="You are a famous short story writer asked to write for a magazine",
 instructions=["You are a pilot on a plane flying from Hawaii to Japan."],
 markdown=True,
 debug_mode=True,
)
agent.print_response("Tell me a 2 sentence horror story.", stream=True)
```

Will translate to (set `debug_mode=True` to view the logs):

```js
DEBUG ============== system ==============
DEBUG You are a famous short story writer asked to write for a magazine

 ## Instructions
 - You are a pilot on a plane flying from Hawaii to Japan.
 - Use markdown to format your answers.
DEBUG ============== user ==============
DEBUG Tell me a 2 sentence horror story.
DEBUG ============== assistant ==============
DEBUG As the autopilot disengaged inexplicably mid-flight over the Pacific, the pilot glanced at the copilot's seat
 only to find it empty despite his every recall of a full crew boarding. Hands trembling, he looked into the
 cockpit's rearview mirror and found his own reflection grinning back with blood-red eyes, whispering,
 "There's no escape, not at 30,000 feet."
DEBUG **************** METRICS START ****************
DEBUG * Time to first token: 0.4518s
DEBUG * Time to generate response: 1.2594s
DEBUG * Tokens per second: 63.5243 tokens/s
DEBUG * Input tokens: 59
DEBUG * Output tokens: 80
DEBUG * Total tokens: 139
DEBUG * Prompt tokens details: {'cached_tokens': 0}
DEBUG * Completion tokens details: {'reasoning_tokens': 0}
DEBUG **************** METRICS END ******************
```

## Set the system message directly

You can manually set the system message using the `system_message` parameter.

```python
from agno.agent import Agent

agent = Agent(system_message="Share a 2 sentence story about")
agent.print_response("Love in the year 12000.")
```

<Tip>
 Some models via some model providers, like `llama-3.2-11b-vision-preview` on Groq, require no system message with other messages. To remove the system message, set `create_default_system_message=False` and `system_message=None`. Additionally, if `markdown=True` is set, it will add a system message, so either remove it or explicitly disable the system message.
</Tip>

## User message

The input `message` sent to the `Agent.run()` or `Agent.print_response()` functions is used as the user message.

## Default system message

The Agent creates a default system message that can be customized using the following parameters:

| Parameter | Type | Default | Description |
| ------------------------------- | ----------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description` | `str` | `None` | A description of the Agent that is added to the start of the system message. |
| `goal` | `str` | `None` | Describe the task the agent should achieve. |
| `instructions` | `List[str]` | `None` | List of instructions added to the system prompt in `<instructions>` tags. Default instructions are also created depending on values for `markdown`, `output_model` etc. |
| `additional_context` | `str` | `None` | Additional context added to the end of the system message. |
| `expected_output` | `str` | `None` | Provide the expected output from the Agent. This is added to the end of the system message. |
| `markdown` | `bool` | `False` | Add an instruction to format the output using markdown. |
| `add_datetime_to_instructions` | `bool` | `False` | If True, add the current datetime to the prompt to give the agent a sense of time. This allows for relative times like "tomorrow" to be used in the prompt |
| `system_message` | `str` | `None` | System prompt: provide the system prompt as a string |
| `system_message_role` | `str` | `system` | Role for the system message. |
| `create_default_system_message` | `bool` | `True` | If True, build a default system prompt using agent settings and use that. |

<Tip>
 Disable the default system message by setting `create_default_system_message=False`.
</Tip>

## Default user message

The Agent creates a default user message, which is either the input message or a message with the `context` if `enable_rag=True`. The default user message can be customized using:

| Parameter | Type | Default | Description |
| ----------------------------- | ------------------------- | -------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `context` | `str` | `None` | Additional context added to the end of the user message. |
| `add_context` | `bool` | `False` | If True, add the context to the user prompt. |
| `resolve_context` | `bool` | `True` | If True, resolve the context (i.e. call any functions in the context) before adding it to the user prompt. |
| `add_references` | `bool` | `False` | Enable RAG by adding references from the knowledge base to the prompt. |
| `retriever` | `Callable` | `None` | Function to get references to add to the user\_message. This function, if provided, is called when `add_references` is True. |
| `references_format` | `Literal["json", "yaml"]` | `"json"` | Format of the references. |
| `add_history_to_messages` | `bool` | `False` | If true, adds the chat history to the messages sent to the Model. |
| `num_history_responses` | `int` | `3` | Number of historical responses to add to the messages. |
| `user_message` | `Union[List, Dict, str]` | `None` | Provide the user prompt as a string. Note: this will ignore the message sent to the run function. |
| `user_message_role` | `str` | `user` | Role for the user message. |
| `create_default_user_message` | `bool` | `True` | If True, build a default user prompt using references and chat history. |

<Tip>
 Disable the default user message by setting `create_default_user_message=False`.
</Tip>

# Agent.run()
Source: https://docs.agno.com/agents/run

Learn how to run an agent and get the response.

The `Agent.run()` function runs the agent and generates a response, either as a `RunResponse` object or a stream of `RunResponse` objects.

Many of our examples use `agent.print_response()` which is a helper utility to print the response in the terminal. It uses `agent.run()` under the hood.

Here's how to run your agent. The response is captured in the `response` and `response_stream` variables.

```python
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response

agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))

# Run agent and return the response as a variable
response: RunResponse = agent.run("Tell me a 5 second short story about a robot")
# Run agent and return the response as a stream
response_stream: Iterator[RunResponse] = agent.run("Tell me a 5 second short story about a lion", stream=True)

# Print the response in markdown format
pprint_run_response(response, markdown=True)
# Print the response stream in markdown format
pprint_run_response(response_stream, markdown=True)
```

<Note>Set `stream=True` to return a stream of `RunResponse` objects.</Note>

## RunResponse

The `Agent.run()` function returns either a `RunResponse` object or an `Iterator[RunResponse]` when `stream=True`. It has the following attributes:

<Note>
 Understanding Metrics

 For a detailed explanation of how metrics are collected and used, please refer to the [Metrics Documentation](/agents/metrics).
</Note>

### RunResponse Attributes

| Attribute | Type | Default | Description |
| ---------------- | ---------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `content` | `Any` | `None` | Content of the response. |
| `content_type` | `str` | `"str"` | Specifies the data type of the content. |
| `context` | `List[MessageContext]` | `None` | The context added to the response for RAG. |
| `event` | `str` | `RunEvent.run_response.value` | Event type of the response. |
| `event_data` | `Dict[str, Any]` | `None` | Data associated with the event. |
| `messages` | `List[Message]` | `None` | A list of messages included in the response. |
| `metrics` | `Dict[str, Any]` | `None` | Usage metrics of the run. |
| `model` | `str` | `None` | The model used in the run. |
| `run_id` | `str` | `None` | Run Id. |
| `agent_id` | `str` | `None` | Agent Id for the run. |
| `session_id` | `str` | `None` | Session Id for the run. |
| `tools` | `List[Dict[str, Any]]` | `None` | List of tools provided to the model. |
| `images` | `List[Image]` | `None` | List of images the model produced. |
| `videos` | `List[Video]` | `None` | List of videos the model produced. |
| `audio` | `List[Audio]` | `None` | List of audio snippets the model produced. |
| `response_audio` | `ModelResponseAudio` | `None` | The model's raw response in audio. |
| `created_at` | `int` | - | Unix timestamp of the response creation. |
| `extra_data` | `RunResponseExtraData` | `None` | Extra data containing optional fields like `references`, `add_messages`, `history`, `reasoning_steps`, and `reasoning_messages`. |

## Streaming Intermediate Steps

Throughout the execution of an agent, multiple events take place, and we provide these events in real-time for enhanced agent transparency.

You can enable streaming of intermediate steps by setting `stream_intermediate_steps=True`.

```python
# Stream with intermediate steps
response_stream = agent.run(
 "Tell me a 5 second short story about a lion",
 stream=True,
 stream_intermediate_steps=True
)
```

### Event Types

The following events are sent by the `Agent.run()` and `Agent.arun()` functions depending on agent's configuration:

| Event Type | Description |
| -------------------- | ---------------------------------------------------------------------------- |
| `RunStarted` | Indicates the start of a run |
| `RunResponse` | Contains the model's response text as individual chunks |
| `RunCompleted` | Signals successful completion of the run |
| `RunError` | Indicates an error occurred during the run |
| `RunCancelled` | Signals that the run was cancelled |
| `ToolCallStarted` | Indicates the start of a tool call |
| `ToolCallCompleted` | Signals completion of a tool call. This also contains the tool call results. |
| `ReasoningStarted` | Indicates the start of the agent's reasoning process |
| `ReasoningStep` | Contains a single step in the reasoning process |
| `ReasoningCompleted` | Signals completion of the reasoning process |
| `UpdatingMemory` | Indicates that the agent is updating its memory |
| `WorkflowStarted` | Indicates the start of a workflow |
| `WorkflowCompleted` | Signals completion of a workflow |

You can see this behavior in action in our [Playground](https://app.agno.com/playground/agents?endpoint=demo.agnoagents.com\&agent=reasoning-agent).

# Sessions
Source: https://docs.agno.com/agents/sessions

When we call `Agent.run()`, it creates a stateless, singular Agent run.

But what if we want to continue this run i.e. have a multi-turn conversation? That's where `sessions` come in. A session is collection of consecutive runs.

In practice, a session is a multi-turn conversation between a user and an Agent. Using a `session_id`, we can connect the conversation history and state across multiple runs.

Let's outline some key concepts:

* **Session:** A session is collection of consecutive runs like a multi-turn conversation between a user and an Agent. Sessions are identified by a `session_id` and each turn is a **run**.
* **Run:** Every interaction (i.e. chat or turn) with an Agent is called a **run**. Runs are identified by a `run_id` and `Agent.run()` creates a new `run_id` when called.
* **Messages:** are the individual messages sent between the model and the Agent. Messages are the communication protocol between the Agent and model.

Let's start with an example where a single run is created with an Agent. A `run_id` is automatically generated, as well as a `session_id` (because we didn't provide one to continue the conversation). This run is not yet associated with a user.

```python
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response

agent = Agent(model=OpenAIChat(id="gpt-4o-mini"))

# Run agent and return the response as a variable
agent.print_response("Tell me a 5 second short story about a robot")
```

## Multi-user, multi-session Agents

Each user that is interacting with an Agent gets a unique set of sessions and you can have multiple users interacting with the same Agent at the same time.

Set a `user_id` to connect a user to their sessions with the Agent.

In the example below, we set a `session_id` to demo how to have multi-turn conversations with multiple users at the same time. In production, the `session_id` is auto generated.

<Note>
 Note: Multi-user, multi-session currently only works with `Memory.v2`, which will become the default memory implementation in the next release.
</Note>

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.memory.v2 import Memory

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Multi-user, multi-session only work with Memory.v2
 memory=Memory(),
 add_history_to_messages=True,
 num_history_runs=3,
)

user_1_id = "user_101"
user_2_id = "user_102"

user_1_session_id = "session_101"
user_2_session_id = "session_102"

# Start the session with user 1
agent.print_response(
 "Tell me a 5 second short story about a robot.",
 user_id=user_1_id,
 session_id=user_1_session_id,
)
# Continue the session with user 1
agent.print_response("Now tell me a joke.", user_id=user_1_id, session_id=user_1_session_id)

# Start the session with user 2
agent.print_response("Tell me about quantum physics.", user_id=user_2_id, session_id=user_2_session_id)
# Continue the session with user 2
agent.print_response("What is the speed of light?", user_id=user_2_id, session_id=user_2_session_id)

# Ask the agent to give a summary of the conversation, this will use the history from the previous messages
agent.print_response(
 "Give me a summary of our conversation.",
 user_id=user_1_id,
 session_id=user_1_session_id,
)
```

## Fetch messages from last N sessions

In some scenarios, you might want to fetch messages from the last N sessions to provide context or continuity in conversations.

Here's an example of how you can achieve this:

```python
# Remove the tmp db file before running the script
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

os.remove("tmp/data.db")

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 user_id="user_1",
 storage=SqliteStorage(table_name="agent_sessions_new", db_file="tmp/data.db"),
 search_previous_sessions_history=True, # allow searching previous sessions
 num_history_sessions=2, # only include the last 2 sessions in the search to avoid context length issues
 show_tool_calls=True,
)

session_1_id = "session_1_id"
session_2_id = "session_2_id"
session_3_id = "session_3_id"
session_4_id = "session_4_id"
session_5_id = "session_5_id"

agent.print_response("What is the capital of South Africa?", session_id=session_1_id)
agent.print_response("What is the capital of China?", session_id=session_2_id)
agent.print_response("What is the capital of France?", session_id=session_3_id)
agent.print_response("What is the capital of Japan?", session_id=session_4_id)
agent.print_response(
 "What did I discuss in my previous conversations?", session_id=session_5_id
) # It should only include the last 2 sessions
```

<Note>
 To enable fetching messages from the last N sessions, you need to use the following flags:

 * `search_previous_sessions_history`: Set this to `True` to allow searching through previous sessions.
 * `num_history_sessions`: Specify the number of past sessions to include in the search. In this example, it is set to `2` to include only the last 2 sessions.
 It's advisable to keep this number to 2 or 3 for now, as a larger number might fill up the context length of the model, potentially leading to performance issues.

 These flags help manage the context length and ensure that only relevant session history is included in the conversation.
</Note>

# Agent State
Source: https://docs.agno.com/agents/state

**State** is any kind of data the Agent needs to maintain throughout runs.

<Check>
 A simple yet common use case for Agents is to manage lists, items and other "information" for a user. For example, a shopping list, a todo list, a wishlist, etc.

 This can be easily managed using the `session_state`. The Agent updates the `session_state` in tool calls and exposes them to the Model in the `description` and `instructions`.
</Check>

Agno's provides a powerful and elegant state management system, here's how it works:

* The `Agent` has a `session_state` parameter.
* We add our state variables to this `session_state` dictionary.
* We update the `session_state` dictionary in tool calls or other functions.
* We share the current `session_state` with the Model in the `description` and `instructions`.
* The `session_state` is stored with Agent sessions and is persisted in a database. Meaning, it is available across execution cycles.

Here's an example of an Agent managing a shopping list:

```python session_state.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Define a tool that increments our counter and returns the new value
def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list."""
 agent.session_state["shopping_list"].append(item)
 return f"The shopping list is now {agent.session_state['shopping_list']}"

# Create an Agent that maintains state
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Initialize the session state with a counter starting at 0
 session_state={"shopping_list": []},
 tools=[add_item],
 # You can use variables from the session state in the instructions
 instructions="Current state (shopping list) is: {shopping_list}",
 # Important: Add the state to the messages
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response("Add milk, eggs, and bread to the shopping list", stream=True)
print(f"Final session state: {agent.session_state}")
```

<Tip>
 This is as good and elegant as state management gets.
</Tip>

## Maintaining state across multiple runs

A big advantage of **sessions** is the ability to maintain state across multiple runs. For example, let's say the agent is helping a user keep track of their shopping list.

<Note>
 By setting `add_state_in_messages=True`, the keys of the `session_state` dictionary are available in the `description` and `instructions` as variables.

 Use this pattern to add the shopping\_list to the instructions directly.
</Note>

```python shopping_list.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Define tools to manage our shopping list
def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list and return confirmation."""
 # Add the item if it's not already in the list
 if item.lower() not in [i.lower() for i in agent.session_state["shopping_list"]]:
 agent.session_state["shopping_list"].append(item)
 return f"Added '{item}' to the shopping list"
 else:
 return f"'{item}' is already in the shopping list"

def remove_item(agent: Agent, item: str) -> str:
 """Remove an item from the shopping list by name."""
 # Case-insensitive 
 for i, list_item in enumerate(agent.session_state["shopping_list"]):
 if list_item.lower() == item.lower():
 agent.session_state["shopping_list"].pop(i)
 return f"Removed '{list_item}' from the shopping list"

 return f"'{item}' was not found in the shopping list"

def list_items(agent: Agent) -> str:
 """List all items in the shopping list."""
 shopping_list = agent.session_state["shopping_list"]

 if not shopping_list:
 return "The shopping list is empty."

 items_text = "\n".join([f"- {item}" for item in shopping_list])
 return f"Current shopping list:\n{items_text}"

# Create a Shopping List Manager Agent that maintains state
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Initialize the session state with an empty shopping list
 session_state={"shopping_list": []},
 tools=[add_item, remove_item, list_items],
 # You can use variables from the session state in the instructions
 instructions=dedent("""\
 Your job is to manage a shopping list.

 The shopping list starts empty. You can add items, remove items by name, and list all items.

 Current shopping list: {shopping_list}
 """),
 show_tool_calls=True,
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response("Add milk, eggs, and bread to the shopping list", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("I got bread", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("I need apples and oranges", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("whats on my list?", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("Clear everything from my list and start over with just bananas and yogurt", stream=True)
print(f"Session state: {agent.session_state}")
```

<Tip>
 We love how elegantly we can maintain and pass on state across multiple runs.
</Tip>

## Using state in instructions

You can use variables from the session state in the instructions by setting `add_state_in_messages=True`.

<Tip>
 Don't use the f-string syntax in the instructions. Directly use the `{key}` syntax, Agno substitutes the values for you.
</Tip>

```python state_in_instructions.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Initialize the session state with a variable
 session_state={"user_name": "John"},
 # You can use variables from the session state in the instructions
 instructions="Users name is {user_name}",
 show_tool_calls=True,
 add_state_in_messages=True,
 markdown=True,
)

agent.print_response("What is my name?", stream=True)
```

## Persisting state in database

`session_state` is part of the Agent session and is saved to the database after each run if a `storage` driver is provided.

Here's an example of an Agent that maintains a shopping list and persists the state in a database. Run this script multiple times to see the state being persisted.

```python session_state_storage.py
"""Run `pip install agno openai sqlalchemy` to install dependencies."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

# Define a tool that adds an item to the shopping list
def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list."""
 if item not in agent.session_state["shopping_list"]:
 agent.session_state["shopping_list"].append(item)
 return f"The shopping list is now {agent.session_state['shopping_list']}"

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Fix the session id to continue the same session across execution cycles
 session_id="fixed_id_for_demo",
 # Initialize the session state with an empty shopping list
 session_state={"shopping_list": []},
 # Add a tool that adds an item to the shopping list
 tools=[add_item],
 # Store the session state in a SQLite database
 storage=SqliteStorage(table_name="agent_sessions", db_file="tmp/data.db"),
 # Add the current shopping list from the state in the instructions
 instructions="Current shopping list is: {shopping_list}",
 # Important: Set `add_state_in_messages=True`
 # to make `{shopping_list}` available in the instructions
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response("What's on my shopping list?", stream=True)
print(f"Session state: {agent.session_state}")
agent.print_response("Add milk, eggs, and bread", stream=True)
print(f"Session state: {agent.session_state}")
```

# Session Storage
Source: https://docs.agno.com/agents/storage

Use **Session Storage** to persist Agent sessions and state to a database or file.

<Tip>
 **Why do we need Session Storage?**

 Agents are ephemeral and the built-in memory only lasts for the current execution cycle.

 In production environments, we serve (or trigger) Agents via an API and need to continue the same session across multiple requests. Storage persists the session history and state in a database and allows us to pick up where we left off.

 Storage also let's us inspect and evaluate Agent sessions, extract few-shot examples and build internal monitoring tools. It lets us **look at the data** which helps us build better Agents.
</Tip>

Adding storage to an Agent, Team or Workflow is as simple as providing a `Storage` driver and Agno handles the rest. You can use Sqlite, Postgres, Mongo or any other database you want.

Here's a simple example that demostrates persistence across execution cycles:

```python storage.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from rich.pretty import pprint

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Fix the session id to continue the same session across execution cycles
 session_id="fixed_id_for_demo",
 storage=SqliteStorage(table_name="agent_sessions", db_file="tmp/data.db"),
 add_history_to_messages=True,
 num_history_runs=3,
)
agent.print_response("What was my last question?")
agent.print_response("What is the capital of France?")
agent.print_response("What was my last question?")
pprint(agent.get_messages_for_session())
```

The first time you run this, the answer to "What was my last question?" will not be available. But run it again and the Agent will able to answer properly. Because we have fixed the session id, the Agent will continue from the same session every time you run the script.

## Benefits of Storage

Storage has typically been an under-discussed part of Agent Engineering -- but we see it as the unsung hero of production agentic applications.

In production, you need storage to:

* Continue sessions: retrieve sessions history and pick up where you left off.
* Get list of sessions: To continue a previous session, you need to maintain a list of sessions available for that agent.
* Save state between runs: save the Agent's state to a database or file so you can inspect it later.

But there is so much more:

* Storage saves our Agent's session data for inspection and evaluations.
* Storage helps us extract few-shot examples, which can be used to improve the Agent.
* Storage enables us to build internal monitoring tools and dashboards.

<Warning>
 Storage is such a critical part of your Agentic infrastructure that it should never be offloaded to a third party. You should almost always use your own storage layer for your Agents.
</Warning>

## Example: Use Postgres for storage

<Steps>
 <Step title="Run Postgres">
 Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **Postgres** on port **5532** using:

 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agno/pgvector:16
 ```
 </Step>

 <Step title="Create an Agent with Storage">
 Create a file `agent_with_storage.py` with the following contents

 ```python
 import typer
 from typing import Optional, List
 from agno.agent import Agent
 from agno.storage.postgres import PostgresStorage
 from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
 from agno.vectordb.pgvector import PgVector, SearchType

 db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
 knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url, search_type=SearchType.hybrid),
 )
 storage = PostgresStorage(table_name="pdf_agent", db_url=db_url)

 def pdf_agent(new: bool = False, user: str = "user"):
 session_id: Optional[str] = None

 if not new:
 existing_sessions: List[str] = storage.get_all_session_ids(user)
 if len(existing_sessions) > 0:
 session_id = existing_sessions[0]

 agent = Agent(
 session_id=session_id,
 user_id=user,
 knowledge=knowledge_base,
 storage=storage,
 # Show tool calls in the response
 show_tool_calls=True,
 # Enable the agent to read the chat history
 read_chat_history=True,
 # We can also automatically add the chat history to the messages sent to the model
 # But giving the model the chat history is not always useful, so we give it a tool instead
 # to only use when needed.
 # add_history_to_messages=True,
 # Number of historical responses to add to the messages.
 # num_history_responses=3,
 )
 if session_id is None:
 session_id = agent.session_id
 print(f"Started Session: {session_id}\n")
 else:
 print(f"Continuing Session: {session_id}\n")

 # Runs the agent as a cli app
 agent.cli_app(markdown=True)

 if __name__ == "__main__":
 # Load the knowledge base: Comment after first run
 knowledge_base.load(upsert=True)

 typer.run(pdf_agent)
 ```
 </Step>

 <Step title="Run the agent">
 Install libraries

 <CodeGroup>
 ```bash Mac
 pip install -U agno openai pgvector pypdf "psycopg[binary]" sqlalchemy
 ```

 ```bash Windows
 pip install -U agno openai pgvector pypdf "psycopg[binary]" sqlalchemy
 ```
 </CodeGroup>

 Run the agent

 ```bash
 python agent_with_storage.py
 ```

 Now the agent continues across sessions. Ask a question:

 ```
 How do I make pad thai?
 ```

 Then message `bye` to exit, start the app again and ask:

 ```
 What was my last message?
 ```
 </Step>

 <Step title="Start a new run">
 Run the `agent_with_storage.py` file with the `--new` flag to start a new run.

 ```bash
 python agent_with_storage.py --new
 ```
 </Step>
</Steps>

## Schema Upgrades

When using `AgentStorage`, the SQL-based storage classes have fixed schemas. As new Agno features are released, the schemas might need to be updated.

Upgrades can either be done manually or automatically.

### Automatic Upgrades

Automatic upgrades are done when the `auto_upgrade_schema` parameter is set to `True` in the storage class constructor.
You only need to set this once for an agent run and the schema would be upgraded.

```python
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
storage = PostgresStorage(table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True)
```

### Manual Upgrades

Manual schema upgrades can be done by calling the `upgrade_schema` method on the storage class.

```python
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
storage = PostgresStorage(table_name="agent_sessions", db_url=db_url)
storage.upgrade_schema()
```

## Params

| Parameter | Type | Default | Description |
| --------- | ------------------------ | ------- | -------------------------------- |
| `storage` | `Optional[AgentStorage]` | `None` | Storage mechanism for the agent. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/tree/main/cookbook/storage)

# Structured Output
Source: https://docs.agno.com/agents/structured-output

One of our favorite features is using Agents to generate structured data (i.e. a pydantic model). Use this feature to extract features, classify data, produce fake data etc. The best part is that they work with function calls, knowledge bases and all other features.

## Example

Let's create an Movie Agent to write a `MovieScript` for us.

```python movie_agent.py
from typing import List
from rich.pretty import pprint
from pydantic import BaseModel, Field
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat

class MovieScript(BaseModel):
 setting: str = Field(..., description="Provide a nice setting for a blockbuster movie.")
 ending: str = Field(..., description="Ending of the movie. If not available, provide a happy ending.")
 genre: str = Field(
 ..., description="Genre of the movie. If not available, select action, thriller or romantic comedy."
 )
 name: str = Field(..., description="Give a name to this movie")
 characters: List[str] = Field(..., description="Name of characters for this movie.")
 storyline: str = Field(..., description="3 sentence storyline for the movie. Make it exciting!")

# Agent that uses JSON mode
json_mode_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description="You write movie scripts.",
 response_model=MovieScript,
 use_json_mode=True,
)
json_mode_agent.print_response("New York")

# Agent that uses structured outputs
structured_output_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

structured_output_agent.print_response("New York")
```

Run the script to see the output.

```bash
pip install -U agno openai

python movie_agent.py
```

The output is an object of the `MovieScript` class, here's how it looks:

```python
# Using JSON mode
MovieScript(
│ setting='The bustling streets of New York City, filled with skyscrapers, secret alleyways, and hidden underground passages.',
│ ending='The protagonist manages to thwart an international conspiracy, clearing his name and winning the love of his life back.',
│ genre='Thriller',
│ name='Shadows in the City',
│ characters=['Alex Monroe', 'Eva Parker', 'Detective Rodriguez', 'Mysterious Mr. Black'],
│ storyline="When Alex Monroe, an ex-CIA operative, is framed for a crime he didn't commit, he must navigate the dangerous streets of New York to clear his name. As he uncovers a labyrinth of deceit involving the city's most notorious crime syndicate, he enlists the help of an old flame, Eva Parker. Together, they race against time to expose the true villain before it's too late."
)

# Use the structured output
MovieScript(
│ setting='In the bustling streets and iconic skyline of New York City.',
│ ending='Isabella and Alex, having narrowly escaped the clutches of the Syndicate, find themselves standing at the top of the Empire State Building. As the glow of the setting sun bathes the city, they share a victorious kiss. Newly emboldened and as an unstoppable duo, they vow to keep NYC safe from any future threats.',
│ genre='Action Thriller',
│ name='The NYC Chronicles',
│ characters=['Isabella Grant', 'Alex Chen', 'Marcus Kane', 'Detective Ellie Monroe', 'Victor Sinclair'],
│ storyline='Isabella Grant, a fearless investigative journalist, uncovers a massive conspiracy involving a powerful syndicate plotting to control New York City. Teaming up with renegade cop Alex Chen, they must race against time to expose the culprits before the city descends into chaos. Dodging danger at every turn, they fight to protect the city they love from imminent destruction.'
)
```

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/async/structured_output.py)

# Agent Teams [Deprecated]
Source: https://docs.agno.com/agents/teams

<Note>
 Agent Teams were an initial implementation of our multi-agent architecture (2023-2025) that use a transfer/handoff mechanism. After 2 years of experimentation, we've learned that this mechanism is not scalable and do NOT recommend it for complex multi-agent systems.

 Please use the new [Teams](/teams) architecture instead.
</Note>

We can combine multiple Agents to form a team and tackle tasks as a cohesive unit. Here's a simple example that converts an agent into a team to write an article about the top stories on hackernews.

```python hackernews_team.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.hackernews import HackerNewsTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

article_reader = Agent(
 name="Article Reader",
 model=OpenAIChat("gpt-4o"),
 role="Reads articles from URLs.",
 tools=[Newspaper4kTools()],
)

hn_team = Agent(
 name="Hackernews Team",
 model=OpenAIChat("gpt-4o"),
 team=[hn_researcher, web_searcher, article_reader],
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the article reader to read the links for the stories to get more information.",
 "Important: you must provide the article reader with the links to read.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 show_tool_calls=True,
 markdown=True,
)
hn_team.print_response("Write an article about the top 2 stories on hackernews", stream=True)
```

Run the script to see the output.

```bash
pip install -U openai duckduckgo-search newspaper4k lxml_html_clean agno

python hackernews_team.py
```

## How to build Agent Teams

1. Add a `name` and `role` parameter to the member Agents.
2. Create a Team Leader that can delegate tasks to team-members.
3. Use your Agent team just like you would use a regular Agent.

# Tools
Source: https://docs.agno.com/agents/tools

Learn how to use tools in Agno to build AI agents.

**Agents use tools to take actions and interact with external systems**.

Tools are functions that an Agent can run to achieve tasks. For example: searching the web, running SQL, sending an email or calling APIs. You can use any python function as a tool or use a pre-built **toolkit**. The general syntax is:

```python
from agno.agent import Agent

agent = Agent(
 # Add functions or Toolkits
 tools=[...],
 # Show tool calls in the Agent response
 show_tool_calls=True
)
```

## Using a Toolkit

Agno provides many pre-built **toolkits** that you can add to your Agents. For example, let's use the DuckDuckGo toolkit to search the web.

<Tip>You can find more toolkits in the [Toolkits](/tools/toolkits) guide.</Tip>

<Steps>
 <Step title="Create Web Search Agent">
 Create a file `web_search.py`

 ```python web_search.py
 from agno.agent import Agent
 from agno.tools.duckduckgo import DuckDuckGoTools

 agent = Agent(tools=[DuckDuckGoTools()], show_tool_calls=True, markdown=True)
 agent.print_response("Whats happening in France?", stream=True)
 ```
 </Step>

 <Step title="Run the agent">
 Install libraries

 ```shell
 pip install openai duckduckgo-search agno
 ```

 Run the agent

 ```shell
 python web_search.py
 ```
 </Step>
</Steps>

## Writing your own Tools

For more control, write your own python functions and add them as tools to an Agent. For example, here's how to add a `get_top_hackernews_stories` tool to an Agent.

```python hn_agent.py
import json
import httpx

from agno.agent import Agent

def get_top_hackernews_stories(num_stories: int = 10) -> str:
 """Use this function to get top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to return. Defaults to 10.

 Returns:
 str: JSON string of top stories.
 """

 # Fetch top story IDs
 response = httpx.get('https://hacker-news.firebaseio.com/v0/topstories.json')
 story_ids = response.json()

 # Fetch story details
 stories = []
 for story_id in story_ids[:num_stories]:
 story_response = httpx.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json')
 story = story_response.json()
 if "text" in story:
 story.pop("text", None)
 stories.append(story)
 return json.dumps(stories)

agent = Agent(tools=[get_top_hackernews_stories], show_tool_calls=True, markdown=True)
agent.print_response("Summarize the top 5 stories on hackernews?", stream=True)
```

Read more about:

* [Available toolkits](/tools/toolkits)
* [Using functions as tools](/tools/tool-decorator)

## Attributes

The following attributes allow an `Agent` to use tools

| Parameter | Type | Default | Description |
| ------------------------ | ------------------------------------------------------ | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tools` | `List[Union[Tool, Toolkit, Callable, Dict, Function]]` | - | A list of tools provided to the Model. Tools are functions the model may generate JSON inputs for. |
| `show_tool_calls` | `bool` | `False` | Print the signature of the tool calls in the Model response. |
| `tool_call_limit` | `int` | - | Maximum number of tool calls allowed for a single run. |
| `tool_choice` | `Union[str, Dict[str, Any]]` | - | Controls which (if any) tool is called by the model. "none" means the model will not call a tool and instead generates a message. "auto" means the model can pick between generating a message or calling a tool. Specifying a particular function via `{"type": "function", "function": {"name": "my_function"}}` forces the model to call that tool. "none" is the default when no tools are present. "auto" is the default if tools are present. |
| `read_chat_history` | `bool` | `False` | Add a tool that allows the Model to read the chat history. |
| `search_knowledge` | `bool` | `False` | Add a tool that allows the Model to search the knowledge base (aka Agentic RAG). |
| `update_knowledge` | `bool` | `False` | Add a tool that allows the Model to update the knowledge base. |
| `read_tool_call_history` | `bool` | `False` | Add a tool that allows the Model to get the tool call history. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/tree/main/cookbook/tools)

# User Control Flows
Source: https://docs.agno.com/agents/user-control-flow

Learn how to control the flow of an agent's execution in Agno. This is also called "Human in the Loop".

User control flows in Agno enable you to implement "Human in the Loop" patterns, where human oversight and input are required during agent execution. This is crucial for:

* Validating sensitive operations
* Reviewing tool calls before execution
* Gathering user input for decision-making
* Managing external tool execution

## Types of User Control Flows

Agno supports four main types of user control flows:

1. **User Confirmation**: Require explicit user approval before executing tool calls
2. **User Input**: Gather specific information from users during execution
3. **Dynamic User Input**: Have the agent collect user input as it needs it
4. **External Tool Execution**: Execute tools outside of the agent's control

## Pausing Agent Execution

User control flows interrupt the agent's execution and require human oversight. The run can then be continued by calling the `continue_run` method.

For example:

```python
agent.run("Perform sensitive operation")

if agent.is_paused:
 # The agent will pause while human input is provided
 # ... perform other tasks

 # The user can then continue the run
 response = agent.continue_run()
 # or response = await agent.acontinue_run()
```

The `continue_run` method continues with the state of the agent at the time of the pause. You can also pass the `run_response` of a specific run to the `continue_run` method, or the `run_id`.

## User Confirmation

User confirmation allows you to pause execution and require explicit user approval before proceeding with tool calls. This is useful for:

* Sensitive operations
* API calls that modify data
* Actions with significant consequences

The following example shows how to implement user confirmation.

```python
from agno.tools import tool
from agno.agent import Agent
from agno.models.openai import OpenAIChat

@tool(requires_confirmation=True)
def sensitive_operation(data: str) -> str:
 """Perform a sensitive operation that requires confirmation."""
 # Implementation here
 return "Operation completed"

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[sensitive_operation],
)

# Run the agent
agent.run("Perform sensitive operation")

# Handle confirmation
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_confirmation:
 # Get user confirmation
 print(f"Tool {tool.tool_name}({tool.tool_args}) requires confirmation")
 confirmed = input(f"Confirm? (y/n): ").lower() == "y"
 tool.confirmed = confirmed

 # Continue execution
 response = agent.continue_run()
```

You can also specify which tools in a toolkit require confirmation.

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.tools.yfinance import YFinanceTools
from agno.utils import pprint

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[YFinanceTools(requires_confirmation_tools=["get_current_stock_price"])],
)

agent.run("What is the current stock price of Apple?")
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_confirmation:
 print(f"Tool {tool.tool_name}({tool.tool_args}) requires confirmation")
 confirmed = input(f"Confirm? (y/n): ").lower() == "y"

 if message == "n":
 tool.confirmed = False
 else:
 # We update the tools in place
 tool.confirmed = True

 run_response = agent.continue_run()
 pprint.pprint_run_response(run_response)
```

## User Input

User input flows allow you to gather specific information from users during execution. This is useful for:

* Collecting required parameters
* Getting user preferences
* Gathering missing information

In the example below, we require all the input for the `send_email` tool from the user.

```python
from typing import List
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.function import UserInputField

# We still provide a docstring to the tool; This will be used to populate the `user_input_schema`
@tool(requires_user_input=True)
def send_email(to: str, subject: str, body: str) -> dict:
 """Send an email to the user.

 Args:
 to (str): The address to send the email to.
 subject (str): The subject of the email.
 body (str): The body of the email.
 """
 # Implementation here
 return f"Email sent to {to} with subject {subject} and body {body}"

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[send_email],
)

agent.run("Send an email please")
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name} ({field.field_type.__name__}) -> {field.description}")

 # Get user input
 user_value = input(f"Please enter a value for {field.name}: ")

 # Update the field value
 field.value = user_value

 run_response = (
 agent.continue_run()
 )
```

The `RunResponse` object has a list of tools and in the case of `requires_user_input`, the tools that require input will have `user_input_schema` populated.
This is a list of `UserInputField` objects.

```python
class UserInputField:
 name: str # The name of the field
 field_type: Type # The required type of the field
 description: Optional[str] = None # The description of the field
 value: Optional[Any] = None # The value of the field. Populated by the agent or the user.
```

You can also specify which fields should be filled by the user while the agent will provide the rest of the fields.

```python

# You can either specify the user_input_fields leave empty for all fields to be provided by the user
@tool(requires_user_input=True, user_input_fields=["to_address"])
def send_email(subject: str, body: str, to_address: str) -> str:
 """
 Send an email.

 Args:
 subject (str): The subject of the email.
 body (str): The body of the email.
 to_address (str): The address to send the email to.
 """
 return f"Sent email to {to_address} with subject {subject} and body {body}"

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[send_email],
)

agent.run("Send an email with the subject 'Hello' and the body 'Hello, world!'")
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name} ({field.field_type.__name__}) -> {field.description}")

 # Get user input (if the value is not set, it means the user needs to provide the value)
 if field.value is None:
 user_value = input(f"Please enter a value for {field.name}: ")
 field.value = user_value
 else:
 print(f"Value provided by the agent: {field.value}")

 run_response = (
 agent.continue_run()
 )
```

## Dynamic User Input

This pattern provides the agent with tools to indicate when it needs user input. It's ideal for:

* Cases where it is unknown how the user will interact with the agent
* When you want a form-like interaction with the user

In the following example, we use a specialized tool to allow the agent to collect user feedback when it needs it.

```python
from typing import Any, Dict

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.tools.toolkit import Toolkit
from agno.tools.user_control_flow import UserControlFlowTools
from agno.utils import pprint

# Example toolkit for handling emails
class EmailTools(Toolkit):
 def __init__(self, *args, **kwargs):
 super().__init__(
 name="EmailTools", tools=[self.send_email, self.get_emails], *args, **kwargs
 )

 def send_email(self, subject: str, body: str, to_address: str) -> str:
 """Send an email to the given address with the given subject and body.

 Args:
 subject (str): The subject of the email.
 body (str): The body of the email.
 to_address (str): The address to send the email to.
 """
 return f"Sent email to {to_address} with subject {subject} and body {body}"

 def get_emails(self, date_from: str, date_to: str) -> str:
 """Get all emails between the given dates.

 Args:
 date_from (str): The start date.
 date_to (str): The end date.
 """
 return [
 {
 "subject": "Hello",
 "body": "Hello, world!",
 "to_address": "test@test.com",
 "date": date_from,
 },
 {
 "subject": "Random other email",
 "body": "This is a random other email",
 "to_address": "john@doe.com",
 "date": date_to,
 },
 ]

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[EmailTools(), UserControlFlowTools()],
 markdown=True,
 debug_mode=True,
)

run_response = agent.run("Send an email with the body 'How is it going in Tokyo?'")

# We use a while loop to continue the running until the agent is satisfied with the user input
while run_response.is_paused:
 for tool in run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name} ({field.field_type.__name__}) -> {field.description}")

 # Get user input (if the value is not set, it means the user needs to provide the value)
 if field.value is None:
 user_value = input(f"Please enter a value for {field.name}: ")
 field.value = user_value
 else:
 print(f"Value provided by the agent: {field.value}")

 run_response = agent.continue_run(run_response=run_response)

 # If the agent is not paused for input, we are done
 if not run_response.is_paused:
 pprint.pprint_run_response(run_response)
 break
```

## External Tool Execution

External tool execution allows you to execute tools outside of the agent's control. This is useful for:

* External service calls
* Database operations

```python
import subprocess

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint

# We have to create a tool with the correct name, arguments and docstring for the agent to know what to call.
@tool(external_execution=True)
def execute_shell_command(command: str) -> str:
 """Execute a shell command.

 Args:
 command (str): The shell command to execute

 Returns:
 str: The output of the shell command
 """
 return subprocess.check_output(command, shell=True).decode("utf-8")

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[execute_shell_command],
 markdown=True,
)

run_response = agent.run("What files do I have in my current directory?")
if run_response.is_paused:
 for tool in run_response.tools_awaiting_external_execution:
 if tool.tool_name == execute_shell_command.name:
 print(f"Executing {tool.tool_name} with args {tool.tool_args} externally")

 # We execute the tool ourselves. You can execute any function or process here and use the tool_args as input.
 result = execute_shell_command.entrypoint(**tool.tool_args)
 # We have to set the result on the tool execution object so that the agent can continue
 tool.result = result

 run_response = agent.continue_run()
 pprint.pprint_run_response(run_response)
```

## Best Practices

1. **Sanitise user input**: Always validate and sanitize user input to prevent security vulnerabilities.
2. **Error Handling**: Always implement proper error handling for user input and external calls
3. **Input Validation**: Validate user input before processing

## Developer Resources

* View more [Examples](/examples/concepts/user-control-flows)
* View [Cookbook](https://github.com/agno-agi/agno/tree/main/cookbook/agent_concepts/user_control_flows)

# AG-UI App
Source: https://docs.agno.com/applications/ag-ui/introduction

Expose your Agno Agent as a AG-UI compatible app

AG-UI, or [Agent-User Interaction Protocol](https://github.com/ag-ui-protocol/ag-ui), is a protocol standarizing how AI agents connect to front-end applications.

## Example usage

<Steps>
 <Step title="Install the backend dependencies">
 ```bash
 pip install agno ag-ui-protocol
 ```
 </Step>

 <Step title="Run the backend">
 Now let's run a `AGUIApp` exposing an Agno Agent. You can use the previous code!
 </Step>

 <Step title="Run the frontend">
 You can use [Dojo](https://github.com/ag-ui-protocol/ag-ui/tree/main/typescript-sdk/apps/dojo), an advanced and customizable option to use as frontend for AG-UI agents.

 1. Clone the project: `git clone https://github.com/ag-ui-protocol/ag-ui.git`
 2. Follow the instructions [here](https://github.com/ag-ui-protocol/ag-ui/tree/main/typescript-sdk/apps/dojo) to learn how to install the needed dependencies and run the project.
 3. Remember to install the dependencies in `/ag-ui/typescript-sdk` with `pnpm install`, and to build the Agno package in `/integrations/agno` with `pnpm run build`.
 4. You can now run your Dojo! It will show our Agno agent as one of the available options.
 </Step>

 <Step title="Chat with your Agno Agent">
 Done! If you are running Dojo as your front-end, you can now go to [http://localhost:3000](http://localhost:3000) in your browser and chat with your Agno Agent.
 </Step>
</Steps>

![AG-UI Dojo screenshot](https://mintlify.s3.us-west-1.amazonaws.com/agno/images/agui-dojo.png)

You can see more examples in our [AG-UI integration examples](/examples/applications/ag-ui) section.

## Core Components

* `AGUIApp`: Wraps Agno agents/teams for in a FastAPI app.
* `serve`: Serves the FastAPI AG-UI app using Uvicorn.

`AGUIApp` uses helper functions for routing.

## `AGUIApp` Class

Main entry point for Agno AG-UI apps.

### Initialization Parameters

| Parameter | Type | Default | Description |
| ------------- | -------------------------- | ------- | ------------------------------------------------ |
| `agent` | `Optional[Agent]` | `None` | Agno `Agent` instance. |
| `team` | `Optional[Team]` | `None` | Agno `Team` instance. |
| `settings` | `Optional[APIAppSettings]` | `None` | API configuration. Defaults if `None`. |
| `api_app` | `Optional[FastAPI]` | `None` | Existing FastAPI app. New one created if `None`. |
| `router` | `Optional[APIRouter]` | `None` | Existing APIRouter. New one created if `None`. |
| `app_id` | `Optional[str]` | `None` | App identifier (autogenerated if not set). |
| `name` | `Optional[str]` | `None` | Name for the App. |
| `description` | `Optional[str]` | `None` | Description for the App. |

*Provide `agent` or `team`, not both.*

### Key Method

| Method | Parameters | Return Type | Description |
| --------- | ------------------------ | ----------- | ------------------------------------------------------------------------------------------- |
| `get_app` | `use_async: bool = True` | `FastAPI` | Returns configured FastAPI app (async by default). Sets prefix, error handlers, CORS, docs. |

## Endpoints

Endpoints are available at the specified `prefix` (default `/v1`).

### 1. `POST /agui`

This is the main entrypoint to interact with your Agno Agent or Team.

It expects a `RunAgentInput` object (from the `ag-ui-protocol` package) as defined by the protocol. You can read more about it in [their docs](https://docs.ag-ui.com/quickstart/server).

## Serving the Application (`serve`)

Serves the FastAPI app using Uvicorn.

### Parameters

| Parameter | Type | Default | Description |
| --------- | --------------------- | ------------- | ------------------------------------------------- |
| `app` | `Union[str, FastAPI]` | `N/A` | FastAPI app instance or import string (Required). |
| `host` | `str` | `"localhost"` | Host to bind. |
| `port` | `int` | `7777` | Port to bind. |
| `reload` | `bool` | `False` | Enable auto-reload for development. |

You can check some usage examples in our [AG-UI integration examples](/examples/applications/ag-ui) section.

# FastAPI App
Source: https://docs.agno.com/applications/fastapi/introduction

Host agents as FastAPI Applications.

The FastAPI App is used to serve Agents or Teams using a FastAPI server with a rest api interface.

### Example Usage

Create an agent, wrap it with `FastAPIApp`, and serve it:

```python
from agno.agent import Agent
from agno.app.fastapi.app import FastAPIApp
from agno.models.openai import OpenAIChat

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"), # Ensure OPENAI_API_KEY is set
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
)

# Async router by default (use_async=True)
fastapi_app = FastAPIApp(
 agent=basic_agent,
 name="Basic Agent",
 app_id="basic_agent",
 description="A basic agent that can answer questions and help with tasks.",
)

app = fastapi_app.get_app()

# For synchronous router:
# app = fastapi_app.get_app(use_async=False)

if __name__ == "__main__":
 fastapi_app.serve(app="basic:app", port=8001, reload=True)

```

**To run:**

1. Set `OPENAI_API_KEY` environment variable.
2. API at `http://localhost:8001`, docs at `http://localhost:8001/docs`.

Send `POST` requests to `http://localhost:8001/v1/run`:

```json
{
 "message": "Hello Basic Agent, tell me a fun fact!",
 "stream": false
}
```

## Core Components

* `FastAPIApp`: Wraps Agno agents/teams for FastAPI.
* `FastAPIApp.serve`: Serves the FastAPI app using Uvicorn.

`FastAPIApp` uses helper functions for routing.

## `FastAPIApp` Class

Main entry point for Agno FastAPI apps.

### Initialization Parameters

| Parameter | Type | Default | Description |
| ------------- | -------------------------- | ------- | ------------------------------------------------ |
| `agents` | `Optional[List[Agent]]` | `None` | List of Agno `Agent` instances. |
| `teams` | `Optional[List[Team]]` | `None` | List of Agno `Team` instances. |
| `workflows` | `Optional[List[Team]]` | `None` | List of Agno `Workflow` instances. |
| `settings` | `Optional[APIAppSettings]` | `None` | API configuration. Defaults if `None`. |
| `api_app` | `Optional[FastAPI]` | `None` | Existing FastAPI app. New one created if `None`. |
| `router` | `Optional[APIRouter]` | `None` | Existing APIRouter. New one created if `None`. |
| `app_id` | `Optional[str]` | `None` | App identifier (autogenerated if not set). |
| `name` | `Optional[str]` | `None` | Name for the App. |
| `description` | `Optional[str]` | `None` | Description for the App. |

*Provide `agent` or `team`, not both.*

### Key Method

| Method | Parameters | Return Type | Description |
| --------- | --------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------- |
| `get_app` | `use_async: bool = True`<br />`prefix: str = "/v1"` | `FastAPI` | Returns configured FastAPI app (async by default). Sets prefix, error handlers, CORS, docs. |

## Endpoints

Endpoints are available at the specified `prefix` (default `/v1`).

### 1. `POST /run`

* **Description**: Interacts with the agent/team (uses `agent.run()`/`arun()` or `team.run()`/`arun()`).
* **Request Form Parameters**:
 | Parameter | Type | Default | Description |
 | ------------ | ---------------------------- | -------------------------------------- | --------------------------------------- |
 | `message` | `str` | `...` | Input message (Required). |
 | `stream` | `bool` | `True` (sync), `False` (async default) | Stream response. |
 | `monitor` | `bool` | `False` | Enable monitoring. |
 | `session_id` | `Optional[str]` | `None` | Session ID for conversation continuity. |
 | `user_id` | `Optional[str]` | `None` | User ID. |
 | `files` | `Optional[List[UploadFile]]` | `None` | Files to upload. |
* **Responses**:
 * `stream=True`: `StreamingResponse` (`text/event-stream`) with JSON `RunResponse`/`TeamRunResponse` events.
 * `stream=False`: JSON `RunResponse`/`TeamRunResponse` dictionary.

### Parameters

| Parameter | Type | Default | Description |
| --------- | --------------------- | ------------- | ------------------------------------------------- |
| `app` | `Union[str, FastAPI]` | `N/A` | FastAPI app instance or import string (Required). |
| `host` | `str` | `"localhost"` | Host to bind. |
| `port` | `int` | `7777` | Port to bind. |
| `reload` | `bool` | `False` | Enable auto-reload for development. |

# Playground App
Source: https://docs.agno.com/applications/playground/introduction

Host agents as Playground Applications.

The Playground App is used to serve Agents, Teams and Workflows using a FastAPI server with several endpoints to manage and interact with `Agents`, `Workflows`, and `Teams` on the [Agno Playground](/introduction/playground).

### Example Usage

Create an agent, and serve it with `Playground`:

```python
from agno.agent import Agent
from agno.memory.agent import AgentMemory
from agno.memory.db.postgres import PgMemoryDb
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.postgres import PostgresStorage

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"), # Ensure OPENAI_API_KEY is set
 memory=AgentMemory(
 db=PgMemoryDb(
 table_name="agent_memory",
 db_url=db_url,
 ),
 create_user_memories=True,
 update_user_memories_after_run=True,
 create_session_summary=True,
 update_session_summary_after_run=True,
 ),
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
)

playground = Playground(
 agents=[
 basic_agent,
 ],
 name="Basic Agent",
 description="A playground for basic agent",
 app_id="basic-agent",
)
app = playground.get_app()

if __name__ == "__main__":
 playground.serve(app="basic:app", reload=True)
```

**To run:**

1. Ensure your PostgreSQL server is running and accessible via the `db_url`.
2. Set the `OPENAI_API_KEY` environment variable.
3. The Playground UI will be available at `http://localhost:7777`. API docs (if enabled in settings) are typically at `http://localhost:7777/docs`.
4. Use playground with [Agent Playground](/introduction/playground) .

## Core Components

* `Playground`: Wraps Agno agents, teams, or workflows in an API.
* `Playground.serve`: Serves the Playground FastAPI app using Uvicorn.

The `Playground` class is the main entry point for creating Agno Playground applications. It allows you to easily expose your agents, teams, and workflows through a web interface with [Agent Playground](/introduction/playground) or [Agent UI](/agent-ui/introduction).

## `Playground` Class

### Initialization Parameters

| Parameter | Type | Default | Description |
| ------------- | ------------------------------ | ------- | ----------------------------------------------------- |
| `agents` | `Optional[List[Agent]]` | `None` | List of Agno `Agent` instances. |
| `teams` | `Optional[List[Team]]` | `None` | List of Agno `Team` instances. |
| `workflows` | `Optional[List[Workflow]]` | `None` | List of Agno `Workflow` instances. |
| `settings` | `Optional[PlaygroundSettings]` | `None` | Playground configuration. Defaults if `None`. |
| `api_app` | `Optional[FastAPI]` | `None` | Existing FastAPI app. A new one is created if `None`. |
| `router` | `Optional[APIRouter]` | `None` | Existing APIRouter. A new one is created if `None`. |
| `app_id` | `Optional[str]` | `None` | App identifier (autogenerated if not set). |
| `name` | `Optional[str]` | `None` | Name for the App. |
| `description` | `Optional[str]` | `None` | Description for the App. |

*Provide at least one of `agents`, `teams`, or `workflows`.*

### Key Methods

| Method | Parameters | Return Type | Description |
| ------------------ | --------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------- |
| `get_app` | `use_async: bool = True`<br />`prefix: str = "/v1"` | `FastAPI` | Returns configured FastAPI app (async by default). Sets prefix, error handlers, CORS, docs. |
| `get_router` | | `APIRouter` | Returns the synchronous APIRouter for playground endpoints. |
| `get_async_router` | | `APIRouter` | Returns the asynchronous APIRouter for playground endpoints. |

### Endpoints

Endpoints are available at the specified `prefix` (default `/v1`) combined with the playground router's prefix (`/playground`). For example, the status endpoint is typically `/v1/playground/status`.

### Parameters

| Parameter | Type | Default | Description |
| --------- | --------------------- | ------------- | ------------------------------------------------- |
| `app` | `Union[str, FastAPI]` | `N/A` | FastAPI app instance or import string (Required). |
| `host` | `str` | `"localhost"` | Host to bind. |
| `port` | `int` | `7777` | Port to bind. |
| `reload` | `bool` | `False` | Enable auto-reload for development. |

# Slack App
Source: https://docs.agno.com/applications/slack/introduction

Host agents as Slack Applications.

The Slack App is used to serve Agents or Teams via Slack, using a FastAPI server to handle Slack events and send messages.

## Setup Steps

<Snippet file="setup-slack-app.mdx" />

### Example Usage

Create an agent, wrap it with `SlackAPI`, and serve it:

```python
from agno.agent import Agent
from agno.app.slack.app import SlackAPI
from agno.models.openai import OpenAIChat

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"), # Ensure OPENAI_API_KEY is set
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
)

slack_api_app = SlackAPI(
 agent=basic_agent,
)
app = slack_api_app.get_app()

if __name__ == "__main__":
 slack_api_app.serve("basic:app", port=8000, reload=True)
```

## Core Components

* `SlackAPI`: Wraps Agno agents/teams for Slack integration via FastAPI.
* `SlackAPI.serve`: Serves the FastAPI app using Uvicorn, configured for Slack.

## `SlackAPI` Class

Main entry point for Agno Slack applications.

### Initialization Parameters

| Parameter | Type | Default | Description |
| ------------- | -------------------------- | ------- | ------------------------------------------------ |
| `agent` | `Optional[Agent]` | `None` | Agno `Agent` instance. |
| `team` | `Optional[Team]` | `None` | Agno `Team` instance. |
| `settings` | `Optional[APIAppSettings]` | `None` | API configuration. Defaults if `None`. |
| `api_app` | `Optional[FastAPI]` | `None` | Existing FastAPI app. New one created if `None`. |
| `router` | `Optional[APIRouter]` | `None` | Existing APIRouter. New one created if `None`. |
| `app_id` | `Optional[str]` | `None` | App identifier (autogenerated if not set). |
| `name` | `Optional[str]` | `None` | Name for the App. |
| `description` | `Optional[str]` | `None` | Description for the App. |

*Provide `agent` or `team`, not both.*

## Endpoints

The main endpoint for Slack integration:

### `POST /slack/events`

* **Description**: Handles all Slack events including messages and app mentions
* **Security**: Verifies Slack signature for each request
* **Event Types**:
 * URL verification challenges
 * Message events
 * App mention events
* **Features**:
 * Threaded conversations
 * Background task processing
 * Message splitting for long responses
 * Support for both direct messages and channel interactions

## Testing the Integration

1. Start your application locally with `python <my-app>.py` (ensure ngrok is running)
2. Invite the bot to a channel using `/invite @YourAppName`
3. Try mentioning the bot in the channel: `@YourAppName hello`
4. Test direct messages by opening a DM with the bot

## Troubleshooting

* Verify all environment variables are set correctly
* Ensure the bot has proper permissions and is invited to channels
* Check ngrok connection and URL configuration
* Verify event subscriptions are properly configured
* Monitor application logs for detailed error messages

## Support

For additional help or to report issues, please refer to the documentation or open an issue in the repository.

# Whatsapp App
Source: https://docs.agno.com/applications/whatsapp/introduction

Host agents as Whatsapp Applications.

The Whatsapp App is used to serve Agents or Teams interacting via WhatsApp, using a FastAPI server to handle webhook events and to send messages.

<Snippet file="setup-whatsapp-app.mdx" />

### Example Usage

Create an agent, wrap it with `WhatsappAPI`, and serve it:

```python
from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.models.openai import OpenAIChat
from agno.tools.openai import OpenAITools

image_agent = Agent(
 model=OpenAIChat(id="gpt-4o"), # Ensure OPENAI_API_KEY is set
 tools=[OpenAITools(image_model="gpt-image-1")],
 markdown=True,
 show_tool_calls=True,
 debug_mode=True,
 add_history_to_messages=True,
)

# Async router by default (use_async=True)
whatsapp_app = WhatsappAPI(
 agent=image_agent,
 name="Image Generation Tools",
 app_id="image_generation_tools",
 description="A tool that generates images using the OpenAI API.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="image_generation_tools:app", port=8000, reload=True)
```

**To run:**

1. Ensure `OPENAI_API_KEY` environment variable is set if using OpenAI models.
2. The API will be running (e.g., `http://localhost:8000`), but interaction is primarily via WhatsApp through the configured webhook.
3. API docs (if enabled in settings) might be at `http://localhost:8000/docs`.

## Core Components

* `WhatsappAPI`: Wraps Agno agents/teams for WhatsApp integration via FastAPI.
* `WhatsappAPI.serve`: Serves the FastAPI app using Uvicorn, configured for WhatsApp.

## `WhatsappAPI` Class

Main entry point for Agno WhatsApp applications.

### Initialization Parameters

| Parameter | Type | Default | Description |
| ------------- | -------------------------- | ------- | ------------------------------------------------ |
| `agent` | `Optional[Agent]` | `None` | Agno `Agent` instance. |
| `team` | `Optional[Team]` | `None` | Agno `Team` instance. |
| `settings` | `Optional[APIAppSettings]` | `None` | API configuration. Defaults if `None`. |
| `api_app` | `Optional[FastAPI]` | `None` | Existing FastAPI app. New one created if `None`. |
| `router` | `Optional[APIRouter]` | `None` | Existing APIRouter. New one created if `None`. |
| `app_id` | `Optional[str]` | `None` | App identifier (autogenerated if not set). |
| `name` | `Optional[str]` | `None` | Name for the App. |
| `description` | `Optional[str]` | `None` | Description for the App. |

*Provide `agent` or `team`, not both.*

### Key Method

| Method | Parameters | Return Type | Description |
| --------- | ------------------------------------------------ | ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `get_app` | `use_async: bool = True`<br />`prefix: str = ""` | `FastAPI` | Returns configured FastAPI app. Sets prefix, error handlers, and includes WhatsApp routers. Async router is used by default. |

## Endpoints

Endpoints are accessible at the `prefix` (default is root level: `""`).

### 1. `GET /webhook`

* **Description**: Verifies WhatsApp webhook (challenge).
* **Responses**:
 * `200 OK`: Returns `hub.challenge` if tokens match.
 * `403 Forbidden`: Token mismatch or invalid mode.
 * `500 Internal Server Error`: `WHATSAPP_VERIFY_TOKEN` not set.

### 2. `POST /webhook`

* **Description**: Receives incoming WhatsApp messages and events.
* **Processing**:
 * Validates signature (if `APP_ENV="production"` and `WHATSAPP_APP_SECRET` is set).
 * Processes messages (text, image, video, audio, document) via `agent.arun()` or `team.arun()`.
 * Sends replies via WhatsApp.
* **Responses**:
 * `200 OK`: `{"status": "processing"}` or `{"status": "ignored"}`.
 * `403 Forbidden`: Invalid signature.
 * `500 Internal Server Error`: Other processing errors.

### Parameters

| Parameter | Type | Default | Description |
| --------- | --------------------- | ------------- | ------------------------------------------------- |
| `app` | `Union[str, FastAPI]` | `N/A` | FastAPI app instance or import string (Required). |
| `host` | `str` | `"localhost"` | Host to bind. |
| `port` | `int` | `7777` | Port to bind. |
| `reload` | `bool` | `False` | Enable auto-reload for development. |

# Product updates
Source: https://docs.agno.com/changelog/overview

<Update label="2025-06-05" description="v1.5.9">
 ## New Features:

 * **AG-UI App**: Expose your Agno Agents and Teams with an AG-UI compatible FastAPI APP.
 * **vLLM Support**: Added support for running vLLM models via Agno.
 * **Serper Toolkit:** Added `SerperTools` toolkit to search Google
 * **LangDB Support**: Added LangDB AI Gateway support into Agno.
 * **LightRAG server support:** Added LightRAG support which provides a fast, graph-based RAG system that enhances document retrieval and knowledge querying capabilities.
 * **Parser Model:** Added ability to use an external model to apply a structured output to a model response
 * **Pdf Bytes Knowledge: I**ntroduced a new knowledge base class: `PDFBytesKnowledgeBase`, which allows the ingestion of in-memory PDF content via bytes or IO streams instead of file paths.
 * **Qdrant Mcp Server:** Added MCP support for Qdrant
 * **Daytona integration:** Added `DaytonaTools` toolkit to let Agents execute code remotely on Daytona sandboxes
 * **Expand URL addition in Crawl4ai: I**ntroduced a new URL expansion feature directly into the Crawl4ai toolkit. Our agents frequently encounter shortened URLs that crawl4ai cannot scrape effectively, leading to incomplete data retrieval. With this update, shortened URLs are expanded to their final destinations before being processed by the crawler.
 * **AWS SES Tools**: Added `AWSSESTools` to send emails via AWS SES.
 * **Location Aware Agents:** Added `add_location_to_instructions` to automatically detect the current location where the agent is running and add that to the system message.

 ## Improvements:

 * **FastAPIApp Update**: FastAPIApp was updated and `agent` was replaced with `agents`, `team` with `teams` and `workflows` was added. This also now requires you to specify which agent/team/workflow to run.
 * E.g. `http://localhost:8001/runs?agent_id=my-agent`
 * **ZepTools Updates**: Updated `ZepTools` to remove deprecated features.
 * **GmailTools Attachments**: `GmailTools` now support attachments.
 * **Improve code reusability by using fetch with retry and async\_fetch\_with\_retry:** updated `fetch_with_retry` and `async_fetc_with_retry` to be reused in`url_reader.py`
 * **Add name to evaluation examples:** Included name param in evaluation examples
 * **XTools Search**: Added `search_posts` for `XTools`.

 ## Bug Fixes:

 * **Claude Prompt Tokens**: Fixed a bug with prompt tokens not propagating in Claude model class
 * **Add type in base App class for registry:** Can have different types of app like- `slack`, `whatsapp`, etc
 * **Accept empty array of pdf urls:** Fixed an issue where empty PDF URL arrays were not accepted, preventing knowledge base queries without adding new documents
 * **Anthropic cache metrics propagation:** Fixed a bug where Anthropic's prompt caching metrics were not propagating to Agent responses, despite the raw Anthropic API working correctly. This minimal fix ensures cache performance metrics are properly captured and reported.
 * **Handle non serializable objects on RunResponse dict parsing:**
 * Updated `RunResponse.to_dict()` to handle non-serializable fields, as Python enums
</Update>

<Update label="2025-06-03" description="v1.5.8">
 ## New Features:

 * **Slack App**: Introducing the `SlackApp` to allow you to create agents for Slack! The app allows agents to respond to individual messages or on group chats, and it creates threads to respond to messages.
 * **Visualization Tools**: Added `VisualizationTools` that uses `matplotlib` to give agents the ability to make graphs.
 * **Brave Search Tools:** Introduced a new toolkit for integrating `BraveSearch` that allows agent to search the web using brave search api.

 ## Improvements:

 * **Pass filters for traditional RAG:** Properly pass down `knowledge_filters` even if `self.add_references=True` which is a case for traditional RAG (diff from Agentic RAG)
 * **Add infer param to Mem0:** Added infer as a param to `Mem0Tools`

 ## Bug Fixes:

 * **Searxng tool initialization:** Fixed Searxng tool initialization error

 ```
 AttributeError: 'Searxng' object has no attribute 'include_tools'
 ```

 and added comprehensive unit tests.

 * **Fix for enum as a response model for Gemini:** With 1.5.6, a [bug](https://discord.com/channels/965734768803192842/965734768803192845/1377999191632121926) was introduced now allowing enum as a data type for Gemini response model.

 * **OpenAI parsing structured output:** With the changes in the OpenAI library we don't need to parse the structured output separately.

 * **Fix accuracy evals monitoring:** Added logic to handle monitoring when evaluating Teams in the run function of AccuracyEval

 ## Updates

 * **Updates to Apps:**
 * `FastAPIApp` does not have a default `prefix` anymore and `/run` → `/runs` (i.e. the created run endpoint is now `<your_domain>/runs`)
 * `serve_fastapi_app` is now replaced with `.serve()` on the instance of `FastAPIApp`.
 * `serve_whatsapp_app` is now replaced with `.serve()` on the instance of `WhatsappAPI`.
</Update>

<Update label="2025-05-30" description="v1.5.6">
 ## New Features

 * **Team Evals**: All types of Evaluations now support Teams!

 ## Improvements:

 * **Async Workflows**: Added `arun` support for Workflows, so they can now be used with `async` Python.
 * **Parallel Memory Updates**: Made speed improvements when user memories and session summaries are generated.
 * **Reimplement `tool_call_limit`**: Revamp of `tool_call_limit` to make it work across a whole agent run.
 * **Gemini / OpenAI Structure Response:** Improved Gemini and OpenAI Structured Response support. Dict types can now be used when defining structured responses.

 ## Bug Fixes:

 * **Mistral Structured Outputs with Tools**: Fixed an issue preventing Mistral model use with structured output and tools.
 * **Images In Run Without Prompt**: Fixed issues related to images being ignored if there wasn’t a prompt provided on `run`.
 * **Pgvector Upsert Fix: Fixed** Pgvector upsert not copying metadata properly.
 * **Handle AgnoInstrumentor failing with OpenAIResponses:** PR merged in Arize’s openinference repo: [https://github.com/Arize-ai/openinference/pull/1701](https://github.com/Arize-ai/openinference/pull/1701).
 * **Pinecone Filters:** Enabled filters for pinecone vector db.
 * **Combined KB Async:** Add missing async method to Combined KB.
 * **Team Session State Fix**: **`team_session_state`** is now correctly propagated and shared between all members and sub-teams of a team.
 * **Gemini type fix for integers:**
 * Pydantic models with `Dict[str, int]` fields (and other Dict types) were failing when used as `response_schema` for both OpenAI and Gemini models due to schema format incompatibilities.
 * **Session Name**: `session_name` is now available after a run.
 * **Handle UUIDs while serialization in RedisStorage:** Fixed error object of type UUID is not JSON serializable.

 ## Updates:

 * For managing `team_session_state`, you now have to set `team_session_state` on the `Team` instead of `session_state`.
</Update>

<Update label="2025-05-27" description="v1.5.5">
 ## New Features:

 * **Claude File Upload:** We can now upload a file to Anthropic directly and then use it as an input to an agent.
 * **Claude 4 Code Execution Tool:** Updated Claude to execute Python code in a secure, sandboxed environment.
 * \*\*Prompt caching with Anthropic Models: \*\* Allowed resuming from specific prefixes in your prompts. This approach significantly reduces processing time and costs for repetitive tasks or prompts with consistent elements.
 * **Vercel v0 Model:** Added support for new Vercel v0 models and cookbook examples.
 * **Qdrant Hybrid Search support**
 * **Markdown Knowledge Base**: Added native support for Markdown-based knowledge bases.
 * **AI/ML API platform integration:** Introduced integration with [`AI/ML API`](https://aimlapi.com/models/?utm_source=agno\&utm_medium=github\&utm_campaign=integration), a platform providing AI/ML models. AI/ML API provides 300+ AI models including Deepseek, Gemini, ChatGPT. The models run at enterprise-grade rate limits and uptimes.
 * **Update Pydantic and dataclass in function handling:** Added support for `Pydantic` and `dataclass` objects as input to a function. See [here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/tool_concepts/custom_tools/complex_input_types.py) for an example.

 ## Improvements:

 * **Timeout handling for API calls in ExaTools class:**
 * Timeout functionality to Exa API calls to prevent indefinite hanging of search operations. The implementation uses Python's `concurrent.futures` module to enforce timeouts on all Exa API operations (search, get contents, find similar, and answer generation).
 * This change addresses the issue where Exa search functions would hang indefinitely, causing potential service disruptions and resource leaks.
 * **Fetch messages from last N sessions:**
 * A tool for the agent, something like `get_previous_session_messages(number_of_sessions: int)` that returns a list of messages that the agent can analyse
 * Switch on with `search_previous_sessions_history`
 * **Redis Expiration**: Added `expire` key to set TTL on Redis keys.
 * **Add Anthropic Cache Write to Agent Session Metrics:** Added `cache_creation_input_tokens` to agent session metrics, to allow for tracking Anthropic cache write statistics

 ## Bug Fixes:

 * **Huggingface Embedder Updates:**
 * Huggingface has changed some things on their API and they've deprecated `.post` on their `InferenceClient()`- [https://discuss.huggingface.co/t/getting-error-attributeerror-inferenceclient-object-has-no-attribute-post/156682](https://discuss.huggingface.co/t/getting-error-attributeerror-inferenceclient-object-has-no-attribute-post/156682)
 * We can also no longer use `id: str = "jinaai/jina-embeddings-v2-base-code"` as default, because these models are no longer provided by the `HF Inference API`. Changed the default to `id: str = "intfloat/multilingual-e5-large"`
 * **Add `role_map` for `OpenAIChat`:** This allows certain models that don’t adhere to OpenAI’s role mapping to be used vir `OpenAILike`.
 * **Use Content Hash as ID in Upsert in Pgvector:** Use reproducible `content_hash` in upsert as ID.
 * **Insert in Vector DB passes only last chunk meta\_data:** Insert in vector db passes only last chunk meta\_data. issue link- [https://discord.com/channels/965734768803192842/1219054452221153463/1376631140047130649](https://discord.com/channels/965734768803192842/1219054452221153463/1376631140047130649)
 * **Remove Argument Sanitization:** Replaced with a safer way to do this that won't break arguments that shouldn't be sanitized
 * **Handle async tools when running async agents on playground:** Fixed a regression where using Agents with async tools (e.g. MCP tools) was breaking in the Playground.
</Update>

<Update label="2025-05-23" description="v1.5.4">
 ## New Features:

 * **User Control Flows**: This is the beta release of Agno’s Human-in-the-loop flows and tools.
 * We now allow agent runs to be `paused` awaiting completion of certain user requirements before the agent can continue.
 * This also adds the `agent.continue_run` and `agent.acontinue_run` functions.
 * The control flows that are available:
 * User confirmation flow → Decorate a function with `@tool(requires_confirmation=True)` and the agent will expect user confirmation before executing the tool.
 * User input required → Decorate a function with `@tool(requires_user_input=True)` to have the agent stop and ask for user input before continuing.
 * External tool execution → Decorate a function with `@tool(external_execution=True)` to indicate that you will execute this function outside of the agent context.
 * Dynamic user input → Add `UserControlFlowTools()` to an agent to give the agent the ability to dynamically stop the flow and ask for user input where required.
 * See a host of examples [here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/user_control_flows).
 * **Mem0 Toolkit**: Added a toolkit for managing memories in Mem0.
 * **Firecrawl Search**: Added support for Firecrawl web search in `FirecrawlTools`.

 ## Bug Fixes:

 * **Firecrawl Tools and Reader**: Fixed parameter parsing for the Firecrawl reader and tools.
 * **Include/Exclude on all Tools**: Ensure all toolkits support `include_tools` and `exclude_tools`.
</Update>

<Update label="2025-05-21" description="v1.5.3">
 ## Improvements:

 * **Improved Accuracy Evals:** Updated the way accuracy evals works for more accurate agent-based evaluation.

 ## Bug Fixes:

 * **MCP Client Timeout:** Client timeouts now work correctly and use the timeout set on parameters.
</Update>

<Update label="2025-05-20" description="v1.5.2">
 ## New Features:

 * **Agno Apps (Beta)**: Introducing Agno Apps, convenience functions to assist with building production-ready applications. The first supported apps are:
 * `FastAPIApp` → A really simple FastAPI server that provides access to your `agent` or `team`.
 * `WhatsappAPIApp` → An app that implements the Whatsapp protocol allowing you to have an Agno agent running on Whatsapp. Supports image / audio / video input and can generate images as responses. Supports reasoning.
 * **Couchbase Vector DB Support**: Added support for Couchbase as a vector DB for knowledge bases.
 * **Knowledge Filters Update for Teams:** Filters (manual + agentic) can now be used with Teams.
 * **Azure Cosmos DB for MongoDB (vCore) vector db support:** In the MongoDB vector db class add support for cosmosdb mongo vcore support by enabling `cosmos_compatibility=True`
 * **Google Big Query Tools**: Added Toolkit for Google BigQuery support.
 * **Async Support for s3 Readers:** Add async support for `pdf` and `text` s3 readers.
 * **`stop_after_tool_call` and `show_result` for Toolkits:** Now the base Toolkit class has `stop_after_tool_call_tools` and `show_result_tools` similar to the `@tool` decorator.
</Update>

<Update label="2025-05-16" description="v1.5.1">
 ## New Features:

 * **Nebius Model Provider**: Added [Nebius](https://studio.nebius.com/) as a model provider.
 * **Extended Filters Support on Vector DBs**: Added filtering support for other vector DBs.
 * pgvector
 * Milvus
 * Weaviate
 * Chroma

 ## Improvements:

 * **Redis SSL**: Added the `ssl` parameter to `Redis` storage.
</Update>

<Update label="2025-05-13" description="v1.5.0">
 ## New Features:

 * **Azure OpenAI Tools**: Added image generation via Dall-E via Azure AI Foundry.
 * **OpenTelemetry Instrumentation:** We have contributed to the [OpenInference](https://github.com/Arize-ai/openinference) project and added an auto-instrumentor for Agno agents. This adds tracing instrumentation for Agno Agents for any OpenTelemetry-compatible observability provider. These include Arize, Langfuse and Langsmith. Examples added to illustrate how to use each one ([here](https://github.com/agno-agi/agno/tree/main/cookbook/observability)).
 * **Evals Updates**: Added logic to run accuracy evaluations with pre-generated answers and minor improvements for all evals classes.
 * **Hybrid Search and Reranker for Milvus Vector DB:** Added support for `hybrid_search` on Milvus.
 * **MCP with Streamable-HTTP:** Now supporting the streamable-HTTP transport for MCP servers.

 ## Improvements:

 * **Knowledge Filters Cookbook:** Instead of storing the sample data locally, we now pull it from s3 at runtime to keep the forking of the repo as light as possible.

 ## Bug Fixes:

 * **Team Model State:** Fixed issues related to state being shared between models on teams.
 * **Concurrent Agent Runs**: Fixed certain race-conditions related to running agents concurrently.

 ## Breaking changes:

 * **Evals Refactoring:**
 * Our performance evaluation class has been renamed from `PerfEval` to `PerformanceEval`
 * Our accuracy evaluation class has new required fields: `agent`, `prompt` and `expected_answer`
 * **Concurrent Agent Runs:** We removed duplicate information from some events during streaming (`stream=True`). Individual events will have more relevant data now.
</Update>

<Update label="2025-05-10" description="v1.4.6">
 ## New Features:

 * **Cerebras Model Provider**: Added Cerebras as a model provider.
 * **Claude Web Search**: Added support for [Claude’s new web search tool](https://www.anthropic.com/news/web-search).
 * **Knowledge Base Metadata Filtering (Beta)**: Added support for filtering documents by metadata
 * **Two Ways to Apply Filters**:
 * **Explicit Filtering**: Pass filters directly to Agent or during run/query

 ```python
 # Option 1: Filters on Agent initialization
 agent = Agent(
 knowledge=knowledge_base, 
 knowledge_filters={"filter_1": "abc"}
 )
 
 # Option 2: Filters on run execution
 agent.run("Tell me about...", knowledge_filters={"filter_1": "abc"})
 ```

 See docs [here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/filters/pdf/filtering.py)

 * **Agentic Filtering**: Agent automatically detects and applies filters from user queries

 ```python
 # Enable automatic filter detection
 agent = Agent(
 knowledge=knowledge_base, 
 enable_agentic_knowledge_filters=True
 )
 
 # Agent extracts filters from query
 agent.run("Tell me about John Doe's experience...")
 ```

 See docs [here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/filters/pdf/agentic_filtering.py)
 * Two approaches for adding metadata to documents:
 1. **During Knowledge Base Initialization**:

 ```python
 knowledge_base = PDFKnowledgeBase(path=[
 {
 "path": "file_1.pdf", 
 "metadata": {
 "user_id": "abc"
 }
 },
 {
 "path": "file_2.pdf", 
 "metadata": {
 "user_id": "xyz"
 }
 }
 ])
 ```

 2. **During Individual Document Loading:**

 ```python
 knowledge_base.load_document(
 path="file.pdf",
 metadata={"user_id": "abc"}
 )
 ```
 * **Compatibility**
 * **Knowledge Base Types**: `PDF`, `Text`, `DOCX`, `JSON`, and `PDF_URL`
 * **Vector Databases**: `Qdrant`, `LanceDB`, and `MongoDB`

 ## Improvements:

 * **User and Session ID in Tools**: Added `current_user_id` and `current_session_id` as default variables in `session_data` for `Agent` and `Team`.

 ## Bug Fixes:

 * **Knowledge Base ID Clashes**: Knowledge files with overlapping names (e.g., `abc.-.xyz.pdf` and `abc.-.def.pdf`) were being incorrectly identified due to the readers using formatted names as unique id which were getting uniqueness conflict. Introduced a unique ID for each document in all the readers using `uuidv4()` to ensure strict identification and prevent conflicts.
</Update>

<Update label="2025-05-06" description="v1.4.5">
 ## New Features:

 * **Embedder Support via AWS Bedrock**: `AwsBedrockEmbedder` has been added with a default embedding model of `cohere.embed-multilingual-v3`.
 * **Gemini Video Generation Tool**: Added video generation capabilities to `GeminiTools`.

 ## Improvements:

 * **Apify Revamp**: Complete revamp of `ApifyTools` to make it completely compatible with Apify actors.

 ## Bug Fixes:

 * **Tools with Optional Parameters on Llama API**: Fixed edge cases with functions.
</Update>

<Update label="2025-05-03" description="v1.4.4">
 ## New Features:

 * **OpenAI File Support:** Added support for `File` attached to prompts for agents with `OpenAIChat` models.

 ## Improvements:

 * **Llama API:** Various improvements for Llama and LlamaOpenAI model classes including structured output and image input support
 * **Async Custom Retriever**: The `retriever` parameter can now be an `async` function to be used with `agent.arun` and `agent.aprint_response`.
 * **Gemini Video URL Input**: Added support for `Video(url=...)` for Gemini.

 ## Bug Fixes:

 * **OpenAI Responses o3 / o4 Tools**: Fixed broken tool use for advanced reasoning models on `OpenAIResponses`.
 * **MCP on CLI Support**: Fixed support for `MCPTools` usage while calling `agent.acli_app`.
</Update>

<Update label="2025-04-30" description="v1.4.3">
 ## **New Features:**

 * **Llama API:** Added native SDK and OpenAI-like model classes.

 ## **Improvements:**

 * **Claude**: Added support for AWS Session token for Claude.
 * **DynamoDB**: Added support for AWS profile-based authentication.

 ## **Bug Fixes:**

 * **Session Metrics**: Fix for session metrics showing up as 0.
 * **HF Embedder fix**: Fixed Hugging Face Embedder.
</Update>

<Update label="2025-04-25" description="v1.4.2">
 ## New Features:

 * **MCP SSE Support**: Added support for connecting to SSE MCP Servers.
 * **Tool Hooks**: You can now have a hook that is wrapped around all tool calls. This works for `Toolkits` and custom tools. See [this example](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/tool_concepts/toolkits/tool_hook.py).
 * **Team Session State:** You can now manage a single state dictionary across a team leader and team members inside tools given to the team leader/members. See [this example](https://github.com/agno-agi/agno/blob/main/cookbook/teams/team_with_shared_state.py).
 * **Cartesia Tool**: Added support for Cartesia for text-to-speech capabilities.
 * **Gemini Image Tools:** Added a tool that uses Gemini models to generate images.
 * **Groq Audio Tools**: Added a tool that uses Groq models to translate, transcribe and generate audio.

 ## Improvements:

 * **PubmedTools Expanded Results**: Added expanded result sets for `PubmedTools` .
 * **Variety in Tool Results**: Custom tools can now have any return type and it would be handled before being provided to the model.

 ## Bug Fixes:

 * **Teams Shared Model Bug**: Fixed issues where a single model is used across team members. This should reduce tool call failures in team execution.
</Update>

<Update label="2025-04-23" description="v1.4.0">
 ## New Features:

 * **Memory Generally Available**: We have made improvements and adjustments to how Agentic user memory management works. This is now out of beta and generally available. See these [examples](https://github.com/agno-agi/agno/tree/main/cookbook/agent_concepts/memory) and these [docs](https://docs.agno.com/agents/memory) for more info.
 * **OpenAI Tools**: Added `OpenAITools` to enable text-to-speech and image generation through OpenAI’s APIs.
 * **Zep Tools**: Added `ZepTools` and `AsyncZepTools` to manage memories for your Agent using `zep-cloud`

 ## Improvements:

 * **Azure AI Foundry Reasoning**: Added support for reasoning models via Azure AI Foundry. E.g. Deepseek-R1.
 * **Include/Exclude Tools**: Added `include_tools` and `exclude_tools` for all toolkits. This allows for selective enabling / disabling of tools inside toolkits, which is especially useful for larger toolkits.

 ## Bug Fixes:

 * **Gemini with Memory**: Fixed issue with `deepcopy` when Gemini is used with `Memory`.

 ## Breaking Changes:

 * **Memory:** Agents will now by default use an improved `Memory` instead of the now deprecated `AgentMemory`. - `agent.memory.messages` → `run.messages for run in agent.memory.runs` (or `agent.get_messages_for_session()`) - `create_user_memories` → `enable_user_memories` and is now set on the Agent/Team directly. - `create_session_summary` → `enable_session_summaries` and is now set on the Agent/Team directly.
</Update>

<Update label="2025-04-21" description="v1.3.5">
 ## Improvements:

 * **Further Async Vector DB Support**: Support added for:
 * [Clickhouse](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/clickhouse_db/async_clickhouse.py)
 * [ChromaDB](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/chroma_db/async_chroma_db.py)
 * [Cassandra](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/cassandra_db/async_cassandra_db.py)
 * [PineconeDB](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/pinecone_db/async_pinecone_db.py)
 * [Pgvector](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/pgvector_db/async_pg_vector.py)
 * **Reasoning on Agno Platform**:
 * Added extensive support for reasoning on the Agno Platform. Go see your favourite reasoning agents in action!
 * Changes from SDK
 * send proper events in different types of reasoning and populate the `reasoning_content` on `RunResponse` for `stream/non-stream`, `async/non-async`
 * unified json structure for all types of reasoning in `Reasoning events`
 * **Google Caching Support**: Added support for caching files and sending the cached content to Gemini.

 ## Bug Fixes

 * **Firecrawl Scrape**: Fixed issues with non-serializable types for during Firecrawl execution. [https://github.com/agno-agi/agno/issues/2883](https://github.com/agno-agi/agno/issues/2883)
</Update>

<Update label="2025-04-18" description="v1.3.4">
 ## New Features:

 * **Web Browser Tool:** Introduced a `webbrowser` tool for agents to interact with the web.
 * **Proxy Support:** Added `proxy` parameter support to both URL and PDF tools for network customization.

 ## Improvements:

 * **Session State:** Added examples for managing session state in agents.
 * **AzureOpenAIEmbedder:** Now considers `client_params` passed in the `client_params` argument for more flexible configuration.
 * **LiteLLM:** Now uses built-in environment validation to simplify setup.
 * **Team Class:** Added a `mode` attribute to team data serialization for enhanced team configuration.
 * **Insert/Upsert/Log Optimization:** insert/upsert/log\_info operations now trigger only when documents are present in the reader.
 * **Database Preference:** Session state now prefers database-backed storage if available.
 * **Memory Management:** Internal memory system updated for better session handling and resource efficiency.
 * **Module Exports:** Init files that only import now explicitly export symbols using `__all__`.

 ## Bug Fixes:

 * **DynamoDB Storage:** Fixed an issue with storage handling in DynamoDB-based setups.
 * **DeepSeek:** Fixed a bug with API key validation logic.
</Update>

<Update label="2025-04-17" description="v1.3.3">
 ## Improvements:

 * **Gemini File Upload**: Enabled direct use of uploaded files with Gemini.
 * **Metrics Update**: Added audio, reasoning and cached token counts to metrics where available on models.
 * **Reasoning Updates**: We now natively support Ollama and AzureOpenAI reasoning models.

 ## Bug Fixes:

 * **PPrint Util Async**: Added `apprint_run_response` to support async.
 * **Mistral Reasoning:** Fixed issues with using a Mistral model for chain-of-thought reasoning.
</Update>

<Update label="2025-04-16" description="v1.3.2">
 ## New Features:

 * **Redis Memory DB**: Added Redis as a storage provider for `Memory`. See [here](https://docs.agno.com/examples/concepts/memory/mem-redis-memory).

 ## Improvements:

 * **Memory Updates**: Various performance improvements made and convenience functions added:
 * `agent.get_session_summary()` → Use to get the previous session summary from the agent.
 * `agent.get_user_memories()` → Use to get the current user’s memories.
 * You can also add additional instructions to the `MemoryManager` or `SessionSummarizer`.
 * **Confluence Bypass SSL Verification**: If required, you can now skip SSL verification for Confluence connections.
 * **More Flexibility On Team Prompts**: Added `add_member_tools_to_system_message` to remove the member tool names from the system message given to the team leader, which allows flexibility to make teams transfer functions work in more cases.

 ## Bug Fixes:

 * **LiteLLM Streaming Tool Calls**: Fixed issues with tool call streaming in LiteLLM.
 * **E2B Casing Issue**: Fixed issues with parsed Python code that would make some values lowercase.
 * **Team Member IDs**: Fixed edge-cases with team member IDs causing teams to break.
</Update>

<Update label="2025-04-12" description="v1.3.0">
 ## New Features:

 * **Memory Revamp (Beta)**: This is a beta release of a complete revamp of Agno Memory. This includes a new `Memory` class that supports adding, updating and deleting user memories, as well as doing semantic search with a model. This also adds additional abilities to the agent to manage memories on your behalf. See the docs [here](https://docs.agno.com/memory/introduction).
 * **User ID and Session ID on Run**: You can now pass `user_id` and `session_id` on `agent.run()`. This will ensure the agent is set up for the session belonging to the `session_id` and that only the memories of the current user is accessible to the agent. This allows you to build multi-user and multi-session applications with a single agent configuration.
 * **Redis Storage**: Support added for Redis as a session storage provider.
</Update>

<Update label="2025-04-11" description="v1.2.16">
 ## Improvements:

 * **Teams Improvements**: Multiple improvements to teams to make task forwarding to member agents more reliable and to make the team leader more conversational. Also added various examples of reasoning with teams.
 * **Knowledge on Teams**: Added `knowledge` to `Team` to better align with the functionality on `Agent`. This comes with `retriever` to set a custom retriever and `search_knowledge` to enable Agentic RAG.

 ## Bug Fixes:

 * **Gemini Grounding Chunks**: Fixed error when Gemini Grounding was used in streaming.
 * **OpenAI Defaults in Structured Outputs**: OpenAI does not allow defaults in structured outputs. To make our structured outputs as compatible as possible without adverse effects, we made updates to `OpenAIResponses` and `OpenAIChat`.
</Update>

<Update label="2025-04-08" description="v1.2.14">
 ## Improvements:

 * **Improved Github Tools**: Added many more capabilities to `GithubTools`.
 * **Windows Scripts Support**: Converted all the utility scripts to be Windows compatible.
 * **MongoDB VectorDB Async Support**: MongoDB can now be used in async knowledge bases.

 ## Bug Fixes:

 * **Gemini Tool Formatting**: Fixed various cases where functions would not be parsed correctly when used with Gemini.
 * **ChromaDB Version Compatibility:** Fix to ensure that ChromaDB and Agno are compatible with newer versions of ChromaDB.
 * **Team-Member Interactions**: Fixed issue where if members respond with empty content the team would halt. This is now be resolved.
 * **Claude Empty Response:** Fixed a case when the response did not include any content with tool calls resulting in an error from the Anthropic API
</Update>

<Update label="2025-04-07" description="v1.2.12">
 ## New Features:

 * **Timezone Identifier:** Added a new `timezone_identifier` parameter in the Agent class to include the timezone alongside the current date in the instructions.
 * **Google Cloud JSON Storage**: Added support for JSON-based session storage on Google Cloud.
 * **Reasoning Tools**: Added `ReasoningTools` for an advanced reasoning scratchpad for agents.

 ## Improvements:

 * **Async Vector DB and Knowledge Base Improvements**: More knowledge bases have been updated for `async-await` support: - `URLKnowledgeBase` → Find some examples [here](https://github.com/agno-agi/agno/blob/9d1b14af9709dde1e3bf36c241c80fb295c3b6d3/cookbook/agent_concepts/knowledge/url_kb_async.py). - `FireCrawlKnowledgeBase` → Find some examples [here](https://github.com/agno-agi/agno/blob/596898d5ba27d2fe228ea4f79edbe9068d34a1f8/cookbook/agent_concepts/knowledge/firecrawl_kb_async.py). - `DocxKnowledgeBase` → Find some examples [here](https://github.com/agno-agi/agno/blob/f6db19f4684f6ab74044a4466946e281586ca1cf/cookbook/agent_concepts/knowledge/docx_kb_async.py).
</Update>

<Update label="2025-04-07" description="v1.2.11">
 ## Bug Fixes:

 * **Fix for structured outputs**: Fixed cases of structured outputs for reasoning.
</Update>

<Update label="2025-04-07" description="v1.2.10">
 ## 1.2.10

 ## New Features:

 * **Knowledge Tools**: Added `KnowledgeTools` for thinking, searching and analysing documents in a knowledge base.
</Update>

<Update label="2025-04-05" description="v1.2.9">
 ## 1.2.9

 ## Improvements:

 * **Simpler MCP Interface**: Added `MultiMCPTools` to support multiple server connections and simplified the interface to allow `command` to be passed. See [these examples](https://github.com/agno-agi/agno/blob/382667097c31fbb9f08783431dcac5eccd64b84a/cookbook/tools/mcp) of how to use it.
</Update>

<Update label="2025-04-04" description="v1.2.8">
 ## 1.2.8

 # Changelog

 ## New Features:

 * **Toolkit Instructions**: Extended `Toolkit` with `instructions` and `add_instructions` to enable you to specify additional instructions related to how a tool should be used. These instructions are then added to the model’s “system message” if `add_instructions=True` .

 ## Bug Fixes:

 * **Teams transfer functions**: Some tool definitions of teams failed for certain models. This has been fixed.
</Update>

<Update label="2025-04-02" description="v1.2.7">
 ## 1.2.7

 ## New Features:

 * **Gemini Image Generation**: Added support for generating images straight from Gemini using the `gemini-2.0-flash-exp-image-generation` model.

 ## Improvements:

 * **Vertex AI**: Improved use of Vertex AI with Gemini Model class to closely follow the official Google specification
 * **Function Result Caching Improvement:** We now have result caching on all Agno Toolkits and any custom functions using the `@tool` decorator. See the docs [here](https://docs.agno.com/tools/functions).
 * **Async Vector DB and Knowledge Base Improvements**: Various knowledge bases, readers and vector DBs now have `async-await` support, so it will be used in `agent.arun` and `agent.aprint_response`. This also means that `knowledge_base.aload()` is possible which should greatly increase loading speed in some cases. The following have been converted:
 * Vector DBs:
 * `LanceDb` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/lance_db/async_lance_db.py) is a cookbook to illustrate how to use it.
 * `Milvus` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/milvus_db/async_milvus_db.py) is a cookbook to illustrate how to use it.
 * `Weaviate` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/vector_dbs/weaviate_db/async_weaviate_db.py) is a cookbook to illustrate how to use it.
 * Knowledge Bases:
 * `JSONKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/json_kb_async.py) is a cookbook to illustrate how to use it.
 * `PDFKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/pdf_kb_async.py) is a cookbook to illustrate how to use it.
 * `PDFUrlKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/pdf_url_kb_async.py) is a cookbook to illustrate how to use it.
 * `CSVKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/csv_kb_async.py) is a cookbook to illustrate how to use it.
 * `CSVUrlKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/csv_url_kb_async.py) is a cookbook to illustrate how to use it.
 * `ArxivKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/arxiv_kb_async.py) is a cookbook to illustrate how to use it.
 * `WebsiteKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/website_kb_async.py) is a cookbook to illustrate how to use it.
 * `YoutubeKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/youtube_kb_async.py) is a cookbook to illustrate how to use it.
 * `TextKnowledgeBase` → [Here](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/text_kb_async.py) is a cookbook to illustrate how to use it.

 ## Bug Fixes:

 * **Recursive Chunking Infinite Loop**: Fixes an issue with RecursiveChunking getting stuck in an infinite loop for large documents.
</Update>

<Update label="2025-03-28" description="v1.2.6">
 ## 1.2.6

 ## Bug Fixes:

 * **Gemini Function call result fix**: Fixed a bug with function call results failing formatting and added proper role mapping .
 * **Reasoning fix**: Fixed an issue with default reasoning and improved logging for reasoning models .
</Update>

<Update label="2025-03-27" description="v1.2.5">
 ## 1.2.5

 ## New Features:

 * **E2B Tools:** Added E2B Tools to run code in E2B Sandbox

 ## Improvements:

 * **Teams Tools**: Add `tools` and `tool_call_limit` to `Team`. This means the team leader itself can also have tools provided by the user, so it can act as an agent.
 * **Teams Instructions:** Improved instructions around attached images, audio, videos, and files. This should increase success when attaching artifacts to prompts meant for member agents.
 * **MCP Include/Exclude Tools**: Expanded `MCPTools` to allow you to specify tools to specifically include or exclude from all the available tools on an MCP server. This is very useful for limiting which tools the model has access to.
 * **Tool Decorator Async Support**: The `@tool()` decorator now supports async functions, including async pre and post-hooks.

 ## Bug Fixes:

 * **Default Chain-of-Thought Reasoning:** Fixed issue where reasoning would not default to manual CoT if the provided reasoning model was not capable of reasoning.
 * **Teams non-markdown responses**: Fixed issue with non-markdown responses in teams.
 * **Ollama tool choice:** Removed `tool_choice` from Ollama usage as it is not supported.
 * **Worklow session retrieval from storage**: Fixed `entity_id` mappings.
</Update>

<Update label="2025-03-25" description="v1.2.4">
 ## 1.2.4

 ## Improvements:

 * **Tool Choice on Teams**: Made `tool_choice` configurable.

 ## Bug Fixes:

 * **Sessions not created**: Made issue where sessions would not be created in existing tables without a migration be more visible. Please read the docs on [storage schema migrations](https://docs.agno.com/agents/storage).
 * **Todoist fixes**: Fixed `update_task` on `TodoistTools`.
</Update>

<Update label="2025-03-24" description="v1.2.3">
 ## 1.2.3

 ## Improvements:

 * **Teams Error Handling:** Improved the flow in cases where the model gets it wrong when forwarding tasks to members.
</Update>

<Update label="2025-03-24" description="v1.2.2">
 ## 1.2.2

 ## Bug Fixes:

 * **Teams Memory:** Fixed issues related to memory not persisting correctly across multiple sessions.
</Update>

<Update label="2025-03-24" description="v1.2.1">
 ## 1.2.1

 ## Bug Fixes:

 * **Teams Markdown**: Fixed issue with markdown in teams responses.
</Update>

<Update label="2025-03-24" description="v1.2.0">
 ## 1.2.0

 ## New Features:

 * **Financial Datasets Tools**: Added tools for [https://www.financialdatasets.ai/](https://www.financialdatasets.ai/).
 * **Docker Tools**: Added tools to manage local docker environments.

 ## Improvements:

 * **Teams Improvements:** Reasoning enabled for the team.
 * **MCP Simplification:** Simplified creation of `MCPTools` for connections to external MCP servers. See the updated [docs](https://docs.agno.com/tools/mcp#example%3A-filesystem-agent).

 ## Bug Fixes:

 * **Azure AI Factory:** Fix for a broken import in Azure AI Factory.
</Update>

<Update label="2025-03-23" description="v1.1.17">
 ## 1.1.17

 ## Improvements:

 * **Better Debug Logs**: Enhanced debug logs for better readability and clarity.
</Update>

<Update label="2025-03-22" description="v1.1.16">
 ## 1.1.16

 ## New Features:

 * **Async Qdrant VectorDB:** Implemented async support for Qdrant VectorDB, improving performance and efficiency.
 * **Claude Think Tool:** Introduced the Claude **Think tool**, following the specified implementation [guide.](https://www.anthropic.com/engineering/claude-think-tool)
</Update>

<Update label="2025-03-21" description="v1.1.15">
 ## 1.1.15

 ## Improvements:

 * **Tool Result Caching:** Added caching of selected searchers and scrapers. This is only intended for testing and should greatly improve iteration speed, prevent rate limits and reduce costs (where applicable) when testing agents. Applies to:
 * DuckDuckGoTools
 * ExaTools
 * FirecrawlTools
 * GoogleSearchtools
 * HackernewsTools
 * NewspaperTools
 * Newspaper4kTools
 * Websitetools
 * YFinanceTools
 * **Show tool calls**: Improved how tool calls are displayed when `print_response` and `aprint_response` is used. They are now displayed in a separate panel different from response panel. It can also be used in conjunction in `response_model`.
</Update>

<Update label="2025-03-20" description="v1.1.14">
 ## 1.1.14 - Teams Revamp

 ## New Features:

 * **Teams Revamp**: Announcing a new iteration of Agent teams with the following features:
 * Create a `Team` in one of 3 modes: “Collaborate”, “Coordinate” or “Route”.
 * Various improvements have been made that was broken with the previous teams implementation. Including returning structured output from member agents (for “route” mode), passing images, audio and video to member agents, etc.
 * It has added features like “agentic shared context” between team members and sharing of individual team member responses with other team members.
 * This also comes with a revamp of Agent and Team debug logs. Use `debug_mode=True` and `team.print_response(...)` to see it in action.
 * Find the docs [here](https://docs.agno.com/teams/introduction). Please look at the example implementations [here](https://github.com/agno-agi/agno/blob/c8e47d1643065a0a6ee795c6b063f8576a7a2ef6/cookbook/examples/teams).
 * This is the first release. Please give us feedback. Updates and improvements will follow.
 * Support for `Agent(team=[])` is still there, but deprecated (see below).
 * **LiteLLM:** Added [LiteLLM](https://www.litellm.ai/) support, both as a native implementation and via the `OpenAILike` interface.

 ## Improvements:

 * **Change structured\_output to response\_format:** Added `use_json_mode: bool = False` as a parameter of `Agent` and `Team`, which in conjunction with `response_model=YourModel`, is used to indicate whether the agent/team model should be forced to respond in json instead of (now default) structured output. Previous behaviour defaulted to “json-mode”, but since most models now support native structured output, we are now defaulting to native structured output. It is now also much simpler to work with response models, since now only `response_model` needs to be set. It is not necessary anymore to set `structured_output=True` to specifically get structured output from the model.
 * **Website Tools + Combined Knowledgebase:** Added functionality for `WebsiteTools` to also update combined knowledgebases.

 ## Bug Fixes:

 * **AgentMemory**: Fixed `get_message_pairs()` fetching incorrect messages.
 * **UnionType in Functions**: Fixed issue with function parsing where pipe-style unions were used in function parameters.
 * **Gemini Array Function Parsing**: Fixed issue preventing gemini function parsing to work in some MCP cases.

 ## Deprecations:

 * **Structured Output:** `Agent.structured_output` has been replaced by `Agent.use_json_mode`. This will be removed in a future major version release.
 * **Agent Team:** `Agent.team` is deprecated with the release of our new Teams implementation [here](https://docs.agno.com/teams/introduction). This will be removed in a future major version release.
</Update>

<Update label="2025-03-14" description="v1.1.13">
 ## 1.1.13

 ## Improvements:

 * **OpenAIResponses File Search**: Added support for the built-in [“File Search”](https://platform.openai.com/docs/guides/tools-file-search) function from OpenAI. This automatically uploads `File` objects attached to the agent prompt.
 * **OpenAIReponses web citations**: Added support to extract URL citations after usage of the built-in “Web Search” tool from OpenAI.
 * **Anthropic document citations**: Added support to extract document citations from Claude responses when `File` objects are attached to agent prompts.
 * **Cohere Command A**: Support and examples added for Coheres new flagship model

 ## Bug Fixes:

 * **Ollama tools**: Fixed issues with tools where parameters are not typed.
 * **Anthropic Structured Output**: Fixed issue affecting Anthropic and Anthropic via Azure where structured output wouldn’t work in some cases. This should make the experience of using structured output for models that don’t natively support it better overall. Also now works with enums as types in the Pydantic model.
 * **Google Maps Places**: Support from Google for Places API has been changed and this brings it up to date so we can continue to support “search places”.
</Update>

<Update label="2025-03-13" description="v1.1.12">
 ## 1.1.12

 ## New Features:

 * **Citations**: Improved support for capturing, displaying, and storing citations from models, with integration for Gemini and Perplexity.

 ## Improvements:

 * **CalComTools**: Improvement to tool Initialization.

 ## Bug Fixes:

 * **MemoryManager**: Limit parameter was added fixing a KeyError in MongoMemoryDb.
</Update>

<Update label="2025-03-13" description="v1.1.11">
 ## 1.1.11

 ## New Features:

 * **OpenAI Responses**: Added a new model implementation that supports OpenAI’s Responses API. This includes support for their [“websearch”](https://platform.openai.com/docs/guides/tools-web-search#page-top) built-in tool.
 * **Openweather API Tool:** Added tool to get real-time weather information.

 ## Improvements:

 * **Storage Refactor:** Merged agent and workflow storage classes to align storage better for agents, teams and workflows. This change is backwards compatible and should not result in any disruptions.
</Update>

<Update label="2025-03-12" description="v1.1.10">
 ## 1.1.10

 ## New Features:

 * **File Prompts**: Introduced a new `File` type that can be added to prompts and will be sent to the model providers. Only Gemini and Anthropic Claude supported for now.
 * **LMStudio:** Added support for [LMStudio](https://lmstudio.ai/) as a model provider. See the [docs](https://docs.agno.com/models/lmstudio).
 * **AgentQL Tools**: Added tools to support [AgentQL](https://www.agentql.com/) for connecting agents to websites for scraping, etc. See the [docs](https://docs.agno.com/tools/toolkits/agentql).
 * **Browserbase Tool:** Added [Browserbase](https://www.browserbase.com/) tool.

 ## Improvements:

 * **Cohere Vision**: Added support for image understanding with Cohere models. See [this cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/models/cohere/image_agent.py) to try it out.
 * **Embedder defaults logging**: Improved logging when using the default OpenAI embedder.

 ## Bug Fixes:

 * **Ollama Embedder**: Fix for getting embeddings from Ollama across different versions.
</Update>

<Update label="2025-03-06" description="v1.1.9">
 ## 1.1.9

 ## New Features:

 * **IBM Watson X:** Added support for IBM Watson X as a model provider. Find the docs [here](https://docs.agno.com/models/ibm-watsonx).
 * **DeepInfra**: Added support for [DeepInfra](https://deepinfra.com). Find the docs [here](https://docs.agno.com/models/deepinfra).
 * **Support for MCP**: Introducing `MCPTools` along with examples for using MCP with Agno agents.

 ## Bug Fixes:

 * **Mistral with reasoning**: Fixed cases where Mistral would fail when reasoning models from other providers generated reasoning content.
</Update>

<Update label="2025-03-03" description="v1.1.8">
 ## 1.1.8

 ## New Features:

 * **Video File Upload on Playground**: You can now upload video files and have a model interpret the video. This feature is supported only by select `Gemini` models with video processing capabilities.

 ## Bug Fixes:

 * **Huggingface**: Fixed multiple issues with the `Huggingface` model integration. Tool calling is now fully supported in non-streaming cases.
 * **Gemini**: Resolved an issue with manually setting the assistant role and tool call result metrics.
 * **OllamaEmbedder**: Fixed issue where no embeddings were returned.
</Update>

<Update label="2025-02-26" description="v1.1.7">
 ## 1.1.7

 ## New Features:

 * **Audio File Upload on Playground**: You can now upload audio files and have a model interpret the audio, do sentiment analysis, provide an audio transcription, etc.

 ## Bug Fixes:

 * **Claude Thinking Streaming**: Fix Claude thinking when streaming is active, as well as for async runs.
</Update>

<Update label="2025-02-24" description="v1.1.6">
 ## 1.1.6

 ## New Features:

 -**Claude 3.7 Support:** Added support for the latest Claude 3.7 Sonnet model

 ## Bug Fixes:

 -**Claude Tool Use**: Fixed an issue where tools and content could not be used in the same block when interacting with Claude models.
</Update>

<Update label="2025-02-24" description="v1.1.5">
 ## 1.1.5

 ## New Features:

 * **Audio Responses:** Agents can now deliver audio responses (both with streaming and non-streaming).

 * The audio is in the `agent.run_response.response_audio`.

 * This only works with `OpenAIChat` with the `gpt-4o-audio-preview` model. See [their docs](https://platform.openai.com/docs/guides/audio) for more on how it works. For example

 ```python
 from agno.agent import Agent
 from agno.models.openai import OpenAIChat
 from agno.utils.audio import write_audio_to_file

 agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"], # Both text and audio responses are provided.
 audio={"voice": "alloy", "format": "wav"},
 ),
 )
 agent.print_response(
 "Tell me a 5 second story"
 )
 if agent.run_response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.base64_audio, filename=str(filename)
 )
 ```

 * See the [audio\_conversation\_agent cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/playground/audio_conversation_agent.py) to test it out on the Agent Playground.

 * **Image understanding support for [Together.ai](http://Together.ai) and XAi**: You can now give images to agents using models from XAi and Together.ai.

 ## Improvements:

 * **Automated Tests:** Added integration tests for all models. Most of these will be run on each pull request, with a suite of integration tests run before a new release is published.
 * **Grounding and Search with Gemini:** [Grounding and Search](https://ai.google.dev/gemini-api/docs/grounding?lang=python) can be used to improve the accuracy and recency of responses from the Gemini models.

 ## Bug Fixes:

 * **Structured output updates**: Fixed various cases where native structured output was not used on models.
 * **Ollama tool parsing**: Fixed cases for Ollama with tools with optional parameters.
 * **Gemini Memory Summariser**: Fixed cases where Gemini models were used as the memory summariser.
 * **Gemini auto tool calling**: Enabled automatic tool calling when tools are provided, aligning behavior with other models.
 * **FixedSizeChunking issue with overlap:** Fixed issue where chunking would fail if overlap was set.
 * **Claude tools with multiple types**: Fixed an issue where Claude tools would break when handling a union of types in parameters.
 * **JSON response parsing**: Fixed cases where JSON model responses returned quoted strings within dictionary values.
</Update>

<Update label="2025-02-17" description="v1.1.4">
 ## 1.1.4

 ## Improvements:

 * **Gmail Tools**: Added `get_emails_by_thread` and `send_email_reply` methods to `GmailTools`.

 ## Bug Fixes:

 * **Gemini List Parameters**: Fixed an issue with functions using list-type parameters in Gemini.
 * **Gemini Safety Parameters**: Fixed an issue with passing safety parameters in Gemini.
 * **ChromaDB Multiple Docs:** Fixed an issue with loading multiple documents into ChromaDB.
 * **Agentic Chunking:** Fixed an issue where OpenAI was required for chunking even when a model was provided.
</Update>

<Update label="2025-02-16" description="v1.1.3">
 ## 1.1.3

 ## Bug Fixes:

 * **Gemini Tool-Call History**: Fixed an issue where Gemini rejected tool-calls from historic messages.
</Update>

<Update label="2025-02-15" description="v1.1.2">
 ## 1.1.2

 ## Improvements:

 * **Reasoning with o3 Models**: Reasoning support added for OpenAI’s o3 models.
 * **Gemini embedder update:** Updated the `GeminiEmbedder` to use the new [Google’s genai SDK](https://github.com/googleapis/python-genai). This update introduces a slight change in the interface:

 ```python
 # Before
 embeddings = GeminiEmbedder("models/text-embedding-004").get_embedding(
 "The quick brown fox jumps over the lazy dog."
 )

 # After
 embeddings = GeminiEmbedder("text-embedding-004").get_embedding(
 "The quick brown fox jumps over the lazy dog."
 )
 ```

 ## Bug Fixes:

 * **Singlestore Fix:** Fixed an issue where querying SingleStore caused the embeddings column to return in binary format.
 * **MongoDB Vectorstore Fix:** Fixed multiple issues in MongoDB, including duplicate creation and deletion of collections during initialization. All known issues have been resolved.
 * **LanceDB Fix:** Fixed various errors in LanceDB and added on\_bad\_vectors as a parameter.
</Update>

<Update label="2025-02-14" description="v1.1.1">
 ## 1.1.1

 ## Improvements:

 * **File / Image Uploads on Agent UI:** Agent UI now supports file and image uploads with prompts.
 * Supported file formats: `.pdf` , `.csv` , `.txt` , `.docx` , `.json`
 * Supported image formats: `.png` , `.jpeg` , `.jpg` , `.webp`
 * **Firecrawl Custom API URL**: Allowed users to set a custom API URL for Firecrawl.
 * **Updated `ModelsLabTools` Toolkit Constructor**: The constructor in `/libs/agno/tools/models_labs.py` has been updated to accommodate audio generation API calls. This is a breaking change, as the parameters for the `ModelsLabTools` class have changed. The `url` and `fetch_url` parameters have been removed, and API URLs are now decided based on the `file_type` provided by the user.

 ```python
 MODELS_LAB_URLS = {
 "MP4": "https://modelslab.com/api/v6/video/text2video",
 "MP3": "https://modelslab.com/api/v6/voice/music_gen",
 "GIF": "https://modelslab.com/api/v6/video/text2video",
 }

 MODELS_LAB_FETCH_URLS = {
 "MP4": "https://modelslab.com/api/v6/video/fetch",
 "MP3": "https://modelslab.com/api/v6/voice/fetch",
 "GIF": "https://modelslab.com/api/v6/video/fetch",
 }
 ```

 The `FileType` enum now includes `MP3` type:

 ```jsx
 class FileType(str, Enum):
 MP4 = "mp4"
 GIF = "gif"
 MP3 = "mp3"
 ```

 ## Bug Fixes:

 * **Gemini functions with no parameters:** Addressed an issue where Gemini would reject function declarations with empty properties.
 * **Fix exponential memory growth**: Fixed certain cases where the agent memory would grow exponentially.
 * **Chroma DB:** Fixed various issues related to metadata on insertion and search.
 * **Gemini Structured Output**: Fixed a bug where Gemini would not generate structured output correctly.
 * **MistralEmbedder:** Fixed issue with instantiation of `MistralEmbedder`.
 * **Reasoning**: Fixed an issue with setting reasoning models.
 * **Audio Response:** Fixed an issue with streaming audio artefacts to the playground.
</Update>

<Update label="2025-02-12" description="v1.1.0">
 ## 1.1.0 - Models Refactor and Cloud Support

 ## Model Improvements:

 * **Models Refactor**: A complete overhaul of our models implementation to improve on performance and to have better feature parity across models.
 * This improves metrics and visibility on the Agent UI as well.
 * All models now support async-await, with the exception of `AwsBedrock`.
 * **Azure AI Foundry**: We now support all models on Azure AI Foundry. Learn more [here](https://learn.microsoft.com/azure/ai-services/models)..
 * **AWS Bedrock Support**: Our redone AWS Bedrock implementation now supports all Bedrock models. It is important to note [which models support which features](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html).
 * **Gemini via Google SDK**: With the 1.0.0 release of [Google's genai SDK](https://github.com/googleapis/python-genai) we could improve our previous implementation of `Gemini`. This will allow for easier integration of Gemini features in future.
 * **Model Failure Retries:** We added better error handling of third-party errors (e.g. Rate-Limit errors) and the agent will now optionally retry with exponential backoff if `exponential_backoff` is set to `True`.

 ## Other Improvements

 * **Exa Answers Support**: Added support for the [Exa answers](https://docs.exa.ai/reference/answer) capability.
 * **GoogleSearchTools**: Updated the name of `GoogleSearch` to `GoogleSearchTools` for consistency.

 ## Deprecation

 * Our `Gemini` implementation directly on the Vertex API has been replaced by the Google SDK implementation of `Gemini`.
 * Our `Gemini` implementation via the OpenAI client has been replaced by the Google SDK implementation of `Gemini`.
 * Our `OllamaHermes` has been removed as the implementation of `Ollama` was improved.

 ## Bug Fixes

 * **Team Members Names**: Fixed a bug where teams where team members have non-aphanumeric characters in their names would cause exceptions.
</Update>

<Update label="2025-02-07" description="v1.0.8">
 ## 1.0.8

 ## New Features:

 * **Perplexity Model**: We now support [Perplexity](https://www.perplexity.ai/) as a model provider.
 * **Todoist Toolkit:** Added a toolkit for managing tasks on Todoist.
 * **JSON Reader**: Added a JSON file reader for use in knowledge bases.

 ## Improvements:

 * **LanceDb**: Implemented `name_exists` function for LanceDb.

 ## Bug Fixes:

 * **Storage growth bug:** Fixed a bug with duplication of `run_messages.messages` for every run in storage.
</Update>

<Update label="2025-02-05" description="v1.0.7">
 ## 1.0.7

 ## New Features:

 * **Google Sheets Toolkit**: Added a basic toolkit for reading, creating and updating Google sheets.
 * **Weviate Vector Store**: Added support for Weviate as a vector store.

 ## Improvements:

 * **Mistral Async**: Mistral now supports async execution via `agent.arun()` and `agent.aprint_response()`.
 * **Cohere Async**: Cohere now supports async execution via `agent.arun()` and `agent.aprint_response()`.

 ## Bug Fixes:

 * **Retriever as knowledge source**: Added small fix and examples for using the custom `retriever` parameter with an agent.
</Update>

<Update label="2025-02-05" description="v1.0.6">
 ## 1.0.6

 ## New Features:

 * **Google Maps Toolkit**: Added a rich toolkit for Google Maps that includes business discovery, directions, navigation, geocode locations, nearby places, etc.
 * **URL reader and knowledge base**: Added reader and knowledge base that can process any URL and store the text contents in the document store.

 ## Bug Fixes:

 * **Zoom tools fix:** Zoom tools updated to include the auth step and other misc fixes.
 * **Github search\_repositories pagination**: Pagination did not work correctly and this was fixed.
</Update>

<Update label="2025-02-03" description="v1.0.5">
 ## 1.0.5

 ## New Features:

 * **Gmail Tools:** Add tools for Gmail, including mail search, sending mails, etc.

 ## Improvements:

 * **Exa Toolkit Upgrade:** Added `find_similar` to `ExaTools`
 * **Claude Async:** Claude models can now be used with `await agent.aprint_response()` and `await agent.arun()`.
 * **Mistral Vision:** Mistral vision models are now supported. Various examples were added to illustrate [example](https://github.com/agno-agi/agno/blob/main/cookbook/models/mistral/image_file_input_agent.py).
</Update>

<Update label="2025-02-02" description="v1.0.4">
 ## 1.0.4

 ## Bug Fixes:

 * **Claude Tool Invocation:** Fixed issue where Claude was not working with tools that have no parameters.
</Update>

<Update label="2025-01-31" description="v1.0.3">
 ## 1.0.3

 ## Improvements:

 * **OpenAI Reasoning Parameter:** Added a reasoning parameter to OpenAI models.
</Update>

<Update label="2025-01-31" description="v1.0.2">
 ## 1.0.2

 ## Improvements:

 * **Model Client Caching:** Made all models cache the client instantiation, improving Agno agent instantiation time
 * **XTools:** Renamed `TwitterTools` to `XTools` and updated capabilities to be compatible with Twitter API v2.

 ## Bug Fixes:

 * **Agent Dataclass Compatibility:** Removed `slots=True` from the agent dataclass decorator, which was not compatible with Python \< 3.10.
 * **AzureOpenAIEmbedder:** Made `AzureOpenAIEmbedder` a dataclass to match other embedders.
</Update>

<Update label="2025-01-31" description="v1.0.1">
 ## 1.0.1

 ## Improvement:

 * **Mistral Model Caching:** Enabled caching for Mistral models.
</Update>

<Update label="2025-01-30" description="v1.0.0">
 ## 1.0.0 - Agno

 This is the major refactor from `phidata` to `agno`, released with the official launch of Agno AI.

 See the [migration guide](../how-to/phidata-to-agno) for additional guidance.

 ## Interface Changes:

 * `phi.model.x` → `agno.models.x`

 * `phi.knowledge_base.x` → `agno.knowledge.x` (applies to all knowledge bases)

 * `phi.document.reader.xxx` → `agno.document.reader.xxx_reader` (applies to all document readers)

 * All Agno toolkits are now suffixed with `Tools`. E.g. `DuckDuckGo` → `DuckDuckGoTools`

 * Multi-modal interface updates:

 * `agent.run(images=[])` and `agent.print_response(images=[])` is now of type `Image`

 ```python
 class Image(BaseModel):
 url: Optional[str] = None # Remote location for image
 filepath: Optional[Union[Path, str]] = None # Absolute local location for image
 content: Optional[Any] = None # Actual image bytes content
 detail: Optional[str] = None # low, medium, high or auto (per OpenAI spec https://platform.openai.com/docs/guides/vision?lang=node#low-or-high-fidelity-image-understanding)
 id: Optional[str] = None
 ```

 * `agent.run(audio=[])` and `agent.print_response(audio=[])` is now of type `Audio`

 ```python
 class Audio(BaseModel):
 filepath: Optional[Union[Path, str]] = None # Absolute local location for audio
 content: Optional[Any] = None # Actual audio bytes content
 format: Optional[str] = None
 ```

 * `agent.run(video=[])` and `agent.print_response(video=[])` is now of type `Video`

 ```python
 class Video(BaseModel):
 filepath: Optional[Union[Path, str]] = None # Absolute local location for video
 content: Optional[Any] = None # Actual video bytes content
 ```

 * `RunResponse.images` is now a list of type `ImageArtifact`

 ```python
 class ImageArtifact(Media):
 id: str
 url: str # Remote location for file
 alt_text: Optional[str] = None
 ```

 * `RunResponse.audio` is now a list of type `AudioArtifact`

 ```python
 class AudioArtifact(Media):
 id: str
 url: Optional[str] = None # Remote location for file
 base64_audio: Optional[str] = None # Base64-encoded audio data
 length: Optional[str] = None
 mime_type: Optional[str] = None
 ```

 * `RunResponse.videos` is now a list of type `VideoArtifact`

 ```python
 class VideoArtifact(Media):
 id: str
 url: str # Remote location for file
 eta: Optional[str] = None
 length: Optional[str] = None
 ```

 * `RunResponse.response_audio` is now of type `AudioOutput`

 ```python
 class AudioOutput(BaseModel):
 id: str
 content: str # Base64 encoded
 expires_at: int
 transcript: str
 ```

 * Models:
 * `Hermes` → `OllamaHermes`
 * `AzureOpenAIChat` → `AzureOpenAI`
 * `CohereChat` → `Cohere`
 * `DeepSeekChat` → `DeepSeek`
 * `GeminiOpenAIChat` → `GeminiOpenAI`
 * `HuggingFaceChat` → `HuggingFace`

 * Embedders now all take `id` instead of `model` as a parameter. For example

 ```python
 db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

 knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=OllamaEmbedder(id="llama3.2", dimensions=3072),
 ),
 )
 knowledge_base.load(recreate=True)
 ```

 * Agent Storage class
 * `PgAgentStorage` → `PostgresDbAgentStorage`
 * `SqlAgentStorage` → `SqliteDbAgentStorage`
 * `MongoAgentStorage` → `MongoDbAgentStorage`
 * `S2AgentStorage` → `SingleStoreDbAgentStorage`

 * Workflow Storage class
 * `SqlWorkflowStorage` → `SqliteDbWorkflowStorage`
 * `PgWorkflowStorage` → `PostgresDbWorkflowStorage`
 * `MongoWorkflowStorage` → `MongoDbWorkflowStorage`

 * Knowledge Base
 * `phi.knowledge.pdf.PDFUrlKnowledgeBase` → `agno.knowledge.pdf_url.PDFUrlKnowledgeBase`
 * `phi.knowledge.csv.CSVUrlKnowledgeBase` → `agno.knowledge.csv_url.CSVUrlKnowledgeBase`

 * Readers
 * `phi.document.reader.arxiv` → `agno.document.reader.arxiv_reader`
 * `phi.document.reader.docx` → `agno.document.reader.docx_reader`
 * `phi.document.reader.json` → `agno.document.reader.json_reader`
 * `phi.document.reader.pdf` → `agno.document.reader.pdf_reader`
 * `phi.document.reader.s3.pdf` → `agno.document.reader.s3.pdf_reader`
 * `phi.document.reader.s3.text` → `agno.document.reader.s3.text_reader`
 * `phi.document.reader.text` → `agno.document.reader.text_reader`
 * `phi.document.reader.website` → `agno.document.reader.website_reader`

 ## Improvements:

 * **Dataclasses:** Changed various instances of Pydantic models to dataclasses to improve the speed.
 * Moved `Embedder` class from pydantic to data class

 ## Removals

 * Removed all references to `Assistant`
 * Removed all references to `llm`
 * Removed the `PhiTools` tool
 * On the `Agent` class, `guidelines`, `prevent_hallucinations`, `prevent_prompt_leakage`, `limit_tool_access`, and `task` has been removed. They can be incorporated into the `instructions` parameter as you see fit.

 ## Bug Fixes:

 * **Semantic Chunking:** Fixed semantic chunking by replacing `similarity_threshold` param with `threshold` param.

 ## New Features:

 * **Evals for Agents:** Introducing Evals to measure the performance, accuracy, and reliability of your Agents.
</Update>

# Agentic Chunking
Source: https://docs.agno.com/chunking/agentic-chunking

Agentic chunking is an intelligent method of splitting documents into smaller chunks by using a model to determine natural breakpoints in the text. Rather than splitting text at fixed character counts, it analyzes the content to find semantically meaningful boundaries like paragraph breaks and topic transitions.

## Usage

```python
from agno.agent import Agent
from agno.document.chunking.agentic import AgenticChunking
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes_agentic_chunking", db_url=db_url),
 chunking_strategy=AgenticChunking(),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 knowledge_base=knowledge_base,
 search_knowledge=True,
)

agent.print_response("How to make Thai curry?", markdown=True)
```

## Agentic Chunking Params

<Snippet file="chunking-agentic.mdx" />

# Document Chunking
Source: https://docs.agno.com/chunking/document-chunking

Document chunking is a method of splitting documents into smaller chunks based on document structure like paragraphs and sections. It analyzes natural document boundaries rather than splitting at fixed character counts. This is useful when you want to process large documents while preserving semantic meaning and context.

## Usage

```python
from agno.agent import Agent
from agno.document.chunking.document import DocumentChunking
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes_document_chunking", db_url=db_url),
 chunking_strategy=DocumentChunking(),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 knowledge_base=knowledge_base,
 search_knowledge=True,
)

agent.print_response("How to make Thai curry?", markdown=True)

```

## Document Chunking Params

<Snippet file="chunking-document.mdx" />

# Fixed Size Chunking
Source: https://docs.agno.com/chunking/fixed-size-chunking

Fixed size chunking is a method of splitting documents into smaller chunks of a specified size, with optional overlap between chunks. This is useful when you want to process large documents in smaller, manageable pieces.

## Usage

```python
from agno.agent import Agent
from agno.document.chunking.fixed import FixedSizeChunking
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes_fixed_size_chunking", db_url=db_url),
 chunking_strategy=FixedSizeChunking(),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 knowledge_base=knowledge_base,
 search_knowledge=True,
)

agent.print_response("How to make Thai curry?", markdown=True)
```

## Fixed Size Chunking Params

<Snippet file="chunking-fixed-size.mdx" />

# Recursive Chunking
Source: https://docs.agno.com/chunking/recursive-chunking

Recursive chunking is a method of splitting documents into smaller chunks by recursively applying a chunking strategy. This is useful when you want to process large documents in smaller, manageable pieces.

```python
from agno.agent import Agent
from agno.document.chunking.recursive import RecursiveChunking
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes_recursive_chunking", db_url=db_url),
 chunking_strategy=RecursiveChunking(),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 knowledge_base=knowledge_base,
 search_knowledge=True,
)

agent.print_response("How to make Thai curry?", markdown=True)

```

## Recursive Chunking Params

<Snippet file="chunking-recursive.mdx" />

# Semantic Chunking
Source: https://docs.agno.com/chunking/semantic-chunking

Semantic chunking is a method of splitting documents into smaller chunks by analyzing semantic similarity between text segments using embeddings. It uses the chonkie library to identify natural breakpoints where the semantic meaning changes significantly, based on a configurable similarity threshold. This helps preserve context and meaning better than fixed-size chunking by ensuring semantically related content stays together in the same chunk, while splitting occurs at meaningful topic transitions.

```python
from agno.agent import Agent
from agno.document.chunking.semantic import SemanticChunking
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes_semantic_chunking", db_url=db_url),
 chunking_strategy=SemanticChunking(),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 knowledge_base=knowledge_base,
 search_knowledge=True,
)

agent.print_response("How to make Thai curry?", markdown=True)

```

## Semantic Chunking Params

<Snippet file="chunking-semantic.mdx" />

# AWS Bedrock Embedder
Source: https://docs.agno.com/embedder/aws_bedrock

The `AwsBedrockEmbedder` class is used to embed text data into vectors using the AWS Bedrock API. By default, it uses the Cohere Embed Multilingual V3 model for generating embeddings.

# Setup

## Set your AWS credentials

```bash
export AWS_ACCESS_KEY_ID = xxx
export AWS_SECRET_ACCESS_KEY = xxx
export AWS_REGION = xxx
```

<Note>
 By default, this embedder uses the `cohere.embed-multilingual-v3` model. You must enable access to this model from the AWS Bedrock model catalog before using this embedder.
</Note>

## Run PgVector

```bash
docker run - d \
 - e POSTGRES_DB = ai \
 - e POSTGRES_USER = ai \
 - e POSTGRES_PASSWORD = ai \
 - e PGDATA = /var/lib/postgresql/data/pgdata \
 - v pgvolume: / var/lib/postgresql/data \
 - p 5532: 5432 \
 - -name pgvector \
 agnohq/pgvector: 16
```

# Usage

```python cookbook/embedders/aws_bedrock_embedder.py

# Embed sentence in database
embeddings = AwsBedrockEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)
# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage with a PDF knowledge base
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 reader=PDFUrlReader(
 chunk_size=2048
 ), # Required because Cohere model has a fixed size of 2048
 vector_db=PgVector(
 table_name="recipes",
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 embedder=AwsBedrockEmbedder(),
 ),
)
knowledge_base.load(recreate=False)
```

# Params

| Parameter | Type | Default | Description |
| ----------------------- | -------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `id` | `str` | `"cohere.embed-multilingual-v3"` | The model ID to use. You need to enable this model in your AWS Bedrock model catalog. |
| `dimensions` | `int` | `1024` | The dimensionality of the embeddings generated by the model(1024 for Cohere models). |
| `input_type` | `str` | `"search_query"` | Prepends special tokens to differentiate types. Options: 'search\_document', 'search\_query', 'classification', 'clustering'. |
| `truncate` | `Optional[str]` | `None` | How to handle inputs longer than the maximum token length. Options: 'NONE', 'START', 'END'. |
| `embedding_types` | `Optional[List[str]]` | `None` | Types of embeddings to return . Options: 'float', 'int8', 'uint8', 'binary', 'ubinary'. |
| `aws_region` | `Optional[str]` | `None` | The AWS region to use. If not provided, falls back to AWS\_REGION env variable. |
| `aws_access_key_id` | `Optional[str]` | `None` | The AWS access key ID. If not provided, falls back to AWS\_ACCESS\_KEY\_ID env variable. |
| `aws_secret_access_key` | `Optional[str]` | `None` | The AWS secret access key. If not provided, falls back to AWS\_SECRET\_ACCESS\_KEY env variable. |
| `session` | `Optional[Session]` | `None` | A boto3 Session object to use for authentication. |
| `request_params` | `Optional[Dict[str, Any]]` | `None` | Additional parameters to pass to the API requests. |
| `client_params` | `Optional[Dict[str, Any]]` | `None` | Additional parameters to pass to the boto3 client. |
| `client` | `Optional[AwsClient]` | `None` | An instance of the AWS Bedrock client to use for making API requests. |

# Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/aws_bedrock_embedder.py)

# Azure OpenAI Embedder
Source: https://docs.agno.com/embedder/azure_openai

The `AzureOpenAIEmbedder` class is used to embed text data into vectors using the Azure OpenAI API. Get your key from [here](https://ai.azure.com/).

## Setup

### Set your API keys

```bash
export AZURE_EMBEDDER_OPENAI_API_KEY=xxx
export AZURE_EMBEDDER_OPENAI_ENDPOINT=xxx
export AZURE_EMBEDDER_DEPLOYMENT=xxx
```

### Run PgVector

```bash
docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
```

## Usage

```python cookbook/embedders/azure_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.azure_openai import AzureOpenAIEmbedder

# Embed sentence in database
embeddings = AzureOpenAIEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="azure_openai_embeddings",
 embedder=AzureOpenAIEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ------------------------- | ----------------------------- | -------------------------- | -------------------------------------------------------------------------------- |
| `model` | `str` | `"text-embedding-ada-002"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `1536` | The dimensionality of the embeddings generated by the model. |
| `encoding_format` | `Literal['float', 'base64']` | `"float"` | The format in which the embeddings are encoded. Options are "float" or "base64". |
| `user` | `str` | - | The user associated with the API request. |
| `api_key` | `str` | - | The API key used for authenticating requests. |
| `api_version` | `str` | `"2024-02-01"` | The version of the API to use for the requests. |
| `azure_endpoint` | `str` | - | The Azure endpoint for the API requests. |
| `azure_deployment` | `str` | - | The Azure deployment name for the API requests. |
| `base_url` | `str` | - | The base URL for the API endpoint. |
| `azure_ad_token` | `str` | - | The Azure Active Directory token for authentication. |
| `azure_ad_token_provider` | `Any` | - | The provider for obtaining the Azure AD token. |
| `organization` | `str` | - | The organization associated with the API request. |
| `request_params` | `Optional[Dict[str, Any]]` | - | Additional parameters to include in the API request. Optional. |
| `client_params` | `Optional[Dict[str, Any]]` | - | Additional parameters for configuring the API client. Optional. |
| `openai_client` | `Optional[AzureOpenAIClient]` | - | An instance of the AzureOpenAIClient to use for making API requests. Optional. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/azure_embedder.py)

# Cohere Embedder
Source: https://docs.agno.com/embedder/cohere

The `CohereEmbedder` class is used to embed text data into vectors using the Cohere API. You can get started with Cohere from [here](https://docs.cohere.com/reference/about)

Get your key from [here](https://dashboard.cohere.com/api-keys).

## Usage

```python cookbook/embedders/cohere_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.cohere import CohereEmbedder

# Add embedding to database
embeddings = CohereEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")
# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="cohere_embeddings",
 embedder=CohereEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ----------------- | -------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `model` | `str` | `"embed-english-v3.0"` | The name of the model used for generating embeddings. |
| `input_type` | `str` | `search_query` | The type of input to embed. You can find more details [here](https://docs.cohere.com/docs/embeddings#the-input_type-parameter) |
| `embedding_types` | `Optional[List[str]]` | - | The type of embeddings to generate. Optional. |
| `api_key` | `str` | - | The Cohere API key used for authenticating requests. |
| `request_params` | `Optional[Dict[str, Any]]` | - | Additional parameters to include in the API request. Optional. |
| `client_params` | `Optional[Dict[str, Any]]` | - | Additional parameters for configuring the API client. Optional. |
| `cohere_client` | `Optional[CohereClient]` | - | An instance of the CohereClient to use for making API requests. Optional. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/cohere_embedder.py)

# Fireworks Embedder
Source: https://docs.agno.com/embedder/fireworks

The `FireworksEmbedder` can be used to embed text data into vectors using the Fireworks API. Fireworks uses the OpenAI API specification, so the `FireworksEmbedder` class is similar to the `OpenAIEmbedder` class, incorporating adjustments to ensure compatibility with the Fireworks platform. Get your key from [here](https://fireworks.ai/account/api-keys).

## Usage

```python cookbook/embedders/fireworks_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.fireworks import FireworksEmbedder

# Embed sentence in database
embeddings = FireworksEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="fireworks_embeddings",
 embedder=FireworksEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ------------ | ----- | ----------------------------------------- | ------------------------------------------------------------ |
| `model` | `str` | `"nomic-ai/nomic-embed-text-v1.5"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `768` | The dimensionality of the embeddings generated by the model. |
| `api_key` | `str` | - | The API key used for authenticating requests. |
| `base_url` | `str` | `"https://api.fireworks.ai/inference/v1"` | The base URL for the API endpoint. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/fireworks_embedder.py)

# Gemini Embedder
Source: https://docs.agno.com/embedder/gemini

The `GeminiEmbedder` class is used to embed text data into vectors using the Gemini API. You can get one from [here](https://ai.google.dev/aistudio).

## Usage

```python cookbook/embedders/gemini_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.google import GeminiEmbedder

# Embed sentence in database
embeddings = GeminiEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="gemini_embeddings",
 embedder=GeminiEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ---------------- | -------------------------- | --------------------------- | ----------------------------------------------------------- |
| `dimensions` | `int` | `768` | The dimensionality of the generated embeddings |
| `model` | `str` | `models/text-embedding-004` | The name of the Gemini model to use |
| `task_type` | `str` | - | The type of task for which embeddings are being generated |
| `title` | `str` | - | Optional title for the embedding task |
| `api_key` | `str` | - | The API key used for authenticating requests. |
| `request_params` | `Optional[Dict[str, Any]]` | - | Optional dictionary of parameters for the embedding request |
| `client_params` | `Optional[Dict[str, Any]]` | - | Optional dictionary of parameters for the Gemini client |
| `gemini_client` | `Optional[Client]` | - | Optional pre-configured Gemini client instance |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/gemini_embedder.py)

# HuggingFace Embedder
Source: https://docs.agno.com/embedder/huggingface

The `HuggingfaceCustomEmbedder` class is used to embed text data into vectors using the Hugging Face API. You can get one from [here](https://huggingface.co/settings/tokens).

## Usage

```python cookbook/embedders/huggingface_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.huggingface import HuggingfaceCustomEmbedder

# Embed sentence in database
embeddings = HuggingfaceCustomEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="huggingface_embeddings",
 embedder=HuggingfaceCustomEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| -------------------- | -------------------------- | ------------------ | ------------------------------------------------------------ |
| `dimensions` | `int` | - | The dimensionality of the generated embeddings |
| `model` | `str` | `all-MiniLM-L6-v2` | The name of the HuggingFace model to use |
| `api_key` | `str` | - | The API key used for authenticating requests |
| `client_params` | `Optional[Dict[str, Any]]` | - | Optional dictionary of parameters for the HuggingFace client |
| `huggingface_client` | `Any` | - | Optional pre-configured HuggingFace client instance |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/huggingface_embedder.py)

# What are Embedders?
Source: https://docs.agno.com/embedder/introduction

Learn how to use embedders with Agno to convert complex information into vector representations.

An Embedder converts complex information into vector representations, allowing it to be stored in a vector database. By transforming data into embeddings, the embedder enables efficient searching and retrieval of contextually relevant information. This process enhances the responses of language models by providing them with the necessary business context, ensuring they are context-aware. Agno uses the `OpenAIEmbedder` as the default embedder, but other embedders are supported as well. Here is an example:

```python
from agno.agent import Agent, AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.openai import OpenAIEmbedder

# Create knowledge base
knowledge_base=AgentKnowledge(
 vector_db=PgVector(
 db_url=db_url,
 table_name=embeddings_table,
 embedder=OpenAIEmbedder(),
 ),
 # 2 references are added to the prompt
 num_documents=2,
),

# Add information to the knowledge base
knowledge_base.load_text("The sky is blue")

# Add the knowledge base to the Agent
agent = Agent(knowledge_base=knowledge_base)
```

The following embedders are supported:

* [OpenAI](/embedder/openai)
* [Gemini](/embedder/gemini)
* [Ollama](/embedder/ollama)
* [Voyage AI](/embedder/voyageai)
* [Azure OpenAI](/embedder/azure_openai)
* [Mistral](/embedder/mistral)
* [Fireworks](/embedder/fireworks)
* [Together](/embedder/together)
* [HuggingFace](/embedder/huggingface)
* [Qdrant FastEmbed](/embedder/qdrant_fastembed)

# Mistral Embedder
Source: https://docs.agno.com/embedder/mistral

The `MistralEmbedder` class is used to embed text data into vectors using the Mistral API. Get your key from [here](https://console.mistral.ai/api-keys/).

## Usage

```python cookbook/embedders/mistral_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.mistral import MistralEmbedder

# Embed sentence in database
embeddings = MistralEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="mistral_embeddings",
 embedder=MistralEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ---------------- | -------------------------- | ----------------- | -------------------------------------------------------------------------- |
| `model` | `str` | `"mistral-embed"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `1024` | The dimensionality of the embeddings generated by the model. |
| `request_params` | `Optional[Dict[str, Any]]` | - | Additional parameters to include in the API request. Optional. |
| `api_key` | `str` | - | The API key used for authenticating requests. |
| `endpoint` | `str` | - | The endpoint URL for the API requests. |
| `max_retries` | `Optional[int]` | - | The maximum number of retries for API requests. Optional. |
| `timeout` | `Optional[int]` | - | The timeout duration for API requests. Optional. |
| `client_params` | `Optional[Dict[str, Any]]` | - | Additional parameters for configuring the API client. Optional. |
| `mistral_client` | `Optional[MistralClient]` | - | An instance of the MistralClient to use for making API requests. Optional. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/mistral_embedder.py)

# Ollama Embedder
Source: https://docs.agno.com/embedder/ollama

The `OllamaEmbedder` can be used to embed text data into vectors locally using Ollama.

<Note>The model used for generating embeddings needs to run locally. In this case it is `openhermes` so you have to [install `ollama`](https://ollama.com/download) and run `ollama pull openhermes` in your terminal.</Note>

## Usage

```python cookbook/embedders/ollama_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.ollama import OllamaEmbedder

# Embed sentence in database
embeddings = OllamaEmbedder(id="openhermes").get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="ollama_embeddings",
 embedder=OllamaEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| --------------- | -------------------------- | -------------- | ------------------------------------------------------------------------- |
| `model` | `str` | `"openhermes"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `4096` | The dimensionality of the embeddings generated by the model. |
| `host` | `str` | - | The host address for the API endpoint. |
| `timeout` | `Any` | - | The timeout duration for API requests. |
| `options` | `Any` | - | Additional options for configuring the API request. |
| `client_kwargs` | `Optional[Dict[str, Any]]` | - | Additional keyword arguments for configuring the API client. Optional. |
| `ollama_client` | `Optional[OllamaClient]` | - | An instance of the OllamaClient to use for making API requests. Optional. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/ollama_embedder.py)

# OpenAI Embedder
Source: https://docs.agno.com/embedder/openai

Agno uses the `OpenAIEmbedder` as the default embeder for the vector database. The `OpenAIEmbedder` class is used to embed text data into vectors using the OpenAI API. Get your key from [here](https://platform.openai.com/api-keys).

## Usage

```python cookbook/embedders/openai_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.openai import OpenAIEmbedder

# Embed sentence in database
embeddings = OpenAIEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="openai_embeddings",
 embedder=OpenAIEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ----------------- | ---------------------------- | -------------------------- | -------------------------------------------------------------------------------- |
| `model` | `str` | `"text-embedding-ada-002"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `1536` | The dimensionality of the embeddings generated by the model. |
| `encoding_format` | `Literal['float', 'base64']` | `"float"` | The format in which the embeddings are encoded. Options are "float" or "base64". |
| `user` | `str` | - | The user associated with the API request. |
| `api_key` | `str` | - | The API key used for authenticating requests. |
| `organization` | `str` | - | The organization associated with the API request. |
| `base_url` | `str` | - | The base URL for the API endpoint. |
| `request_params` | `Optional[Dict[str, Any]]` | - | Additional parameters to include in the API request. |
| `client_params` | `Optional[Dict[str, Any]]` | - | Additional parameters for configuring the API client. |
| `openai_client` | `Optional[OpenAIClient]` | - | An instance of the OpenAIClient to use for making API requests. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/openai_embedder.py)

# Qdrant FastEmbed Embedder
Source: https://docs.agno.com/embedder/qdrant_fastembed

The `FastEmbedEmbedder` class is used to embed text data into vectors using the [FastEmbed](https://qdrant.github.io/fastembed/).

## Usage

```python cookbook/embedders/qdrant_fastembed.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.fastembed import FastEmbedEmbedder

# Embed sentence in database
embeddings = FastEmbedEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="qdrant_embeddings",
 embedder=FastEmbedEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ------------ | ----- | ------------------------ | ---------------------------------------------- |
| `dimensions` | `int` | - | The dimensionality of the generated embeddings |
| `model` | `str` | `BAAI/bge-small-en-v1.5` | The name of the qdrant\_fastembed model to use |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/qdrant_fastembed.py)

# SentenceTransformers Embedder
Source: https://docs.agno.com/embedder/sentencetransformers

The `SentenceTransformerEmbedder` class is used to embed text data into vectors using the [SentenceTransformers](https://www.sbert.net/) library.

## Usage

```python cookbook/embedders/sentence_transformer_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.sentence_transformer import SentenceTransformerEmbedder

# Embed sentence in database
embeddings = SentenceTransformerEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="sentence_transformer_embeddings",
 embedder=SentenceTransformerEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ----------------------------- | ------------------ | ------------------- | ------------------------------------------------------------ |
| `dimensions` | `int` | - | The dimensionality of the generated embeddings |
| `model` | `str` | `all-mpnet-base-v2` | The name of the SentenceTransformers model to use |
| `sentence_transformer_client` | `Optional[Client]` | - | Optional pre-configured SentenceTransformers client instance |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/sentence_transformer_embedder.py)

# Together Embedder
Source: https://docs.agno.com/embedder/together

The `TogetherEmbedder` can be used to embed text data into vectors using the Together API. Together uses the OpenAI API specification, so the `TogetherEmbedder` class is similar to the `OpenAIEmbedder` class, incorporating adjustments to ensure compatibility with the Together platform. Get your key from [here](https://api.together.xyz/settings/api-keys).

## Usage

```python cookbook/embedders/together_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.together import TogetherEmbedder

# Embed sentence in database
embeddings = TogetherEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="together_embeddings",
 embedder=TogetherEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ------------ | ----- | ---------------------------------------- | ------------------------------------------------------------ |
| `model` | `str` | `"nomic-ai/nomic-embed-text-v1.5"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `768` | The dimensionality of the embeddings generated by the model. |
| `api_key` | `str` | | The API key used for authenticating requests. |
| `base_url` | `str` | `"https://api.Together.ai/inference/v1"` | The base URL for the API endpoint. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/together_embedder.py)

# Voyage AI Embedder
Source: https://docs.agno.com/embedder/voyageai

The `VoyageAIEmbedder` class is used to embed text data into vectors using the Voyage AI API. Get your key from [here](https://dash.voyageai.com/api-keys).

## Usage

```python cookbook/embedders/voyageai_embedder.py
from agno.agent import AgentKnowledge
from agno.vectordb.pgvector import PgVector
from agno.embedder.voyageai import VoyageAIEmbedder

# Embed sentence in database
embeddings = VoyageAIEmbedder().get_embedding("The quick brown fox jumps over the lazy dog.")

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Use an embedder in a knowledge base
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="voyageai_embeddings",
 embedder=VoyageAIEmbedder(),
 ),
 num_documents=2,
)
```

## Params

| Parameter | Type | Default | Description |
| ---------------- | -------------------------- | ------------------------------------------ | ------------------------------------------------------------------- |
| `model` | `str` | `"voyage-2"` | The name of the model used for generating embeddings. |
| `dimensions` | `int` | `1024` | The dimensionality of the embeddings generated by the model. |
| `request_params` | `Optional[Dict[str, Any]]` | - | Additional parameters to include in the API request. Optional. |
| `api_key` | `str` | - | The API key used for authenticating requests. |
| `base_url` | `str` | `"https://api.voyageai.com/v1/embeddings"` | The base URL for the API endpoint. |
| `max_retries` | `Optional[int]` | - | The maximum number of retries for API requests. Optional. |
| `timeout` | `Optional[float]` | - | The timeout duration for API requests. Optional. |
| `client_params` | `Optional[Dict[str, Any]]` | - | Additional parameters for configuring the API client. Optional. |
| `voyage_client` | `Optional[Client]` | - | An instance of the Client to use for making API requests. Optional. |

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/agent_concepts/knowledge/embedders/voyageai_embedder.py)

# Simple Agent Evals
Source: https://docs.agno.com/evals/introduction

Learn how to evaluate your Agno Agents and Teams across three key dimensions - accuracy (using LLM-as-a-judge), performance (runtime and memory), and reliability (tool calls).

**Evals** are unit tests for your Agents and Teams, use them judiciously to measure and improve their performance. Agno provides 3 dimensions for evaluating Agents:

* **Accuracy:** How complete/correct/accurate is the Agent's response (LLM-as-a-judge)
* **Performance:** How fast does the Agent respond and what's the memory footprint?
* **Reliability:** Does the Agent make the expected tool calls?

## Accuracy

Accuracy evals use input/output pairs to measure your Agents and Teams performance against a gold-standard answer. Use a larger model to score the Agent's responses (LLM-as-a-judge).

#### Example

In this example, the `AccuracyEval` will run the Agent with the input, then use a larger model (`o4-mini`) to score the Agent's response according to the guidelines provided.

```python calculate_accuracy.py
from typing import Optional
from agno.agent import Agent
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools

evaluation = AccuracyEval(
 model=OpenAIChat(id="o4-mini"),
 agent=Agent(model=OpenAIChat(id="gpt-4o"), tools=[CalculatorTools(enable_all=True)]),
 input="What is 10*5 then to the power of 2? do it step by step",
 expected_output="2500",
 additional_guidelines="Agent output should include the steps and the final answer.",
)

result: Optional[AccuracyResult] = evaluation.run(print_results=True)
assert result is not None and result.avg_score >= 8
```

<Frame>
 <img height="200" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/images/accuracy-eval-result.png" style={{ borderRadius: '8px' }} />
</Frame>

You can also run the `AccuracyEval` on an existing output (without running the Agent).

```python accuracy_eval_with_output.py
from typing import Optional

from agno.agent import Agent
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools

evaluation = AccuracyEval(
 model=OpenAIChat(id="o4-mini"),
 input="What is 10*5 then to the power of 2? do it step by step",
 expected_output="2500",
 num_iterations=1,
)
result_with_given_answer: Optional[AccuracyResult] = evaluation.run_with_output(
 output="2500", print_results=True
)
assert result_with_given_answer is not None and result_with_given_answer.avg_score >= 8
```

## Performance

Performance evals measure the latency and memory footprint of an Agent or Team.

<Note>
 While latency will be dominated by the model API response time, we should still keep performance top of mind and track the Agent or Team's performance with and without certain components. Eg: it would be good to know what's the average latency with and without storage, memory, with a new prompt, or with a new model.
</Note>

#### Example

```python storage_performance.py
"""Run `pip install openai agno` to install dependencies."""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.eval.perf import PerfEval

def simple_response():
 agent = Agent(model=OpenAIChat(id='gpt-4o-mini'), system_message='Be concise, reply with one sentence.', add_history_to_messages=True)
 response_1 = agent.run('What is the capital of France?')
 print(response_1.content)
 response_2 = agent.run('How many people live there?')
 print(response_2.content)
 return response_2.content

simple_response_perf = PerfEval(func=simple_response, num_iterations=1, warmup_runs=0)

if __name__ == "__main__":
 simple_response_perf.run(print_results=True)
```

## Reliability

What makes an Agent or Team reliable?

* Does it make the expected tool calls?
* Does it handle errors gracefully?
* Does it respect the rate limits of the model API?

#### Example

The first check is to ensure the Agent makes the expected tool calls. Here's an example:

```python reliability.py
from typing import Optional

from agno.agent import Agent
from agno.eval.reliability import ReliabilityEval, ReliabilityResult
from agno.tools.calculator import CalculatorTools
from agno.models.openai import OpenAIChat
from agno.run.response import RunResponse

def multiply_and_exponentiate():

 agent=Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[CalculatorTools(add=True, multiply=True, exponentiate=True)],
 )
 response: RunResponse = agent.run("What is 10*5 then to the power of 2? do it step by step")
 evaluation = ReliabilityEval(
 agent_response=response,
 expected_tool_calls=["multiply", "exponentiate"],
 )
 result: Optional[ReliabilityResult] = evaluation.run(print_results=True)
 result.assert_passed()

if __name__ == "__main__":
 multiply_and_exponentiate()
```

<Note>
 Reliability evals are currently in `beta`.
</Note>

# Evals on the Agno platform
Source: https://docs.agno.com/evals/platform

You can track your evaluation runs on the Agno platform

<img height="200" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/images/accuracy-eval-on-platform.png" style={{ borderRadius: "8px" }} />

## Track your evaluations

Apart from running your evaluations on the CLI, you can also track them on the Agno platform. This is useful to keep track of results and share them with your team.
Do it following these steps:

<Steps>
 <Step title="Authenticate">
 You can authenticate using your CLI or API key.

 **Using your CLI:**

 ```bash
 ag setup
 ```

 **Using your API key:**

 Get your API key from [Agno App](https://app.agno.com/settings) and use it to link your locally running agents to the Agno platform.

 ```bash
 export AGNO_API_KEY=your_api_key_here
 ```
 </Step>

 <Step title="Track your evaluations">
 When running an evaluation, set `monitoring=True` to track all its runs on the Agno platform:

 ```python
 from agno.agent import Agent
 from agno.eval.accuracy import AccuracyEval
 from agno.models.openai import OpenAIChat

 evaluation = AccuracyEval(
 model=OpenAIChat(id="gpt-4o"),
 agent=Agent(model=OpenAIChat(id="gpt-4o")),
 input="What is 10*5 then to the power of 2? do it step by step",
 expected_output="2500",
 monitoring=True, # This activates monitoring
 )

 # This run will be tracked on the Agno platform
 result = evaluation.run(print_results=True)
 ```

 You can also set the `AGNO_MONITOR` environment variable to `true` to track all evaluation runs.
 </Step>

 <Step title="View your evaluations">
 You can now view your evaluations on the Agno platform at [app.agno.com/evaluations](https://app.agno.com/evaluations).
 </Step>
</Steps>

<Info>Facing issues? Check out our [troubleshooting guide](/faq/cli-auth)</Info>

# Books Recommender
Source: https://docs.agno.com/examples/agents/books-recommender

This example shows how to create an intelligent book recommendation system that provides
comprehensive literary suggestions based on your preferences. The agent combines book databases,
ratings, reviews, and upcoming releases to deliver personalized reading recommendations.

Example prompts to try:

* "I loved 'The Seven Husbands of Evelyn Hugo' and 'Daisy Jones & The Six', what should I read next?"
* "Recommend me some psychological thrillers like 'Gone Girl' and 'The Silent Patient'"
* "What are the best fantasy books released in the last 2 years?"
* "I enjoy historical fiction with strong female leads, any suggestions?"
* "Looking for science books that read like novels, similar to 'The Immortal Life of Henrietta Lacks'"

## Code

```python books_recommender.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

book_recommendation_agent = Agent(
 name="Shelfie",
 tools=[ExaTools()],
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are Shelfie, a passionate and knowledgeable literary curator with expertise in books worldwide! 📚

 Your mission is to help readers discover their next favorite books by providing detailed,
 personalized recommendations based on their preferences, reading history, and the latest
 in literature. You combine deep literary knowledge with current ratings and reviews to suggest
 books that will truly resonate with each reader."""),
 instructions=dedent("""\
 Approach each recommendation with these steps:

 1. Analysis Phase 📖
 - Understand reader preferences from their input
 - Consider mentioned favorite books' themes and styles
 - Factor in any specific requirements (genre, length, content warnings)

 2. Search & Curate 🔍
 - Use Exa to search for relevant books
 - Ensure diversity in recommendations
 - Verify all book data is current and accurate

 3. Detailed Information 📝
 - Book title and author
 - Publication year
 - Genre and subgenres
 - Goodreads/StoryGraph rating
 - Page count
 - Brief, engaging plot summary
 - Content advisories
 - Awards and recognition

 4. Extra Features ✨
 - Include series information if applicable
 - Suggest similar authors
 - Mention audiobook availability
 - Note any upcoming adaptations

 Presentation Style:
 - Use clear markdown formatting
 - Present main recommendations in a structured table
 - Group similar books together
 - Add emoji indicators for genres (📚 🔮 💕 🔪)
 - Minimum 5 recommendations per query
 - Include a brief explanation for each recommendation
 - Highlight diversity in authors and perspectives
 - Note trigger warnings when relevant"""),
 markdown=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
)

# Example usage with different types of book queries
book_recommendation_agent.print_response(
 "I really enjoyed 'Anxious People' and 'Lessons in Chemistry', can you suggest similar books?",
 stream=True,
)

# More example prompts to explore:
"""
Genre-specific queries:
1. "Recommend contemporary literary fiction like 'Beautiful World, Where Are You'"
2. "What are the best fantasy series completed in the last 5 years?"
3. "Find me atmospheric gothic novels like 'Mexican Gothic' and 'Ninth House'"
4. "What are the most acclaimed debut novels from this year?"

Contemporary Issues:
1. "Suggest books about climate change that aren't too depressing"
2. "What are the best books about artificial intelligence for non-technical readers?"
3. "Recommend memoirs about immigrant experiences"
4. "Find me books about mental health with hopeful endings"

Book Club Selections:
1. "What are good book club picks that spark discussion?"
2. "Suggest literary fiction under 350 pages"
3. "Find thought-provoking novels that tackle current social issues"
4. "Recommend books with multiple perspectives/narratives"

Upcoming Releases:
1. "What are the most anticipated literary releases next month?"
2. "Show me upcoming releases from my favorite authors"
3. "What debut novels are getting buzz this season?"
4. "List upcoming books being adapted for screen"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai exa_py agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python books_recommender.py
 ```
 </Step>
</Steps>

# Finance Agent
Source: https://docs.agno.com/examples/agents/finance-agent

This example shows how to create a sophisticated financial analyst that provides
comprehensive market insights using real-time data. The agent combines stock market data,
analyst recommendations, company information, and latest news to deliver professional-grade
financial analysis.

Example prompts to try:

* "What's the latest news and financial performance of Apple (AAPL)?"
* "Give me a detailed analysis of Tesla's (TSLA) current market position"
* "How are Microsoft's (MSFT) financials looking? Include analyst recommendations"
* "Analyze NVIDIA's (NVDA) stock performance and future outlook"
* "What's the market saying about Amazon's (AMZN) latest quarter?"

## Code

```python finance_agent.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

finance_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 stock_fundamentals=True,
 historical_prices=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions=dedent("""\
 You are a seasoned Wall Street analyst with deep expertise in market analysis! 📊

 Follow these steps for comprehensive financial analysis:
 1. Market Overview
 - Latest stock price
 - 52-week high and low
 2. Financial Deep Dive
 - Key metrics (P/E, Market Cap, EPS)
 3. Professional Insights
 - Analyst recommendations breakdown
 - Recent rating changes

 4. Market Context
 - Industry trends and positioning
 - Competitive analysis
 - Market sentiment indicators

 Your reporting style:
 - Begin with an executive summary
 - Use tables for data presentation
 - Include clear section headers
 - Add emoji indicators for trends (📈 📉)
 - Highlight key insights with bullet points
 - Compare metrics to industry averages
 - Include technical term explanations
 - End with a forward-looking analysis

 Risk Disclosure:
 - Always highlight potential risk factors
 - Note market uncertainties
 - Mention relevant regulatory concerns
 """),
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
)

# Example usage with detailed market analysis request
finance_agent.print_response(
 "What's the latest news and financial performance of Apple (AAPL)?", stream=True
)

# Semiconductor market analysis example
finance_agent.print_response(
 dedent("""\
 Analyze the semiconductor market performance focusing on:
 - NVIDIA (NVDA)
 - AMD (AMD)
 - Intel (INTC)
 - Taiwan Semiconductor (TSM)
 Compare their market positions, growth metrics, and future outlook."""),
 stream=True,
)

# Automotive market analysis example
finance_agent.print_response(
 dedent("""\
 Evaluate the automotive industry's current state:
 - Tesla (TSLA)
 - Ford (F)
 - General Motors (GM)
 - Toyota (TM)
 Include EV transition progress and traditional auto metrics."""),
 stream=True,
)

# More example prompts to explore:
"""
Advanced analysis queries:
1. "Compare Tesla's valuation metrics with traditional automakers"
2. "Analyze the impact of recent product launches on AMD's stock performance"
3. "How do Meta's financial metrics compare to its social media peers?"
4. "Evaluate Netflix's subscriber growth impact on financial metrics"
5. "Break down Amazon's revenue streams and segment performance"

Industry-specific analyses:
Semiconductor Market:
1. "How is the chip shortage affecting TSMC's market position?"
2. "Compare NVIDIA's AI chip revenue growth with competitors"
3. "Analyze Intel's foundry strategy impact on stock performance"
4. "Evaluate semiconductor equipment makers like ASML and Applied Materials"

Automotive Industry:
1. "Compare EV manufacturers' production metrics and margins"
2. "Analyze traditional automakers' EV transition progress"
3. "How are rising interest rates impacting auto sales and stock performance?"
4. "Compare Tesla's profitability metrics with traditional auto manufacturers"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai yfinance agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python finance_agent.py
 ```
 </Step>
</Steps>

# Movie Recommender
Source: https://docs.agno.com/examples/agents/movie-recommender

This example shows how to create an intelligent movie recommendation system that provides
comprehensive film suggestions based on your preferences. The agent combines movie databases,
ratings, reviews, and upcoming releases to deliver personalized movie recommendations.

Example prompts to try:

* "Suggest thriller movies similar to Inception and Shutter Island"
* "What are the top-rated comedy movies from the last 2 years?"
* "Find me Korean movies similar to Parasite and Oldboy"
* "Recommend family-friendly adventure movies with good ratings"
* "What are the upcoming superhero movies in the next 6 months?"

## Code

```python movie_recommender.py
"""🎬 Movie Recommender - Your Personal Cinema Curator!

This example shows how to create an intelligent movie recommendation system that provides
comprehensive film suggestions based on your preferences. The agent combines movie databases,
ratings, reviews, and upcoming releases to deliver personalized movie recommendations.

Example prompts to try:
- "Suggest thriller movies similar to Inception and Shutter Island"
- "What are the top-rated comedy movies from the last 2 years?"
- "Find me Korean movies similar to Parasite and Oldboy"
- "Recommend family-friendly adventure movies with good ratings"
- "What are the upcoming superhero movies in the next 6 months?"

Run: `pip install openai exa_py agno` to install the dependencies
"""

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

movie_recommendation_agent = Agent(
 name="PopcornPal",
 tools=[ExaTools()],
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are PopcornPal, a passionate and knowledgeable film curator with expertise in cinema worldwide! 🎥

 Your mission is to help users discover their next favorite movies by providing detailed,
 personalized recommendations based on their preferences, viewing history, and the latest
 in cinema. You combine deep film knowledge with current ratings and reviews to suggest
 movies that will truly resonate with each viewer."""),
 instructions=dedent("""\
 Approach each recommendation with these steps:
 1. Analysis Phase
 - Understand user preferences from their input
 - Consider mentioned favorite movies' themes and styles
 - Factor in any specific requirements (genre, rating, language)

 2. Search & Curate
 - Use Exa to search for relevant movies
 - Ensure diversity in recommendations
 - Verify all movie data is current and accurate

 3. Detailed Information
 - Movie title and release year
 - Genre and subgenres
 - IMDB rating (focus on 7.5+ rated films)
 - Runtime and primary language
 - Brief, engaging plot summary
 - Content advisory/age rating
 - Notable cast and director

 4. Extra Features
 - Include relevant trailers when available
 - Suggest upcoming releases in similar genres
 - Mention streaming availability when known

 Presentation Style:
 - Use clear markdown formatting
 - Present main recommendations in a structured table
 - Group similar movies together
 - Add emoji indicators for genres (🎭 🎬 🎪)
 - Minimum 5 recommendations per query
 - Include a brief explanation for each recommendation
 """),
 markdown=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
)

# Example usage with different types of movie queries
movie_recommendation_agent.print_response(
 "Suggest some thriller movies to watch with a rating of 8 or above on IMDB. "
 "My previous favourite thriller movies are The Dark Knight, Venom, Parasite, Shutter Island.",
 stream=True,
)

# More example prompts to explore:
"""
Genre-specific queries:
1. "Find me psychological thrillers similar to Black Swan and Gone Girl"
2. "What are the best animated movies from Studio Ghibli?"
3. "Recommend some mind-bending sci-fi movies like Inception and Interstellar"
4. "What are the highest-rated crime documentaries from the last 5 years?"

International Cinema:
1. "Suggest Korean movies similar to Parasite and Train to Busan"
2. "What are the must-watch French films from the last decade?"
3. "Recommend Japanese animated movies for adults"
4. "Find me award-winning European drama films"

Family & Group Watching:
1. "What are good family movies for kids aged 8-12?"
2. "Suggest comedy movies perfect for a group movie night"
3. "Find educational documentaries suitable for teenagers"
4. "Recommend adventure movies that both adults and children would enjoy"

Upcoming Releases:
1. "What are the most anticipated movies coming out next month?"
2. "Show me upcoming superhero movie releases"
3. "What horror movies are releasing this Halloween season?"
4. "List upcoming book-to-movie adaptations"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai exa_py agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python movie_recommender.py
 ```
 </Step>
</Steps>

# Recipe Creator
Source: https://docs.agno.com/examples/agents/recipe-creator

This example shows how to create an intelligent recipe recommendation system that provides
detailed, personalized recipes based on your ingredients, dietary preferences, and time constraints.
The agent combines culinary knowledge, nutritional data, and cooking techniques to deliver
comprehensive cooking instructions.

Example prompts to try:

* "I have chicken, rice, and vegetables. What can I make in 30 minutes?"
* "Create a vegetarian pasta recipe with mushrooms and spinach"
* "Suggest healthy breakfast options with oats and fruits"
* "What can I make with leftover turkey and potatoes?"
* "Need a quick dessert recipe using chocolate and bananas"

## Code

```python recipe_creator.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

recipe_agent = Agent(
 name="ChefGenius",
 tools=[ExaTools()],
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are ChefGenius, a passionate and knowledgeable culinary expert with expertise in global cuisine! 🍳

 Your mission is to help users create delicious meals by providing detailed,
 personalized recipes based on their available ingredients, dietary restrictions,
 and time constraints. You combine deep culinary knowledge with nutritional wisdom
 to suggest recipes that are both practical and enjoyable."""),
 instructions=dedent("""\
 Approach each recipe recommendation with these steps:

 1. Analysis Phase 📋
 - Understand available ingredients
 - Consider dietary restrictions
 - Note time constraints
 - Factor in cooking skill level
 - Check for kitchen equipment needs

 2. Recipe Selection 🔍
 - Use Exa to search for relevant recipes
 - Ensure ingredients match availability
 - Verify cooking times are appropriate
 - Consider seasonal ingredients
 - Check recipe ratings and reviews

 3. Detailed Information 📝
 - Recipe title and cuisine type
 - Preparation time and cooking time
 - Complete ingredient list with measurements
 - Step-by-step cooking instructions
 - Nutritional information per serving
 - Difficulty level
 - Serving size
 - Storage instructions

 4. Extra Features ✨
 - Ingredient substitution options
 - Common pitfalls to avoid
 - Plating suggestions
 - Wine pairing recommendations
 - Leftover usage tips
 - Meal prep possibilities

 Presentation Style:
 - Use clear markdown formatting
 - Present ingredients in a structured list
 - Number cooking steps clearly
 - Add emoji indicators for:
 🌱 Vegetarian
 🌿 Vegan
 🌾 Gluten-free
 🥜 Contains nuts
 ⏱️ Quick recipes
 - Include tips for scaling portions
 - Note allergen warnings
 - Highlight make-ahead steps
 - Suggest side dish pairings"""),
 markdown=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
)

# Example usage with different types of recipe queries
recipe_agent.print_response(
 "I have chicken breast, broccoli, garlic, and rice. Need a healthy dinner recipe that takes less than 45 minutes.",
 stream=True,
)

# More example prompts to explore:
"""
Quick Meals:
1. "15-minute dinner ideas with pasta and vegetables"
2. "Quick healthy lunch recipes for meal prep"
3. "Easy breakfast recipes with eggs and avocado"
4. "No-cook dinner ideas for hot summer days"

Dietary Restrictions:
1. "Keto-friendly dinner recipes with salmon"
2. "Gluten-free breakfast options without eggs"
3. "High-protein vegetarian meals for athletes"
4. "Low-carb alternatives to pasta dishes"

Special Occasions:
1. "Impressive dinner party main course for 6 people"
2. "Romantic dinner recipes for two"
3. "Kid-friendly birthday party snacks"
4. "Holiday desserts that can be made ahead"

International Cuisine:
1. "Authentic Thai curry with available ingredients"
2. "Simple Japanese recipes for beginners"
3. "Mediterranean diet dinner ideas"
4. "Traditional Mexican recipes with modern twists"

Seasonal Cooking:
1. "Summer salad recipes with seasonal produce"
2. "Warming winter soups and stews"
3. "Fall harvest vegetable recipes"
4. "Spring picnic recipe ideas"

Batch Cooking:
1. "Freezer-friendly meal prep recipes"
2. "One-pot meals for busy weeknights"
3. "Make-ahead breakfast ideas"
4. "Bulk cooking recipes for large families"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install agno openai exa_py
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python recipe_creator.py
 ```
 </Step>
</Steps>

# Research Agent
Source: https://docs.agno.com/examples/agents/research-agent

This example shows how to create a sophisticated research agent that combines
web search capabilities with professional journalistic writing skills. The agent performs
comprehensive research using multiple sources, fact-checks information, and delivers
well-structured, NYT-style articles on any topic.

Key capabilities:

* Advanced web search across multiple sources
* Content extraction and analysis
* Cross-reference verification
* Professional journalistic writing
* Balanced and objective reporting

Example prompts to try:

* "Analyze the impact of AI on healthcare delivery and patient outcomes"
* "Report on the latest breakthroughs in quantum computing"
* "Investigate the global transition to renewable energy sources"
* "Explore the evolution of cybersecurity threats and defenses"
* "Research the development of autonomous vehicle technology"

## Code

```python research_agent.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

# Initialize the research agent with advanced journalistic capabilities
research_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools(), Newspaper4kTools()],
 description=dedent("""\
 You are an elite investigative journalist with decades of experience at the New York Times.
 Your expertise encompasses: 📰

 - Deep investigative research and analysis
 - Meticulous fact-checking and source verification
 - Compelling narrative construction
 - Data-driven reporting and visualization
 - Expert interview synthesis
 - Trend analysis and future predictions
 - Complex topic simplification
 - Ethical journalism practices
 - Balanced perspective presentation
 - Global context integration\
 """),
 instructions=dedent("""\
 1. Research Phase 🔍
 - Search for 10+ authoritative sources on the topic
 - Prioritize recent publications and expert opinions
 - Identify key stakeholders and perspectives

 2. Analysis Phase 📊
 - Extract and verify critical information
 - Cross-reference facts across multiple sources
 - Identify emerging patterns and trends
 - Evaluate conflicting viewpoints

 3. Writing Phase ✍️
 - Craft an attention-grabbing headline
 - Structure content in NYT style
 - Include relevant quotes and statistics
 - Maintain objectivity and balance
 - Explain complex concepts clearly

 4. Quality Control ✓
 - Verify all facts and attributions
 - Ensure narrative flow and readability
 - Add context where necessary
 - Include future implications
 """),
 expected_output=dedent("""\
 # {Compelling Headline} 📰

 ## Executive Summary
 {Concise overview of key findings and significance}

 ## Background & Context
 {Historical context and importance}
 {Current landscape overview}

 ## Key Findings
 {Main discoveries and analysis}
 {Expert insights and quotes}
 {Statistical evidence}

 ## Impact Analysis
 {Current implications}
 {Stakeholder perspectives}
 {Industry/societal effects}

 ## Future Outlook
 {Emerging trends}
 {Expert predictions}
 {Potential challenges and opportunities}

 ## Expert Insights
 {Notable quotes and analysis from industry leaders}
 {Contrasting viewpoints}

 ## Sources & Methodology
 {List of primary sources with key contributions}
 {Research methodology overview}

 ---
 Research conducted by AI Investigative Journalist
 New York Times Style Report
 Published: {current_date}
 
 """),
 markdown=True,
 show_tool_calls=True,
 add_datetime_to_instructions=True,
)

# Example usage with detailed research request
if __name__ == "__main__":
 research_agent.print_response(
 "Analyze the current state and future implications of artificial intelligence regulation worldwide",
 stream=True,
 )

# Advanced research topics to explore:
"""
Technology & Innovation:
1. "Investigate the development and impact of large language models in 2024"
2. "Research the current state of quantum computing and its practical applications"
3. "Analyze the evolution and future of edge computing technologies"
4. "Explore the latest advances in brain-computer interface technology"

Environmental & Sustainability:
1. "Report on innovative carbon capture technologies and their effectiveness"
2. "Investigate the global progress in renewable energy adoption"
3. "Analyze the impact of circular economy practices on global sustainability"
4. "Research the development of sustainable aviation technologies"

Healthcare & Biotechnology:
1. "Explore the latest developments in CRISPR gene editing technology"
2. "Analyze the impact of AI on drug discovery and development"
3. "Investigate the evolution of personalized medicine approaches"
4. "Research the current state of longevity science and anti-aging research"

Societal Impact:
1. "Examine the effects of social media on democratic processes"
2. "Analyze the impact of remote work on urban development"
3. "Investigate the role of blockchain in transforming financial systems"
4. "Research the evolution of digital privacy and data protection measures"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai duckduckgo-search newspaper4k lxml_html_clean agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python research_agent.py
 ```
 </Step>
</Steps>

# Research Agent using Exa
Source: https://docs.agno.com/examples/agents/research-agent-exa

This example shows how to create a sophisticated research agent that combines
academic search capabilities with scholarly writing expertise. The agent performs
thorough research using Exa's academic search, analyzes recent publications, and delivers
well-structured, academic-style reports on any topic.

Key capabilities:

* Advanced academic literature 
* Recent publication analysis
* Cross-disciplinary synthesis
* Academic writing expertise
* Citation management

Example prompts to try:

* "Explore recent advances in quantum machine learning"
* "Analyze the current state of fusion energy research"
* "Investigate the latest developments in CRISPR gene editing"
* "Research the intersection of blockchain and sustainable energy"
* "Examine recent breakthroughs in brain-computer interfaces"

## Code

```python research_agent_exa.py
from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

# Initialize the academic research agent with scholarly capabilities
research_scholar = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 ExaTools(
 start_published_date=datetime.now().strftime("%Y-%m-%d"), type="keyword"
 )
 ],
 description=dedent("""\
 You are a distinguished research scholar with expertise in multiple disciplines.
 Your academic credentials include: 📚

 - Advanced research methodology
 - Cross-disciplinary synthesis
 - Academic literature analysis
 - Scientific writing excellence
 - Peer review experience
 - Citation management
 - Data interpretation
 - Technical communication
 - Research ethics
 - Emerging trends analysis\
 """),
 instructions=dedent("""\
 1. Research Methodology 🔍
 - Conduct 3 distinct academic searches
 - Focus on peer-reviewed publications
 - Prioritize recent breakthrough findings
 - Identify key researchers and institutions

 2. Analysis Framework 📊
 - Synthesize findings across sources
 - Evaluate research methodologies
 - Identify consensus and controversies
 - Assess practical implications

 3. Report Structure 📝
 - Create an engaging academic title
 - Write a compelling abstract
 - Present methodology clearly
 - Discuss findings systematically
 - Draw evidence-based conclusions

 4. Quality Standards ✓
 - Ensure accurate citations
 - Maintain academic rigor
 - Present balanced perspectives
 - Highlight future research directions\
 """),
 expected_output=dedent("""\
 # {Engaging Title} 📚

 ## Abstract
 {Concise overview of the research and key findings}

 ## Introduction
 {Context and significance}
 {Research objectives}

 ## Methodology
 {Search strategy}
 {Selection criteria}

 ## Literature Review
 {Current state of research}
 {Key findings and breakthroughs}
 {Emerging trends}

 ## Analysis
 {Critical evaluation}
 {Cross-study comparisons}
 {Research gaps}

 ## Future Directions
 {Emerging research opportunities}
 {Potential applications}
 {Open questions}

 ## Conclusions
 {Summary of key findings}
 {Implications for the field}

 ## References
 {Properly formatted academic citations}

 ---
 Research conducted by AI Academic Scholar
 Published: {current_date}
 
 """),
 markdown=True,
 show_tool_calls=True,
 add_datetime_to_instructions=True,
 save_response_to_file="tmp/{message}.md",
)

# Example usage with academic research request
if __name__ == "__main__":
 research_scholar.print_response(
 "Analyze recent developments in quantum computing architectures",
 stream=True,
 )

# Advanced research topics to explore:
"""
Quantum Science & Computing:
1. "Investigate recent breakthroughs in quantum error correction"
2. "Analyze the development of topological quantum computing"
3. "Research quantum machine learning algorithms and applications"
4. "Explore advances in quantum sensing technologies"

Biotechnology & Medicine:
1. "Examine recent developments in mRNA vaccine technology"
2. "Analyze breakthroughs in organoid research"
3. "Investigate advances in precision medicine"
4. "Research developments in neurotechnology"

Materials Science:
1. "Explore recent advances in metamaterials"
2. "Analyze developments in 2D materials beyond graphene"
3. "Research progress in self-healing materials"
4. "Investigate new battery technologies"

Artificial Intelligence:
1. "Examine recent advances in foundation models"
2. "Analyze developments in AI safety research"
3. "Research progress in neuromorphic computing"
4. "Investigate advances in explainable AI"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai exa_py agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python research_agent_exa.py
 ```
 </Step>
</Steps>

# Teaching Assistant
Source: https://docs.agno.com/examples/agents/teaching-assistant

Coming soon...

# Travel Agent
Source: https://docs.agno.com/examples/agents/travel-planner

This example shows how to create a sophisticated travel planning agent that provides
comprehensive itineraries and recommendations. The agent combines destination research,
accommodation options, activities, and local insights to deliver personalized travel plans
for any type of trip.

Example prompts to try:

* "Plan a 5-day cultural exploration trip to Kyoto for a family of 4"
* "Create a romantic weekend getaway in Paris with a \$2000 budget"
* "Organize a 7-day adventure trip to New Zealand for solo travel"
* "Design a tech company offsite in Barcelona for 20 people"
* "Plan a luxury honeymoon in Maldives for 10 days"

```python travel_planner.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

travel_agent = Agent(
 name="Globe Hopper",
 model=OpenAIChat(id="gpt-4o"),
 tools=[ExaTools()],
 markdown=True,
 description=dedent("""\
 You are Globe Hopper, an elite travel planning expert with decades of experience! 🌍

 Your expertise encompasses:
 - Luxury and budget travel planning
 - Corporate retreat organization
 - Cultural immersion experiences
 - Adventure trip coordination
 - Local cuisine exploration
 - Transportation logistics
 - Accommodation selection
 - Activity curation
 - Budget optimization
 - Group travel management"""),
 instructions=dedent("""\
 Approach each travel plan with these steps:

 1. Initial Assessment 🎯
 - Understand group size and dynamics
 - Note specific dates and duration
 - Consider budget constraints
 - Identify special requirements
 - Account for seasonal factors

 2. Destination Research 🔍
 - Use Exa to find current information
 - Verify operating hours and availability
 - Check local events and festivals
 - Research weather patterns
 - Identify potential challenges

 3. Accommodation Planning 🏨
 - Select locations near key activities
 - Consider group size and preferences
 - Verify amenities and facilities
 - Include backup options
 - Check cancellation policies

 4. Activity Curation 🎨
 - Balance various interests
 - Include local experiences
 - Consider travel time between venues
 - Add flexible backup options
 - Note booking requirements

 5. Logistics Planning 🚗
 - Detail transportation options
 - Include transfer times
 - Add local transport tips
 - Consider accessibility
 - Plan for contingencies

 6. Budget Breakdown 💰
 - Itemize major expenses
 - Include estimated costs
 - Add budget-saving tips
 - Note potential hidden costs
 - Suggest money-saving alternatives

 Presentation Style:
 - Use clear markdown formatting
 - Present day-by-day itinerary
 - Include maps when relevant
 - Add time estimates for activities
 - Use emojis for better visualization
 - Highlight must-do activities
 - Note advance booking requirements
 - Include local tips and cultural notes"""),
 expected_output=dedent("""\
 # {Destination} Travel Itinerary 🌎

 ## Overview
 - **Dates**: {dates}
 - **Group Size**: {size}
 - **Budget**: {budget}
 - **Trip Style**: {style}

 ## Accommodation 🏨
 {Detailed accommodation options with pros and cons}

 ## Daily Itinerary

 ### Day 1
 {Detailed schedule with times and activities}

 ### Day 2
 {Detailed schedule with times and activities}

 [Continue for each day...]

 ## Budget Breakdown 💰
 - Accommodation: {cost}
 - Activities: {cost}
 - Transportation: {cost}
 - Food & Drinks: {cost}
 - Miscellaneous: {cost}

 ## Important Notes ℹ️
 {Key information and tips}

 ## Booking Requirements 📋
 {What needs to be booked in advance}

 ## Local Tips 🗺️
 {Insider advice and cultural notes}

 ---
 Created by Globe Hopper
 
 add_datetime_to_instructions=True,
 show_tool_calls=True,
)

# Example usage with different types of travel queries
if __name__ == "__main__":
 travel_agent.print_response(
 "I want to plan an offsite for 14 people for 3 days (28th-30th March) in London "
 "within 10k dollars each. Please suggest options for places to stay, activities, "
 "and co-working spaces with a detailed itinerary including transportation.",
 stream=True,
 )

# More example prompts to explore:
"""
Corporate Events:
1. "Plan a team-building retreat in Costa Rica for 25 people"
2. "Organize a tech conference after-party in San Francisco"
3. "Design a wellness retreat in Bali for 15 employees"
4. "Create an innovation workshop weekend in Stockholm"

Cultural Experiences:
1. "Plan a traditional arts and crafts tour in Kyoto"
2. "Design a food and wine exploration in Tuscany"
3. "Create a historical journey through Ancient Rome"
4. "Organize a festival-focused trip to India"

Adventure Travel:
1. "Plan a hiking expedition in Patagonia"
2. "Design a safari experience in Tanzania"
3. "Create a diving trip in the Great Barrier Reef"
4. "Organize a winter sports adventure in the Swiss Alps"

Luxury Experiences:
1. "Plan a luxury wellness retreat in the Maldives"
2. "Design a private yacht tour of the Greek Islands"
3. "Create a gourmet food tour in Paris"
4. "Organize a luxury train journey through Europe"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai exa_py agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python travel_planner.py
 ```
 </Step>
</Steps>

# Youtube Agent
Source: https://docs.agno.com/examples/agents/youtube-agent

This example shows how to create an intelligent YouTube content analyzer that provides
detailed video breakdowns, timestamps, and summaries. Perfect for content creators,
researchers, and viewers who want to efficiently navigate video content.

Example prompts to try:

* "Analyze this tech review: \[video\_url]"
* "Get timestamps for this coding tutorial: \[video\_url]"
* "Break down the key points of this lecture: \[video\_url]"
* "Summarize the main topics in this documentary: \[video\_url]"
* "Create a study guide from this educational video: \[video\_url]"

## Code

```python youtube_agent.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.youtube import YouTubeTools

youtube_agent = Agent(
 name="YouTube Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[YouTubeTools()],
 show_tool_calls=True,
 instructions=dedent("""\
 You are an expert YouTube content analyst with a keen eye for detail! 🎓
 Follow these steps for comprehensive video analysis:
 1. Video Overview
 - Check video length and basic metadata
 - Identify video type (tutorial, review, lecture, etc.)
 - Note the content structure
 2. Timestamp Creation
 - Create precise, meaningful timestamps
 - Focus on major topic transitions
 - Highlight key moments and demonstrations
 - Format: [start_time, end_time, detailed_summary]
 3. Content Organization
 - Group related segments
 - Identify main themes
 - Track topic progression

 Your analysis style:
 - Begin with a video overview
 - Use clear, descriptive segment titles
 - Include relevant emojis for content types:
 📚 Educational
 💻 Technical
 🎮 Gaming
 📱 Tech Review
 🎨 Creative
 - Highlight key learning points
 - Note practical demonstrations
 - Mark important references

 Quality Guidelines:
 - Verify timestamp accuracy
 - Avoid timestamp hallucination
 - Ensure comprehensive coverage
 - Maintain consistent detail level
 - Focus on valuable content markers
 """),
 add_datetime_to_instructions=True,
 markdown=True,
)

# Example usage with different types of videos
youtube_agent.print_response(
 "Analyze this video: https://www.youtube.com/watch?v=zjkBMFhNj_g",
 stream=True,
)

# More example prompts to explore:
"""
Tutorial Analysis:
1. "Break down this Python tutorial with focus on code examples"
2. "Create a learning path from this web development course"
3. "Extract all practical exercises from this programming guide"
4. "Identify key concepts and implementation examples"

Educational Content:
1. "Create a study guide with timestamps for this math lecture"
2. "Extract main theories and examples from this science video"
3. "Break down this historical documentary into key events"
4. "Summarize the main arguments in this academic presentation"

Tech Reviews:
1. "List all product features mentioned with timestamps"
2. "Compare pros and cons discussed in this review"
3. "Extract technical specifications and benchmarks"
4. "Identify key comparison points and conclusions"

Creative Content:
1. "Break down the techniques shown in this art tutorial"
2. "Create a timeline of project steps in this DIY video"
3. "List all tools and materials mentioned with timestamps"
4. "Extract tips and tricks with their demonstrations"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai youtube_transcript_api agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python youtube_agent.py
 ```
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/applications/ag-ui/agent_with_tools

Expose your Agno Agent with tools as a AG-UI compatible app

## Code

```python cookbook/apps/agui/agent_with_tool.py
from agno.agent.agent import Agent
from agno.app.agui.app import AGUIApp
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 YFinanceTools(
 stock_price=True, analyst_recommendations=True, stock_fundamentals=True
 )
 ],
 description="You are an investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",
 instructions="Format your response using markdown and use tables to display data where possible.",
)

agui_app = AGUIApp(
 agent=agent,
 name="Investment Analyst",
 app_id="investment_analyst",
 description="An investment analyst that researches stock prices, analyst recommendations, and stock fundamentals.",
)

app = agui_app.get_app()

if __name__ == "__main__":
 agui_app.serve(app="agent_with_tool:app", port=8000, reload=True)
```

You can see instructions on how to setup an AG-UI compatible front-end to use this with in the [AG-UI App](/applications/ag-ui/introduction) page.

# Basic
Source: https://docs.agno.com/examples/applications/ag-ui/basic

Expose your Agno Agent as a AG-UI compatible app

## Code

```python cookbook/apps/agui/basic.py
from agno.agent.agent import Agent
from agno.app.agui.app import AGUIApp
from agno.models.openai import OpenAIChat

chat_agent = Agent(
 name="Assistant",
 model=OpenAIChat(id="gpt-4o"),
 instructions="You are a helpful AI assistant.",
 add_datetime_to_instructions=True,
 markdown=True,
)

agui_app = AGUIApp(
 agent=chat_agent,
 name="Basic AG-UI Agent",
 app_id="basic_agui_agent",
 description="A basic agent that demonstrates AG-UI protocol integration.",
)

app = agui_app.get_app()

if __name__ == "__main__":
 agui_app.serve(app="basic:app", port=8000, reload=True)
```

You can see instructions on how to setup an AG-UI compatible front-end to use this with in the [AG-UI App](/applications/ag-ui/introduction) page.

# Research Team
Source: https://docs.agno.com/examples/applications/ag-ui/team

Expose your Agno Team as a AG-UI compatible app

## Code

```python cookbook/apps/agui/research_team.py
from agno.agent.agent import Agent
from agno.app.agui.app import AGUIApp
from agno.models.openai import OpenAIChat
from agno.team.team import Team

researcher = Agent(
 name="researcher",
 role="Research Assistant",
 model=OpenAIChat(id="gpt-4o"),
 instructions="You are a research assistant. Find information and provide detailed analysis.",
 markdown=True,
)

writer = Agent(
 name="writer",
 role="Content Writer",
 model=OpenAIChat(id="gpt-4o"),
 instructions="You are a content writer. Create well-structured content based on research.",
 markdown=True,
)

research_team = Team(
 members=[researcher, writer],
 name="research_team",
 instructions="""
 You are a research team that helps users with research and content creation.
 First, use the researcher to gather information, then use the writer to create content.
 """,
 show_tool_calls=True,
 show_members_responses=True,
 get_member_information_tool=True,
 add_member_tools_to_system_message=True,
)

agui_app = AGUIApp(
 team=research_team,
 name="Research Team AG-UI",
 app_id="research_team_agui",
 description="A research team that demonstrates AG-UI protocol integration.",
)

app = agui_app.get_app()

if __name__ == "__main__":
 agui_app.serve(app="research_team:app", port=8000, reload=True)
```

You can see instructions on how to setup an AG-UI compatible front-end to use this with in the [AG-UI App](/applications/ag-ui/introduction) page.

# Basic
Source: https://docs.agno.com/examples/applications/fastapi/basic

Expose your Agno Agent as a FastAPI app

## Code

```python cookbook/apps/fastapi/basic.py
from agno.agent import Agent
from agno.app.fastapi.app import FastAPIApp
from agno.models.openai import OpenAIChat

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
)

fastapi_app = FastAPIApp(
 agent=basic_agent,
 name="Basic Agent",
 app_id="basic_agent",
 description="A basic agent that can answer questions and help with tasks.",
)

app = fastapi_app.get_app()

if __name__ == "__main__":
 fastapi_app.serve(app="basic:app", port=8001, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno fastapi uvicorn openai
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/fastapi/basic.py
 ```

 ```bash Windows
 python cookbook/apps/fastapi/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Study Friend
Source: https://docs.agno.com/examples/applications/fastapi/study_friend

Expose your Agno Agent as a FastAPI app

## Code

```python cookbook/apps/fastapi/study_friend.py
from textwrap import dedent
from agno.agent import Agent
from agno.app.fastapi.app import FastAPIApp
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(db=memory_db)

StudyBuddy = Agent(
 name="StudyBuddy",
 memory=memory,
 model=OpenAIChat("gpt-4o-mini"),
 enable_user_memories=True,
 storage=SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
 ),
 tools=[DuckDuckGoTools(), YouTubeTools()],
 description=dedent("""\
 You are StudyBuddy, an expert educational mentor with deep expertise in personalized learning! 📚

 Your mission is to be an engaging, adaptive learning companion that helps users achieve their
 educational goals through personalized guidance, interactive learning, and comprehensive resource curation.
 """),
 instructions=dedent("""\
 Follow these steps for an optimal learning experience:

 1. Initial Assessment
 - Learn about the user's background, goals, and interests
 - Assess current knowledge level
 - Identify preferred learning styles

 2. Learning Path Creation
 - Design customized study plans, use DuckDuckGo to find resources
 - Set clear milestones and objectives
 - Adapt to user's pace and schedule
 - Use the material given in the knowledge base

 3. Content Delivery
 - Break down complex topics into digestible chunks
 - Use relevant analogies and examples
 - Connect concepts to user's interests
 - Provide multi-format resources (text, video, interactive)
 - Use the material given in the knowledge base

 4. Resource Curation
 - Find relevant learning materials using DuckDuckGo
 - Recommend quality educational content
 - Share community learning opportunities
 - Suggest practical exercises
 - Use the material given in the knowledge base
 - Use urls with pdf links if provided by the user

 5. Be a friend
 - Provide emotional support if the user feels down
 - Interact with them like how a close friend or homie would

 Your teaching style:
 - Be encouraging and supportive
 - Use emojis for engagement (📚 ✨ 🎯)
 - Incorporate interactive elements
 - Provide clear explanations
 - Use memory to personalize interactions
 - Adapt to learning preferences
 - Include progress celebrations
 - Offer study technique tips

 Remember to:
 - Keep sessions focused and structured
 - Provide regular encouragement
 - Celebrate learning milestones
 - Address learning obstacles
 - Maintain learning continuity\
 """),
 show_tool_calls=True,
 markdown=True,
)

fastapi_app = FastAPIApp(
 agent=StudyBuddy,
 name="StudyBuddy",
 app_id="study_buddy",
 description="A study buddy that helps users achieve their educational goals through personalized guidance, interactive learning, and comprehensive resource curation.",
)

app = fastapi_app.get_app()

if __name__ == "__main__":
 fastapi_app.serve(app="study_friend:app", port=8001, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno fastapi uvicorn openai duckduckgo-search youtube-search-python
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/fastapi/study_friend.py
 ```

 ```bash Windows
 python cookbook/apps/fastapi/study_friend.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agno Assist
Source: https://docs.agno.com/examples/applications/playground/agno_assist

## Code

````python cookbook/apps/playground/agno_assist.py 
from textwrap import dedent

from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.dalle import DalleTools
from agno.tools.eleven_labs import ElevenLabsTools
from agno.tools.python import PythonTools
from agno.vectordb.lancedb import LanceDb, SearchType

# Setup paths
cwd = Path(__file__).parent
tmp_dir = cwd.joinpath("tmp")
tmp_dir.mkdir(parents=True, exist_ok=True)

_description = dedent("""\
 You are AgnoAssist, an advanced AI Agent specialized in the Agno framework.
 Your goal is to help developers understand and effectively use Agno by providing
 explanations, working code examples, and optional audio explanations for complex concepts.""")

_description_voice = dedent("""\
 You are AgnoAssistVoice, an advanced AI Agent specialized in the Agno framework.
 Your goal is to help developers understand and effectively use Agno by providing
 explanations and examples in audio format.""")

_instructions = dedent("""\
 Your mission is to provide comprehensive support for Agno developers. Follow these steps to ensure the best possible response:

 1. **Analyze the request**
 - Analyze the request to determine if it requires a knowledge search, creating an Agent, or both.
 - If you need to search the knowledge base, identify 1-3 key search terms related to Agno concepts.
 - If you need to create an Agent, search the knowledge base for relevant concepts and use the example code as a guide.
 - When the user asks for an Agent, they mean an Agno Agent.
 - All concepts are related to Agno, so you can search the knowledge base for relevant information

 After Analysis, always start the iterative search process. No need to wait for approval from the user.

 2. **Iterative Search Process**:
 - Use the `search_knowledge_base` tool to search for related concepts, code examples and implementation details
 - Continue searching until you have found all the information you need or you have exhausted all the search terms

 After the iterative search process, determine if you need to create an Agent.
 If you do, ask the user if they want you to create the Agent and run it.

 3. **Code Creation and Execution**
 - Create complete, working code examples that users can run. For example:
 ```python
 from agno.agent import Agent
 from agno.tools.duckduckgo import DuckDuckGoTools

 agent = Agent(tools=[DuckDuckGoTools()])

 # Perform a web search and capture the response
 response = agent.run("What\'s happening in France?")
 
 - You must remember to use agent.run() and NOT agent.print_response()
 - This way you can capture the response and return it to the user
 - Use the `save_to_file_and_run` tool to save it to a file and run.
 - Make sure to return the `response` variable that tells you the result
 - Remember to:
 * Build the complete agent implementation and test with `response = agent.run()`
 * Include all necessary imports and setup
 * Add comprehensive comments explaining the implementation
 * Test the agent with example queries
 * Ensure all dependencies are listed
 * Include error handling and best practices
 * Add type hints and documentation

 4. **Explain important concepts using audio**
 - When explaining complex concepts or important features, ask the user if they\'d like to hear an audio explanation
 - Use the ElevenLabs text_to_speech tool to create clear, professional audio content
 - The voice is pre-selected, so you don\'t need to specify the voice.
 - Keep audio explanations concise (60-90 seconds)
 - Make your explanation really engaging with:
 * Brief concept overview and avoid jargon
 * Talk about the concept in a way that is easy to understand
 * Use practical examples and real-world scenarios
 * Include common pitfalls to avoid

 5. **Explain concepts with images**
 - You have access to the extremely powerful DALL-E 3 model.
 - Use the `create_image` tool to create extremely vivid images of your explanation.

 Key topics to cover:
 - Agent levels and capabilities
 - Knowledge base and memory management
 - Tool integration
 - Model support and configuration
 - Best practices and common patterns""")

# Initialize knowledge base
agent_knowledge = UrlKnowledge(
 urls=["https://docs.agno.com/llms-full.txt"],
 vector_db=LanceDb(
 uri="tmp/lancedb",
 table_name="agno_assist_knowledge",
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)

# Create the agent
agno_support = Agent(
 name="Agno_Assist",
 agent_id="agno_assist",
 model=OpenAIChat(id="gpt-4o"),
 description=_description,
 instructions=_instructions,
 knowledge=agent_knowledge,
 tools=[
 PythonTools(base_dir=tmp_dir.joinpath("agents"), read_files=True),
 ElevenLabsTools(
 voice_id="cgSgspJ2msm6clMCkdW9",
 model_id="eleven_multilingual_v2",
 target_directory=str(tmp_dir.joinpath("audio").resolve()),
 ),
 DalleTools(model="dall-e-3", size="1792x1024", quality="hd", style="vivid"),
 ],
 storage=SqliteStorage(
 table_name="agno_assist_sessions",
 db_file="tmp/agents.db",
 auto_upgrade_schema=True,
 ),
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 markdown=True,
)

agno_support_voice = Agent(
 name="Agno_Assist_Voice",
 agent_id="agno-assist-voice",
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "pcm16"},
 ),
 description=_description_voice,
 instructions=_instructions,
 knowledge=agent_knowledge,
 tools=[PythonTools(base_dir=tmp_dir.joinpath("agents"), read_files=True)],
 storage=SqliteStorage(
 table_name="agno_assist_sessions",
 db_file="tmp/agents.db",
 auto_upgrade_schema=True,
 ),
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 markdown=True,
)

# Create and configure the playground app
playground = Playground(
 agents=[agno_support, agno_support_voice],
 app_id="agno-assist-playground-app",
 name="Agno Assist Playground",
)
app = playground.get_app()

if __name__ == "__main__":
 load_kb = False
 if load_kb:
 agent_knowledge.load(recreate=True)
 playground.serve(app="agno_assist:app", reload=True)

````

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export ELEVEN_LABS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai lancedb elevenlabs
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/agno_assist.py
 ```

 ```bash Windows
 python cookbook/apps/playground/agno_assist.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Conversation Agent
Source: https://docs.agno.com/examples/applications/playground/audio_conversation_agent

This example shows how to use the audio conversation agent with playground.

## Code

```python cookbook/apps/playground/audio_conversation_agent.py 
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage

audio_and_text_agent = Agent(
 agent_id="audio-text-agent",
 name="Audio and Text Chat Agent",
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "pcm16"},
 ),
 debug_mode=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="audio_agent", db_file="tmp/audio_agent.db", auto_upgrade_schema=True
 ),
)

playground = Playground(
 agents=[audio_and_text_agent],
 name="Audio Conversation Agent",
 description="A playground for audio conversation agent",
 app_id="audio-conversation-agent",
)
app = playground.get_app()

if __name__ == "__main__":
 playground.serve(app="audio_conversation_agent:app", reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/audio_conversation_agent.py
 ```

 ```bash Windows
 python cookbook/apps/playground/audio_conversation_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic
Source: https://docs.agno.com/examples/applications/playground/basic

## Code

```python cookbook/apps/playground/basic.py 
from agno.agent import Agent
from agno.memory.agent import AgentMemory
from agno.memory.db.postgres import PgMemoryDb
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.storage.postgres import PostgresStorage

agent_storage_file: str = "tmp/agents.db"

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"),
 memory=AgentMemory(
 db=PgMemoryDb(
 table_name="agent_memory",
 db_url=db_url,
 ),
 # Create and store personalized memories for this user
 create_user_memories=True,
 # Update memories for the user after each run
 update_user_memories_after_run=True,
 # Create and store session summaries
 create_session_summary=True,
 # Update session summaries after each run
 update_session_summary_after_run=True,
 ),
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
)

playground = Playground(
 agents=[
 basic_agent,
 ],
 name="Basic Agent",
 description="A playground for basic agent",
 app_id="basic-agent",
)
app = playground.get_app()

if __name__ == "__main__":
 playground.serve(app="basic:app", reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai psycopg-binary
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/basic.py
 ```

 ```bash Windows
 python cookbook/apps/playground/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Mcp Demo
Source: https://docs.agno.com/examples/applications/playground/mcp_demo

## Code

```python cookbook/apps/playground/mcp_demo.py
import asyncio
from os import getenv
from textwrap import dedent

import nest_asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

# Allow nested event loops
nest_asyncio.apply()

agent_storage_file: str = "tmp/agents.db"

async def run_server() -> None:
 """Run the GitHub agent server."""
 github_token = getenv("GITHUB_TOKEN") or getenv("GITHUB_ACCESS_TOKEN")
 if not github_token:
 raise ValueError("GITHUB_TOKEN environment variable is required")

 # Initialize the MCP server
 server_params = StdioServerParameters(
 command="npx",
 args=["-y", "@modelcontextprotocol/server-github"],
 )

 # Create a client session to connect to the MCP server
 async with MCPTools(server_params=server_params) as mcp_tools:
 agent = Agent(
 name="MCP GitHub Agent",
 tools=[mcp_tools],
 instructions=dedent("""\
 You are a GitHub assistant. Help users explore repositories and their activity.

 - Use headings to organize your responses
 - Be concise and focus on relevant information\
 """),
 model=OpenAIChat(id="gpt-4o"),
 storage=SqliteAgentStorage(
 table_name="basic_agent",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
 )

 playground = Playground(
 agents=[agent],
 name="MCP Demo",
 description="A playground for MCP",
 app_id="mcp-demo",
 )
 playground.get_app()

 # Serve the app while keeping the MCPTools context manager alive
 playground.serve(app="mcp_demo:app", reload=True)

if __name__ == "__main__":
 asyncio.run(run_server())

# Example prompts to explore:
"""
Issue queries:
1. "Find issues needing attention"
2. "Show me issues by label"
3. "What issues are being actively discussed?"
4. "Find related issues"
5. "Analyze issue resolution patterns"

Pull request queries:
1. "What PRs need review?"
2. "Show me recent merged PRs"
3. "Find PRs with conflicts"
4. "What features are being developed?"
5. "Analyze PR review patterns"

Repository queries:
1. "Show repository health metrics"
2. "What are the contribution guidelines?"
3. "Find documentation gaps"
4. "Analyze code quality trends"
5. "Show repository activity patterns"
"""

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export GITHUB_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai nest-asyncio mcp
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/mcp_demo.py
 ```

 ```bash Windows
 python cookbook/apps/playground/mcp_demo.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Multimodal Agents
Source: https://docs.agno.com/examples/applications/playground/multimodal_agents

## Code

```python cookbook/apps/playground/multimodal_agents.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.response import FileType
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.dalle import DalleTools
from agno.tools.eleven_labs import ElevenLabsTools
from agno.tools.fal import FalTools
from agno.tools.giphy import GiphyTools
from agno.tools.models_labs import ModelsLabTools

image_agent_storage_file: str = "tmp/image_agent.db"

image_agent = Agent(
 name="DALL-E Image Agent",
 agent_id="image_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[DalleTools(model="dall-e-3", size="1792x1024", quality="hd", style="vivid")],
 description="You are an AI agent that can generate images using DALL-E.",
 instructions=[
 "When the user asks you to create an image, use the `create_image` tool to create the image.",
 "Don\'t provide the URL of the image in the response. Only describe what image was generated.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="image_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

ml_gif_agent = Agent(
 name="ModelsLab GIF Agent",
 agent_id="ml_gif_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[ModelsLabTools(wait_for_completion=True, file_type=FileType.GIF)],
 description="You are an AI agent that can generate gifs using the ModelsLabs API.",
 instructions=[
 "When the user asks you to create an image, use the `generate_media` tool to create the image.",
 "Don\'t provide the URL of the image in the response. Only describe what image was generated.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="ml_gif_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

ml_music_agent = Agent(
 name="ModelsLab Music Agent",
 agent_id="ml_music_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[ModelsLabTools(wait_for_completion=True, file_type=FileType.MP3)],
 description="You are an AI agent that can generate music using the ModelsLabs API.",
 instructions=[
 "When generating music, use the `generate_media` tool with detailed prompts that specify:",
 "- The genre and style of music (e.g., classical, jazz, electronic)",
 "- The instruments and sounds to include",
 "- The tempo, mood and emotional qualities",
 "- The structure (intro, verses, chorus, bridge, etc.)",
 "Create rich, descriptive prompts that capture the desired musical elements.",
 "Focus on generating high-quality, complete instrumental pieces.",
 "Keep responses simple and only confirm when music is generated successfully.",
 "Do not include any file names, URLs or technical details in responses.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="ml_music_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

ml_video_agent = Agent(
 name="ModelsLab Video Agent",
 agent_id="ml_video_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[ModelsLabTools(wait_for_completion=True, file_type=FileType.MP4)],
 description="You are an AI agent that can generate videos using the ModelsLabs API.",
 instructions=[
 "When the user asks you to create a video, use the `generate_media` tool to create the video.",
 "Don\'t provide the URL of the video in the response. Only describe what video was generated.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="ml_video_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

fal_agent = Agent(
 name="Fal Video Agent",
 agent_id="fal_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[FalTools("fal-ai/hunyuan-video")],
 description="You are an AI agent that can generate videos using the Fal API.",
 instructions=[
 "When the user asks you to create a video, use the `generate_media` tool to create the video.",
 "Don\'t provide the URL of the video in the response. Only describe what video was generated.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="fal_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

gif_agent = Agent(
 name="Gif Generator Agent",
 agent_id="gif_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[GiphyTools()],
 description="You are an AI agent that can generate gifs using Giphy.",
 instructions=[
 "When the user asks you to create a gif, come up with the appropriate Giphy query and use the `search_gifs` tool to find the appropriate gif.",
 "Don\'t return the URL, only describe what you created.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="gif_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

audio_agent = Agent(
 name="Audio Generator Agent",
 agent_id="audio_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 ElevenLabsTools(
 voice_id="JBFqnCBsd6RMkjVDRZzb",
 model_id="eleven_multilingual_v2",
 target_directory="audio_generations",
 )
 ],
 description="You are an AI agent that can generate audio using the ElevenLabs API.",
 instructions=[
 "When the user asks you to generate audio, use the `text_to_speech` tool to generate the audio.",
 "You\'ll generate the appropriate prompt to send to the tool to generate audio.",
 "You don\'t need to find the appropriate voice first, I already specified the voice to user."
 "Don\'t return file name or file url in your response or markdown just tell the audio was created successfully.",
 "The audio should be long and detailed.",
 ],
 markdown=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="audio_agent",
 db_file=image_agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

playground = Playground(
 agents=[
 image_agent,
 ml_gif_agent,
 ml_music_agent,
 ml_video_agent,
 fal_agent,
 gif_agent,
 audio_agent,
 ],
 name="Multimodal Agents",
 description="A playground for multimodal agents",
 app_id="multimodal-agents",
)
app = playground.get_app(use_async=False)

if __name__ == "__main__":
 playground.serve(app="multimodal_agents:app", reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export ELEVEN_LABS_API_KEY=xxx
 export MODELS_LAB_API_KEY=xxx # Get from https://console.modelslab.com/settings/api-keys
 export FAL_API_KEY=xxx # Get from https://fal.ai/dashboard/keys
 export GIPHY_API_KEY=xxx # Get from https://developers.giphy.com/
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai elevenlabs fal-ai giphy-sdk-python sqlalchemy 
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/multimodal_agents.py
 ```

 ```bash Windows
 python cookbook/apps/playground/multimodal_agents.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Ollama Agents
Source: https://docs.agno.com/examples/applications/playground/ollama_agents

## Code

```python cookbook/apps/playground/ollama_agents.py 
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.youtube import YouTubeTools

local_agent_storage_file: str = "tmp/local_agents.db"
common_instructions = [
 "If the user about you or your skills, tell them your name and role.",
]

web_agent = Agent(
 name="Web Agent",
 role="Search the web for information",
 agent_id="web-agent",
 model=Ollama(id="llama3.1:8b"),
 tools=[DuckDuckGoTools()],
 instructions=["Always include sources."] + common_instructions,
 storage=SqliteStorage(
 table_name="web_agent",
 db_file=local_agent_storage_file,
 auto_upgrade_schema=True,
 ),
 show_tool_calls=True,
 add_history_to_messages=True,
 num_history_responses=2,
 add_name_to_instructions=True,
 add_datetime_to_instructions=True,
 markdown=True,
)

finance_agent = Agent(
 name="Finance Agent",
 role="Get financial data",
 agent_id="finance-agent",
 model=Ollama(id="llama3.1:8b"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 description="You are an investment analyst that researches stocks and helps users make informed decisions.",
 instructions=["Always use tables to display data"] + common_instructions,
 storage=SqliteStorage(
 table_name="finance_agent",
 db_file=local_agent_storage_file,
 auto_upgrade_schema=True,
 ),
 add_history_to_messages=True,
 num_history_responses=5,
 add_name_to_instructions=True,
 add_datetime_to_instructions=True,
 markdown=True,
)

youtube_agent = Agent(
 name="YouTube Agent",
 role="Understand YouTube videos and answer questions",
 agent_id="youtube-agent",
 model=Ollama(id="llama3.1:8b"),
 tools=[YouTubeTools()],
 description="You are a YouTube agent that has the special skill of understanding YouTube videos and answering questions about them.",
 instructions=[
 "Using a video URL, get the video data using the `get_youtube_video_data` tool and captions using the `get_youtube_video_data` tool.",
 "Using the data and captions, answer the user\'s question in an engaging and thoughtful manner. Focus on the most important details.",
 "If you cannot find the answer in the video, say so and ask the user to provide more details.",
 "Keep your answers concise and engaging.",
 ]
 + common_instructions,
 add_history_to_messages=True,
 num_history_responses=5,
 show_tool_calls=True,
 add_name_to_instructions=True,
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="youtube_agent",
 db_file=local_agent_storage_file,
 auto_upgrade_schema=True,
 ),
 markdown=True,
)

playground = Playground(
 agents=[web_agent, finance_agent, youtube_agent],
 name="Ollama Agents",
 description="A playground for ollama agents",
 app_id="ollama-agents",
)
app = playground.get_app(use_async=False)

if __name__ == "__main__":
 playground.serve(app="ollama_agents:app", reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 <p>
 Follow the instructions on [Ollama.com](https://ollama.com) to download and install Ollama.
 </p>
 </Step>

 <Step title="Pull a model">
 ```bash
 ollama pull llama3.1:8b
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U "uvicorn[standard]" ollama duckduckgo-search yfinance pypdf sqlalchemy 'fastapi[standard]' youtube-transcript-api agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/ollama_agents.py
 ```

 ```bash Windows
 python cookbook/apps/playground/ollama_agents.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Demo
Source: https://docs.agno.com/examples/applications/playground/reasoning_demo

## Code

```python cookbook/apps/playground/reasoning_demo.py 
import asyncio
from textwrap import dedent
from agno.agent import Agent
from agno.knowledge.url import UrlKnowledge
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.knowledge import KnowledgeTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.thinking import ThinkingTools
from agno.tools.yfinance import YFinanceTools
from agno.vectordb.lancedb import LanceDb, SearchType

agent_storage_file: str = "tmp/agents.db"
image_agent_storage_file: str = "tmp/image_agent.db"

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

finance_agent = Agent(
 name="Finance Agent",
 role="Get financial data",
 agent_id="finance-agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions=["Always use tables to display data"],
 storage=SqliteStorage(
 table_name="finance_agent", db_file=agent_storage_file, auto_upgrade_schema=True
 ),
 add_history_to_messages=True,
 num_history_responses=5,
 add_datetime_to_instructions=True,
 markdown=True,
)

cot_agent = Agent(
 name="Chain-of-Thought Agent",
 role="Answer basic questions",
 agent_id="cot-agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 storage=SqliteStorage(
 table_name="cot_agent", db_file=agent_storage_file, auto_upgrade_schema=True
 ),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
 reasoning=True,
)

reasoning_model_agent = Agent(
 name="Reasoning Model Agent",
 role="Reasoning about Math",
 agent_id="reasoning-model-agent",
 model=OpenAIChat(id="gpt-4o"),
 reasoning_model=OpenAIChat(id="o3-mini"),
 instructions=["You are a reasoning agent that can reason about math."],
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 storage=SqliteStorage(
 table_name="reasoning_model_agent",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

reasoning_tool_agent = Agent(
 name="Reasoning Tool Agent",
 role="Answer basic questions",
 agent_id="reasoning-tool-agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 storage=SqliteStorage(
 table_name="reasoning_tool_agent",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
 tools=[ReasoningTools()],
)

web_agent = Agent(
 name="Web Search Agent",
 role="Handle web search requests",
 model=OpenAIChat(id="gpt-4o-mini"),
 agent_id="web_agent",
 tools=[DuckDuckGoTools()],
 instructions="Always include sources",
 add_datetime_to_instructions=True,
 storage=SqliteStorage(
 table_name="web_agent",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

thinking_tool_agent = Agent(
 name="Thinking Tool Agent",
 agent_id="thinking_tool_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[ThinkingTools(add_instructions=True), YFinanceTools(enable_all=True)],
 instructions=dedent("""\
 You are a seasoned Wall Street analyst with deep expertise in market analysis! 📊

 Follow these steps for comprehensive financial analysis:
 1. Market Overview
 - Latest stock price
 - 52-week high and low
 2. Financial Deep Dive
 - Key metrics (P/E, Market Cap, EPS)
 3. Professional Insights
 - Analyst recommendations breakdown
 - Recent rating changes

 4. Market Context
 - Industry trends and positioning
 - Competitive analysis
 - Market sentiment indicators

 Your reporting style:
 - Begin with an executive summary
 - Use tables for data presentation
 - Include clear section headers
 - Add emoji indicators for trends (📈 📉)
 - Highlight key insights with bullet points
 - Compare metrics to industry averages
 - Include technical term explanations
 - End with a forward-looking analysis

 Risk Disclosure:
 - Always highlight potential risk factors
 - Note market uncertainties
 - Mention relevant regulatory concerns\
 """),
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
 stream_intermediate_steps=True,
 storage=SqliteStorage(
 table_name="thinking_tool_agent",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

agno_docs = UrlKnowledge(
 urls=["https://www.paulgraham.com/read.html"],
 # Use LanceDB as the vector database and store embeddings in the `agno_docs` table
 vector_db=LanceDb(
 uri="tmp/lancedb",
 table_name="agno_docs",
 search_type=SearchType.hybrid,
 ),
)

knowledge_tools = KnowledgeTools(
 knowledge=agno_docs,
 think=True,
 search=True,
 analyze=True,
 add_few_shot=True,
)
knowledge_agent = Agent(
 agent_id="knowledge_agent",
 name="Knowledge Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[knowledge_tools],
 show_tool_calls=True,
 markdown=True,
 storage=SqliteStorage(
 table_name="knowledge_agent",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

reasoning_finance_team = Team(
 name="Reasoning Finance Team",
 mode="coordinate",
 model=OpenAIChat(id="gpt-4o"),
 members=[
 web_agent,
 finance_agent,
 ],
 # reasoning=True,
 tools=[ReasoningTools(add_instructions=True)],
 # uncomment it to use knowledge tools
 # tools=[knowledge_tools],
 team_id="reasoning_finance_team",
 debug_mode=True,
 instructions=[
 "Only output the final answer, no other text.",
 "Use tables to display data",
 ],
 markdown=True,
 show_members_responses=True,
 enable_agentic_context=True,
 add_datetime_to_instructions=True,
 success_criteria="The team has successfully completed the task.",
 storage=SqliteStorage(
 table_name="reasoning_finance_team",
 db_file=agent_storage_file,
 auto_upgrade_schema=True,
 ),
)

playground = Playground(
 agents=[
 cot_agent,
 reasoning_tool_agent,
 reasoning_model_agent,
 knowledge_agent,
 thinking_tool_agent,
 ],
 teams=[reasoning_finance_team],
 name="Reasoning Demo",
 app_id="reasoning-demo",
 description="A playground for reasoning",
)
app = playground.get_app()

if __name__ == "__main__":
 asyncio.run(agno_docs.aload(recreate=True))
 playground.serve(app="reasoning_demo:app", reload=True)

# reasoning_tool_agent
# Solve this logic puzzle: A man has to take a fox, a chicken, and a sack of grain across a river.
# The boat is only big enough for the man and one item. If left unattended together,
# the fox will eat the chicken, and the chicken will eat the grain. How can the man get everything across safely?

# knowledge_agent prompt
# What does Paul Graham explain here with respect to need to read?

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys (optional)">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai duckduckgo-search yfinance lancedb sqlalchemy 
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/reasoning_demo.py
 ```

 ```bash Windows
 python cookbook/apps/playground/reasoning_demo.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Teams Demo
Source: https://docs.agno.com/examples/applications/playground/teams_demo

## Code

```python cookbook/apps/playground/teams_demo.py 
from textwrap import dedent
from agno.agent import Agent
from agno.memory.v2 import Memory
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.models.anthropic import Claude
from agno.models.google.gemini import Gemini
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.postgres import PostgresStorage
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.yfinance import YFinanceTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

memory_db = PostgresMemoryDb(table_name="memory", db_url=db_url)

memory = Memory(db=memory_db)

file_agent = Agent(
 name="File Upload Agent",
 agent_id="file-upload-agent",
 role="Answer questions about the uploaded files",
 model=Claude(id="claude-3-7-sonnet-latest"),
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 memory=memory,
 enable_user_memories=True,
 instructions=[
 "You are an AI agent that can analyze files.",
 "You are given a file and you need to answer questions about the file.",
 ],
 show_tool_calls=True,
 markdown=True,
)

video_agent = Agent(
 name="Video Understanding Agent",
 model=Gemini(id="gemini-2.0-flash"),
 agent_id="video-understanding-agent",
 role="Answer questions about video files",
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 memory=memory,
 enable_user_memories=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
)

audio_agent = Agent(
 name="Audio Understanding Agent",
 agent_id="audio-understanding-agent",
 role="Answer questions about audio files",
 model=OpenAIChat(id="gpt-4o-audio-preview"),
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 memory=memory,
 enable_user_memories=True,
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
)

web_agent = Agent(
 name="Web Agent",
 role="Search the web for information",
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 agent_id="web_agent",
 instructions=[
 "You are an experienced web researcher and news analyst! 🔍",
 ],
 memory=memory,
 enable_user_memories=True,
 show_tool_calls=True,
 markdown=True,
 storage=PostgresStorage(
 table_name="web_agent", db_url=db_url, auto_upgrade_schema=True
 ),
)

finance_agent = Agent(
 name="Finance Agent",
 role="Get financial data",
 agent_id="finance_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)
 ],
 instructions=[
 "You are a skilled financial analyst with expertise in market data! 📊",
 "Follow these steps when analyzing financial data:",
 "Start with the latest stock price, trading volume, and daily range",
 "Present detailed analyst recommendations and consensus target prices",
 "Include key metrics: P/E ratio, market cap, 52-week range",
 "Analyze trading patterns and volume trends",
 ],
 memory=memory,
 enable_user_memories=True,
 show_tool_calls=True,
 markdown=True,
)

simple_agent = Agent(
 name="Simple Agent",
 role="Simple agent",
 model=OpenAIChat(id="gpt-4o"),
 instructions=["You are a simple agent"],
 memory=memory,
 enable_user_memories=True,
)

research_agent = Agent(
 name="Research Agent",
 role="Research agent",
 model=OpenAIChat(id="gpt-4o"),
 instructions=["You are a research agent"],
 tools=[DuckDuckGoTools(), ExaTools()],
 agent_id="research_agent",
 memory=memory,
 enable_user_memories=True,
)

research_team = Team(
 name="Research Team",
 description="A team of agents that research the web",
 members=[research_agent, simple_agent],
 model=OpenAIChat(id="gpt-4o"),
 mode="coordinate",
 team_id="research_team",
 success_criteria=dedent("""\
 A comprehensive research report with clear sections and data-driven insights.
 """),
 instructions=[
 "You are the lead researcher of a research team! 🔍",
 ],
 memory=memory,
 enable_user_memories=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
 enable_agentic_context=True,
 storage=PostgresStorage(
 table_name="research_team",
 db_url=db_url,
 mode="team",
 auto_upgrade_schema=True,
 ),
)

multimodal_team = Team(
 name="Multimodal Team",
 description="A team of agents that can handle multiple modalities",
 members=[file_agent, audio_agent, video_agent],
 model=OpenAIChat(id="gpt-4o"),
 mode="route",
 team_id="multimodal_team",
 success_criteria=dedent("""\
 A comprehensive report with clear sections and data-driven insights.
 """),
 instructions=[
 "You are the lead editor of a prestigious financial news desk! 📰",
 ],
 memory=memory,
 enable_user_memories=True,
 storage=PostgresStorage(
 table_name="multimodal_team",
 db_url=db_url,
 mode="team",
 auto_upgrade_schema=True,
 ),
)
financial_news_team = Team(
 name="Financial News Team",
 description="A team of agents that search the web for financial news and analyze it.",
 members=[
 web_agent,
 finance_agent,
 research_agent,
 file_agent,
 audio_agent,
 video_agent,
 ],
 model=OpenAIChat(id="gpt-4o"),
 mode="route",
 team_id="financial_news_team",
 instructions=[
 "You are the lead editor of a prestigious financial news desk! 📰",
 "If you are given a file send it to the file agent.",
 "If you are given an audio file send it to the audio agent.",
 "If you are given a video file send it to the video agent.",
 "Use USD as currency.",
 "If the user is just being conversational, you should respond directly WITHOUT forwarding a task to a member.",
 ],
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
 enable_agentic_context=True,
 show_members_responses=True,
 storage=PostgresStorage(
 table_name="financial_news_team",
 db_url=db_url,
 mode="team",
 auto_upgrade_schema=True,
 ),
 memory=memory,
 enable_user_memories=True,
 expected_output="A good financial news report.",
)

playground = Playground(
 agents=[simple_agent, web_agent, finance_agent, research_agent],
 teams=[research_team, multimodal_team, financial_news_team],
 app_id="teams-demo-playground-app",
 name="Teams Demo Playground",
 description="A playground for teams and agents",
)
app = playground.get_app()

if __name__ == "__main__":
 playground.serve(app="teams_demo:app", reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export ANTHROPIC_API_KEY=xxx
 export GOOGLE_API_KEY=xxx
 export EXA_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno "uvicorn[standard]" openai anthropic google-generativeai duckduckgo-search exa-py yfinance psycopg-binary
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/teams_demo.py
 ```

 ```bash Windows
 python cookbook/apps/playground/teams_demo.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Upload Files
Source: https://docs.agno.com/examples/applications/playground/upload_files

## Code

```python cookbook/apps/playground/upload_files.py 
from agno.agent import Agent
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.docx import DocxKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.models.google.gemini import Gemini
from agno.models.openai import OpenAIChat
from agno.playground import Playground
from agno.storage.postgres import PostgresStorage
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = CombinedKnowledgeBase(
 sources=[
 PDFKnowledgeBase(
 vector_db=PgVector(table_name="recipes_pdf", db_url=db_url), path=""
 ),
 CSVKnowledgeBase(
 vector_db=PgVector(table_name="recipes_csv", db_url=db_url), path=""
 ),
 DocxKnowledgeBase(
 vector_db=PgVector(table_name="recipes_docx", db_url=db_url), path=""
 ),
 JSONKnowledgeBase(
 vector_db=PgVector(table_name="recipes_json", db_url=db_url), path=""
 ),
 TextKnowledgeBase(
 vector_db=PgVector(table_name="recipes_text", db_url=db_url), path=""
 ),
 ],
 vector_db=PgVector(table_name="recipes_combined", db_url=db_url),
)

file_agent = Agent(
 name="File Upload Agent",
 agent_id="file-upload-agent",
 role="Answer questions about the uploaded files",
 model=OpenAIChat(id="gpt-4o-mini"),
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 knowledge=knowledge_base,
 show_tool_calls=True,
 markdown=True,
)

audio_agent = Agent(
 name="Audio Understanding Agent",
 agent_id="audio-understanding-agent",
 role="Answer questions about audio files",
 model=OpenAIChat(id="gpt-4o-audio-preview"),
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
)

video_agent = Agent(
 name="Video Understanding Agent",
 model=Gemini(id="gemini-2.0-flash"),
 agent_id="video-understanding-agent",
 role="Answer questions about video files",
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 add_history_to_messages=True,
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
)

playground = Playground(
 agents=[file_agent, audio_agent, video_agent],
 name="Upload Files Playground",
 description="Upload files and ask questions about them",
 app_id="upload-files-playground",
)
app = playground.get_app()

if __name__ == "__main__":
 playground.serve(app="upload_files:app", reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash

 pip install -U agno "uvicorn[standard]" openai google-generativeai psycopg-binary

 pip install -U "agno[pdf,csv,docx,json,text]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/playground/upload_files.py
 ```

 ```bash Windows
 python cookbook/apps/playground/upload_files.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with User Memory
Source: https://docs.agno.com/examples/applications/slack/agent_with_user_memory

## Code

```python cookbook/apps/slack/agent_with_user_memory.py
from textwrap import dedent
from agno.agent import Agent
from agno.app.slack.app import SlackAPI
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.manager import MemoryManager
from agno.memory.v2.memory import Memory
from agno.models.anthropic.claude import Claude
from agno.storage.sqlite import SqliteStorage
from agno.tools.googlesearch import GoogleSearchTools

agent_storage = SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
)
memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(
 db=memory_db,
 memory_manager=MemoryManager(
 memory_capture_instructions="""\
 Collect User's name,
 Collect Information about user's passion and hobbies,
 Collect Information about the users likes and dislikes,
 Collect information about what the user is doing with their life right now
 """,
 model=Claude(id="claude-3-5-sonnet-20241022"),
 ),
)

# Reset the memory for this example
memory.clear()

personal_agent = Agent(
 name="Basic Agent",
 model=Claude(id="claude-sonnet-4-20250514"),
 tools=[GoogleSearchTools()],
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
 memory=memory,
 enable_user_memories=True,
 instructions=dedent("""
 You are a personal AI friend in a slack chat, your purpose is to chat with the user about things and make them feel good.
 First introduce yourself and ask for their name then, ask about themeselves, their hobbies, what they like to do and what they like to talk about.
 Use Google Search tool to find latest infromation about things in the conversations
 You may sometimes recieve messages prepenned with group message when that is the message then reply to whole group instead of treating them as from a single user
 """),
 debug_mode=True,
 add_state_in_messages=True,
)

slack_api_app = SlackAPI(
 agent=personal_agent,
 name="Agent with User Memory",
 app_id="agent_with_user_memory",
 description="A agent with user memory that can chat with the user about things and make them feel good.",
)
app = slack_api_app.get_app()

if __name__ == "__main__":
 slack_api_app.serve("agent_with_user_memory:app", port=8000, reload=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/slack/agent_with_user_memory.py
 ```

 ```bash Windows
 python cookbook/apps/slack/agent_with_user_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic
Source: https://docs.agno.com/examples/applications/slack/basic

## Code

```python cookbook/apps/slack/basic.py
from agno.agent import Agent
from agno.app.slack.app import SlackAPI
from agno.models.openai import OpenAIChat

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
)

slack_api_app = SlackAPI(
 agent=basic_agent,
 name="Basic Agent",
 app_id="basic_agent",
 description="A basic agent that can answer questions and help with tasks.",
)
app = slack_api_app.get_app()

if __name__ == "__main__":
 slack_api_app.serve("basic:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/slack/basic.py
 ```

 ```bash Windows
 python cookbook/apps/slack/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Agent
Source: https://docs.agno.com/examples/applications/slack/reasoning_agent

## Code

```python cookbook/apps/slack/reasoning_agent.py
from agno.agent import Agent
from agno.app.slack.app import SlackAPI
from agno.models.anthropic.claude import Claude
from agno.tools.thinking import ThinkingTools
from agno.tools.yfinance import YFinanceTools

reasoning_finance_agent = Agent(
 name="Reasoning Finance Agent",
 model=Claude(id="claude-3-7-sonnet-latest"),
 tools=[
 ThinkingTools(add_instructions=True),
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 ),
 ],
 instructions="Use tables to display data. When you use thinking tools, keep the thinking brief.",
 add_datetime_to_instructions=True,
 markdown=True,
)

slack_api_app = SlackAPI(
 agent=reasoning_finance_agent,
 name="Reasoning Finance Agent",
 app_id="reasoning_finance_agent",
 description="A agent that can reason about finance and stock prices.",
)
app = slack_api_app.get_app()

if __name__ == "__main__":
 slack_api_app.serve("reasoning_agent:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/slack/reasoning_agent.py
 ```

 ```bash Windows
 python cookbook/apps/slack/reasoning_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent With Media
Source: https://docs.agno.com/examples/applications/whatsapp/agent_with_media

This example shows how to use the files with whatsapp app.

## Code

```python cookbook/apps/whatsapp/agent_with_media.py
from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.models.google import Gemini

media_agent = Agent(
 name="Media Agent",
 model=Gemini(id="gemini-2.0-flash"),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
)

whatsapp_app = WhatsappAPI(
 agent=media_agent,
 name="Media Agent",
 app_id="media_agent",
 description="A agent that can send media to the user.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="agent_with_media:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/agent_with_media.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/agent_with_media.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent With User Memory
Source: https://docs.agno.com/examples/applications/whatsapp/agent_with_user_memory

This example shows how to use memory with whatsapp app.

## Code

```python cookbook/apps/whatsapp/agent_with_user_memory.py
from textwrap import dedent

from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.manager import MemoryManager
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.sqlite import SqliteStorage
from agno.tools.googlesearch import GoogleSearchTools

agent_storage = SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
)
memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(
 db=memory_db,
 memory_manager=MemoryManager(
 memory_capture_instructions="""\
 Collect User\'s name,
 Collect Information about user\'s passion and hobbies,
 Collect Information about the users likes and dislikes,
 Collect information about what the user is doing with their life right now
 """,
 model=Gemini(id="gemini-2.0-flash"),
 ),
)

# Reset the memory for this example
memory.clear()

personal_agent = Agent(
 name="Basic Agent",
 model=Gemini(id="gemini-2.0-flash"),
 tools=[GoogleSearchTools()],
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
 memory=memory,
 enable_agentic_memory=True,
 instructions=dedent("""
 You are a personal AI friend of the user, your purpose is to chat with the user about things and make them feel good.
 First introduce yourself and ask for their name then, ask about themeselves, their hobbies, what they like to do and what they like to talk about.
 Use Google Search tool to find latest infromation about things in the conversations
 """),
 debug_mode=True,
)

whatsapp_app = WhatsappAPI(
 agent=personal_agent,
 name="Agent with User Memory",
 app_id="agent_with_user_memory",
 description="A agent that can chat with the user about things and make them feel good.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="agent_with_user_memory:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai google-api-python-client "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/agent_with_user_memory.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/agent_with_user_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic
Source: https://docs.agno.com/examples/applications/whatsapp/basic

## Code

```python cookbook/apps/whatsapp/basic.py
from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.models.openai import OpenAIChat

basic_agent = Agent(
 name="Basic Agent",
 model=OpenAIChat(id="gpt-4o"),
 add_history_to_messages=True,
 num_history_responses=3,
 add_datetime_to_instructions=True,
 markdown=True,
)

whatsapp_app = WhatsappAPI(
 agent=basic_agent,
 name="Basic Agent",
 app_id="basic_agent",
 description="A basic agent that can answer questions and help with tasks.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="basic:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/basic.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Generation Model
Source: https://docs.agno.com/examples/applications/whatsapp/image_generation_model

This example shows how to use the image generation model to generate images with whatsapp app.

## Code

```python cookbook/apps/whatsapp/image_generation_model.py
from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.models.google import Gemini

image_agentg = Agent(
 model=Gemini(
 id="gemini-2.0-flash-exp-image-generation",
 response_modalities=["Text", "Image"],
 ),
 debug_mode=True,
)

whatsapp_app = WhatsappAPI(
 agent=image_agent,
 name="Image Generation Model",
 app_id="image_generation_model",
 description="A model that generates images using the Gemini API.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="image_generation_model:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/image_generation_model.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/image_generation_model.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Generation Tools
Source: https://docs.agno.com/examples/applications/whatsapp/image_generation_tools

this example shows how to use the openai tools to generate images with whatsapp app.

## Code

```python cookbook/apps/whatsapp/image_generation_tools.py
from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.models.openai import OpenAIChat
from agno.tools.openai import OpenAITools

image_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[OpenAITools(image_model="gpt-image-1")],
 markdown=True,
 show_tool_calls=True,
 debug_mode=True,
 add_history_to_messages=True,
)

whatsapp_app = WhatsappAPI(
 agent=image_agent,
 name="Image Generation Tools",
 app_id="image_generation_tools",
 description="A tool that generates images using the OpenAI API.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="image_generation_tools:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/image_generation_tools.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/image_generation_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Agent
Source: https://docs.agno.com/examples/applications/whatsapp/reasoning_agent

This example shows how to use the reasoning with whatsapp app.

## Code

```python cookbook/apps/whatsapp/reasoning_agent.py
from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.models.anthropic.claude import Claude
from agno.tools.thinking import ThinkingTools
from agno.tools.yfinance import YFinanceTools

reasoning_finance_agent = Agent(
 name="Reasoning Finance Agent",
 model=Claude(id="claude-3-7-sonnet-latest"),
 tools=[
 ThinkingTools(add_instructions=True),
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 ),
 ],
 instructions="Use tables to display data. When you use thinking tools, keep the thinking brief.",
 add_datetime_to_instructions=True,
 markdown=True,
)

whatsapp_app = WhatsappAPI(
 agent=reasoning_finance_agent,
 name="Reasoning Finance Agent",
 app_id="reasoning_finance_agent",
 description="A finance agent that uses tables to display data and reasoning tools to reason about the data.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="reasoning_agent:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export ANTHROPIC_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno anthropic yfinance "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/reasoning_agent.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/reasoning_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Study Friend
Source: https://docs.agno.com/examples/applications/whatsapp/study_friend

## Code

```python cookbook/apps/whatsapp/study_friend.py
from textwrap import dedent

from agno.agent import Agent
from agno.app.whatsapp.app import WhatsappAPI
from agno.memory import memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.manager import MemoryManager
from agno.memory.v2.memory import Memory
from agno.models.google import Gemini
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.youtube import YouTubeTools

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(
 db=memory_db,
 memory_manager=MemoryManager(
 memory_capture_instructions="""\
 - Collect Information about the user\'s career and acaedemic goals
 - Collect Information about the user\'s previous acaedemic and learning experiences
 - Collect Information about the user\'s current knowledge
 - Collect Information about the user\'s hobbies and passions
 - Collect Information about the user\'s likes and dislikes
 """,
 ),
)

StudyBuddy = Agent(
 name="StudyBuddy",
 memory=memory,
 model=Gemini("gemini-2.0-flash"),
 enable_user_memories=True,
 storage=SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
 ),
 tools=[DuckDuckGoTools(), YouTubeTools()],
 description=dedent("""\
 You are StudyBuddy, an expert educational mentor with deep expertise in personalized learning! 📚

 Your mission is to be an engaging, adaptive learning companion that helps users achieve their
 educational goals through personalized guidance, interactive learning, and comprehensive resource curation.
 """),
 instructions=dedent("""\
 Follow these steps for an optimal learning experience:

 1. Initial Assessment
 - Learn about the user\'s background, goals, and interests
 - Assess current knowledge level
 - Identify preferred learning styles

 2. Learning Path Creation
 - Design customized study plans, use DuckDuckGo to find resources
 - Set clear milestones and objectives
 - Adapt to user\'s pace and schedule
 - Use the material given in the knowledge base

 3. Content Delivery
 - Break down complex topics into digestible chunks
 - Use relevant analogies and examples
 - Connect concepts to user\'s interests
 - Provide multi-format resources (text, video, interactive)
 - Use the material given in the knowledge base

 4. Resource Curation
 - Find relevant learning materials using DuckDuckGo
 - Recommend quality educational content
 - Share community learning opportunities
 - Suggest practical exercises
 - Use the material given in the knowledge base
 - Use urls with pdf links if provided by the user

 5. Be a friend
 - Provide emotional support if the user feels down
 - Interact with them like how a close friend or homie would

 Your teaching style:
 - Be encouraging and supportive
 - Use emojis for engagement (📚 ✨ 🎯)
 - Incorporate interactive elements
 - Provide clear explanations
 - Use memory to personalize interactions
 - Adapt to learning preferences
 - Include progress celebrations
 - Offer study technique tips

 Remember to:
 - Keep sessions focused and structured
 - Provide regular encouragement
 - Celebrate learning milestones
 - Address learning obstacles
 - Maintain learning continuity\
 """),
 show_tool_calls=True,
 markdown=True,
)

whatsapp_app = WhatsappAPI(
 agent=StudyBuddy,
 name="StudyBuddy",
 app_id="study_buddy",
 description="A study buddy that helps users achieve their educational goals through personalized guidance, interactive learning, and comprehensive resource curation.",
)

app = whatsapp_app.get_app()

if __name__ == "__main__":
 whatsapp_app.serve(app="study_friend:app", port=8000, reload=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai duckduckgo-search youtube-search-python "uvicorn[standard]"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/apps/whatsapp/study_friend.py
 ```

 ```bash Windows
 python cookbook/apps/whatsapp/study_friend.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Async
Source: https://docs.agno.com/examples/concepts/async/basic

## Code

```python cookbook/agent_concepts/async/basic.py
import asyncio

from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description="You help people with their health and fitness goals.",
 instructions=["Recipes should be under 5 ingredients"],
 markdown=True,
)
# -*- Print a response to the cli
asyncio.run(agent.aprint_response("Share a breakfast recipe.", stream=True))
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/async/basic.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/async/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Data Analyst
Source: https://docs.agno.com/examples/concepts/async/data_analyst

## Code

```python cookbook/agent_concepts/async/data_analyst.py
import asyncio
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckdb import DuckDbTools

duckdb_tools = DuckDbTools(
 create_tables=False, export_tables=False, summarize_tables=False
)
duckdb_tools.create_table_from_path(
 path="https://agno-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
 table="movies",
)

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[duckdb_tools],
 markdown=True,
 show_tool_calls=True,
 additional_context=dedent("""\
 You have access to the following tables:
 - movies: contains information about movies from IMDB.
 """),
)
asyncio.run(
 agent.aprint_response("What is the average rating of movies?", stream=False)
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno duckdb
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/async/data_analyst.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/async/data_analyst.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Gather Multiple Agents
Source: https://docs.agno.com/examples/concepts/async/gather_agents

## Code

```python cookbook/agent_concepts/async/gather_agents.py
import asyncio

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from rich.pretty import pprint

providers = ["openai", "anthropic", "ollama", "cohere", "google"]
instructions = [
 "Your task is to write a well researched report on AI providers.",
 "The report should be unbiased and factual.",
]

async def get_reports():
 tasks = []
 for provider in providers:
 agent = Agent(
 model=OpenAIChat(id="gpt-4"),
 instructions=instructions,
 tools=[DuckDuckGoTools()],
 )
 tasks.append(
 agent.arun(f"Write a report on the following AI provider: {provider}")
 )

 results = await asyncio.gather(*tasks)
 return results

async def main():
 results = await get_reports()
 for result in results:
 print("************")
 pprint(result.content)
 print("************")
 print("\n")

if __name__ == "__main__":
 asyncio.run(main())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno rich duckduckgo-
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/async/gather_agents.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/async/gather_agents.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Agent
Source: https://docs.agno.com/examples/concepts/async/reasoning

## Code

```python cookbook/agent_concepts/async/reasoning.py
import asyncio

from agno.agent import Agent
from agno.cli.console import console
from agno.models.openai import OpenAIChat

task = "9.11 and 9.9 -- which is bigger?"

regular_agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True)
reasoning_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning=True,
 markdown=True,
)

console.rule("[bold green]Regular Agent[/bold green]")
asyncio.run(regular_agent.aprint_response(task, stream=True))
console.rule("[bold yellow]Reasoning Agent[/bold yellow]")
asyncio.run(
 reasoning_agent.aprint_response(task, stream=True, show_full_reasoning=True)
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/async/reasoning.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/async/reasoning.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Structured Outputs
Source: https://docs.agno.com/examples/concepts/async/structured_output

## Code

```python cookbook/agent_concepts/async/structured_output.py
import asyncio
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIChat
from pydantic import BaseModel, Field
from rich.pretty import pprint # noqa

class MovieScript(BaseModel):
 setting: str = Field(
 ..., description="Provide a nice setting for a blockbuster movie."
 )
 ending: str = Field(
 ...,
 description="Ending of the movie. If not available, provide a happy ending.",
 )
 genre: str = Field(
 ...,
 description="Genre of the movie. If not available, select action, thriller or romantic comedy.",
 )
 name: str = Field(..., description="Give a name to this movie")
 characters: List[str] = Field(..., description="Name of characters for this movie.")
 storyline: str = Field(
 ..., description="3 sentence storyline for the movie. Make it exciting!"
 )

# Agent that uses JSON mode
json_mode_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

# Agent that uses structured outputs
structured_output_agent = Agent(
 model=OpenAIChat(id="gpt-4o-2024-08-06"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

asyncio.run(json_mode_agent.aprint_response("New York"))
asyncio.run(structured_output_agent.aprint_response("New York"))
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/async/structured_output.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/async/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Add Context
Source: https://docs.agno.com/examples/concepts/context/01-add_context

This example demonstrates how to create a context-aware agent that can access real-time data from HackerNews.

## Code

```python cookbook/agent_concepts/context/01-add_context.py
import json
from textwrap import dedent

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_top_hackernews_stories(num_stories: int = 5) -> str:
 """Fetch and return the top stories from HackerNews.

 Args:
 num_stories: Number of top stories to retrieve (default: 5)
 Returns:
 JSON string containing story details (title, url, score, etc.)
 """
 # Get top stories
 stories = [
 {
 k: v
 for k, v in httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
 )
 .json()
 .items()
 if k != "kids" # Exclude discussion threads
 }
 for id in httpx.get(
 "https://hacker-news.firebaseio.com/v0/topstories.json"
 ).json()[:num_stories]
 ]
 return json.dumps(stories, indent=4)

# Create a Context-Aware Agent that can access real-time HackerNews data
agent = Agent(
 model=OpenAIChat(id="gpt-4"),
 # Each function in the context is resolved when the agent is run,
 # think of it as dependency injection for Agents
 context={"top_hackernews_stories": get_top_hackernews_stories},
 # We can add the entire context dictionary to the user message
 add_context=True,
 markdown=True,
)

# Example usage
agent.print_response(
 "Summarize the top stories on HackerNews and identify any interesting trends.",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno httpx
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/context/01-add_context.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/context/01-add_context.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent Context
Source: https://docs.agno.com/examples/concepts/context/02-agent_context

## Code

```python cookbook/agent_concepts/context/02-agent_context.py
import json
from textwrap import dedent

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_top_hackernews_stories(num_stories: int = 5) -> str:
 """Fetch and return the top stories from HackerNews.

 Args:
 num_stories: Number of top stories to retrieve (default: 5)
 Returns:
 JSON string containing story details (title, url, score, etc.)
 """
 # Get top stories
 stories = [
 {
 k: v
 for k, v in httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
 )
 .json()
 .items()
 if k != "kids" # Exclude discussion threads
 }
 for id in httpx.get(
 "https://hacker-news.firebaseio.com/v0/topstories.json"
 ).json()[:num_stories]
 ]
 return json.dumps(stories, indent=4)

# Create a Context-Aware Agent that can access real-time HackerNews data
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 # Each function in the context is evaluated at runtime
 context={"top_hackernews_stories": get_top_hackernews_stories},
 # Alternatively, you can manually add the context to the instructions
 instructions=dedent("""\
 You are an insightful tech trend observer! 📰

 Here are the top stories on HackerNews:
 {top_hackernews_stories}\
 """),
 # add_state_in_messages will make the `top_hackernews_stories` variable
 # available in the instructions
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response(
 "Summarize the top stories on HackerNews and identify any interesting trends.",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno httpx
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/context/02-agent_context.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/context/02-agent_context.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Context In Instructions
Source: https://docs.agno.com/examples/concepts/context/03-context_in_instructions

## Code

```python cookbook/agent_concepts/context/03-context_in_instructions.py
import json
from textwrap import dedent

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_upcoming_spacex_launches(num_launches: int = 5) -> str:
 url = "https://api.spacexdata.com/v5/launches/upcoming"
 launches = httpx.get(url).json()
 launches = sorted(launches, key=lambda x: x["date_unix"])[:num_launches]
 return json.dumps(launches, indent=4)

# Create an Agent that has access to real-time SpaceX data
agent = Agent(
 model=OpenAIChat(id="gpt-4.1"),
 # Each function in the context is evaluated at runtime
 context={"upcoming_spacex_launches": get_upcoming_spacex_launches},
 description=dedent("""\
 You are a cosmic analyst and spaceflight enthusiast. 🚀

 Here are the next SpaceX launches:
 {upcoming_spacex_launches}\
 """),
 # add_state_in_messages will make the `upcoming_spacex_launches` variable
 # available in the description and instructions
 add_state_in_messages=True,
 markdown=True,
)

agent.print_response(
 "Tell me about the upcoming SpaceX missions.",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno httpx
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/context/03-context_in_instructions.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/context/03-context_in_instructions.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Azure OpenAI Embedder
Source: https://docs.agno.com/examples/concepts/embedders/azure-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = AzureOpenAIEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="azure_openai_embeddings",
 embedder=AzureOpenAIEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export AZURE_EMBEDDER_OPENAI_API_KEY=xxx
 export AZURE_EMBEDDER_OPENAI_ENDPOINT=xxx
 export AZURE_EMBEDDER_DEPLOYMENT=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector openai agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/azure_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/azure_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Cohere Embedder
Source: https://docs.agno.com/examples/concepts/embedders/cohere-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.cohere import CohereEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = CohereEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)
# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="cohere_embeddings",
 embedder=CohereEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export COHERE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector cohere agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/cohere_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/cohere_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Fireworks Embedder
Source: https://docs.agno.com/examples/concepts/embedders/fireworks-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.fireworks import FireworksEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = FireworksEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="fireworks_embeddings",
 embedder=FireworksEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export FIREWORKS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector fireworks-ai agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/fireworks_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/fireworks_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Gemini Embedder
Source: https://docs.agno.com/examples/concepts/embedders/gemini-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.google import GeminiEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = GeminiEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="gemini_embeddings",
 embedder=GeminiEmbedder(dimensions=1536),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector google-generativeai agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/gemini_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/gemini_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Huggingface Embedder
Source: https://docs.agno.com/examples/concepts/embedders/huggingface-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.huggingface import HuggingfaceCustomEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = HuggingfaceCustomEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="huggingface_embeddings",
 embedder=HuggingfaceCustomEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export HUGGINGFACE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector huggingface-hub agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/huggingface_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/huggingface_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Mistral Embedder
Source: https://docs.agno.com/examples/concepts/embedders/mistral-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.mistral import MistralEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = MistralEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="mistral_embeddings",
 embedder=MistralEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export MISTRAL_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector mistralai agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/mistral_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/mistral_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Ollama Embedder
Source: https://docs.agno.com/examples/concepts/embedders/ollama-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.ollama import OllamaEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = OllamaEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="ollama_embeddings",
 embedder=OllamaEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the installation instructions at [Ollama's website](https://ollama.ai)
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/ollama_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/ollama_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# OpenAI Embedder
Source: https://docs.agno.com/examples/concepts/embedders/openai-embedder

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.openai import OpenAIEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = OpenAIEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="openai_embeddings",
 embedder=OpenAIEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector openai agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/openai_embedder.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/openai_embedder.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Qdrant FastEmbed Embedder
Source: https://docs.agno.com/examples/concepts/embedders/qdrant-fastembed

## Code

```python
from agno.agent import AgentKnowledge
from agno.embedder.fastembed import FastEmbedEmbedder
from agno.vectordb.pgvector import PgVector

embeddings = FastEmbedEmbedder().get_embedding(
 "The quick brown fox jumps over the lazy dog."
)

# Print the embeddings and their dimensions
print(f"Embeddings: {embeddings[:5]}")
print(f"Dimensions: {len(embeddings)}")

# Example usage:
knowledge_base = AgentKnowledge(
 vector_db=PgVector(
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 table_name="qdrant_embeddings",
 embedder=FastEmbedEmbedder(),
 ),
 num_documents=2,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector fastembed agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/embedders/qdrant_fastembed.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/embedders/qdrant_fastembed.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# LanceDB Hybrid 
Source: https://docs.agno.com/examples/concepts/hybrid-search/lancedb

## Code

```python cookbook/agent_concepts/knowledge/vector_dbs/lance_db/lance_db_hybrid_search.py
from typing import Optional

import typer
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from rich.prompt import Prompt

vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb",
 search_type=SearchType.hybrid,
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

def lancedb_agent(user: str = "user"):
 agent = Agent(
 user_id=user,
 knowledge=knowledge_base,
 search_knowledge=True,
 )

 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in ("exit", "bye"):
 break
 agent.print_response(message)

if __name__ == "__main__":
 # Comment out after first run
 knowledge_base.load(recreate=False)

 typer.run(lancedb_agent)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U lancedb tantivy pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/vector_dbs/lance_db/lance_db_hybrid_search.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/vector_dbs/lance_db/lance_db_hybrid_search.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# MilvusDB Hybrid 
Source: https://docs.agno.com/examples/concepts/hybrid-search/milvusdb

## Code

```python cookbook/agent_concepts/knowledge/vector_dbs/milvus_db/milvus_db_hybrid_search.py
import typer
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.milvus import Milvus, SearchType
from rich.prompt import Prompt

vector_db = Milvus(
 collection="recipes", uri="tmp/milvus.db", search_type=SearchType.hybrid
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

def milvusdb_agent(user: str = "user"):
 agent = Agent(
 user_id=user,
 knowledge=knowledge_base,
 search_knowledge=True,
 )

 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in ("exit", "bye"):
 break
 agent.print_response(message)

if __name__ == "__main__":
 # Comment out after first run
 knowledge_base.load(recreate=True)

 typer.run(milvusdb_agent)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U pymilvus tantivy pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/vector_dbs/milvus_db/milvus_db_hybrid_search.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/vector_dbs/milvus_db/milvus_db_hybrid_search.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# MongoDB Hybrid 
Source: https://docs.agno.com/examples/concepts/hybrid-search/mongodb

## Code

```python cookbook/agent_concepts/knowledge/vector_dbs/mongo_db/mongo_db_hybrid_search.py
import typer
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.mongodb import MongoDb
from agno.vectordb.search import SearchType
from rich.prompt import Prompt

# MongoDB Atlas connection string
"""
Example connection strings:
"mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
"mongodb://localhost:27017/agno?authSource=admin"
"""
mdb_connection_string = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"

vector_db = MongoDb(
 collection_name="recipes",
 db_url=mdb_connection_string,
 search_index_name="recipes",
 search_type=SearchType.hybrid
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

def mongodb_agent(user: str = "user"):
 agent = Agent(
 user_id=user,
 knowledge=knowledge_base,
 search_knowledge=True,
 )

 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in ("exit", "bye"):
 break
 agent.print_response(message)

if __name__ == "__main__":
 # Comment out after first run
 knowledge_base.load(recreate=True)

 typer.run(mongodb_agent)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U pymongo tantivy pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/vector_dbs/mongo_db/mongo_db_hybrid_search.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/vector_dbs/mongo_db/mongo_db_hybrid_search.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PgVector Hybrid 
Source: https://docs.agno.com/examples/concepts/hybrid-search/pgvector

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.pgvector import PgVector, SearchType

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes", db_url=db_url, search_type=SearchType.hybrid
 ),
)
# Load the knowledge base: Comment out after first run
knowledge_base.load(recreate=False)

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 search_knowledge=True,
 read_chat_history=True,
 markdown=True,
)
agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
agent.print_response("What was my last question?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U pgvector pypdf "psycopg[binary]" sqlalchemy openai agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 ./cookbook/scripts/run_pgvector.sh
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/hybrid_search/pgvector/agent.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/hybrid_search/pgvector/agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# QdrantDB Hybrid 
Source: https://docs.agno.com/examples/concepts/hybrid-search/qdrantdb

## Code

```python cookbook/agent_concepts/knowledge/vector_dbs/qdrant_db/qdrant_db_hybrid_search.py
from typing import Optional

import typer
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.qdrant import Qdrant
from rich.prompt import Prompt

COLLECTION_NAME = "thai-recipes"

vector_db = Qdrant(collection=COLLECTION_NAME, url="http://localhost:6333", search_type=SearchType.hybrid)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

def qdrantdb_agent(user: str = "user"):
 agent = Agent(
 user_id=user,
 knowledge=knowledge_base,
 search_knowledge=True,
 )

 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in ("exit", "bye"):
 break
 agent.print_response(message)

if __name__ == "__main__":
 # Comment out after first run
 knowledge_base.load(recreate=True)

 typer.run(qdrantdb_agent)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U qdrant-client fastembed tantivy pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/vector_dbs/qdrant_db/qdrant_db_hybrid_search.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/vector_dbs/qdrant_db/qdrant_db_hybrid_search.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Weaviate Hybrid 
Source: https://docs.agno.com/examples/concepts/hybrid-search/weaviate

## Code

```python cookbook/agent_concepts/knowledge/vector_dbs/weaviate_db/weaviate_db_hybrid_search.py
import typer
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate
from rich.prompt import Prompt

vector_db = Weaviate(
 collection="recipes",
 search_type=SearchType.hybrid,
 vector_index=VectorIndex.HNSW,
 distance=Distance.COSINE,
 local=False, # Set to True if using Weaviate Cloud and False if using local instance
 hybrid_search_alpha=0.6, # Adjust alpha for hybrid search (0.0-1.0, default is 0.5), where 0 is pure keyword search, 1 is pure vector 
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

def weaviate_agent(user: str = "user"):
 agent = Agent(
 user_id=user,
 knowledge=knowledge_base,
 search_knowledge=True,
 )

 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in ("exit", "bye"):
 break
 agent.print_response(message)

if __name__ == "__main__":
 # Comment out after first run
 knowledge_base.load(recreate=True)

 typer.run(weaviate_agent)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U weaviate-client tantivy pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/vector_dbs/weaviate_db/weaviate_db_hybrid_search.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/vector_dbs/weaviate_db/weaviate_db_hybrid_search.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# ArXiv Knowledge Base
Source: https://docs.agno.com/examples/concepts/knowledge/arxiv-kb

## Code

```python
from agno.agent import Agent
from agno.knowledge.arxiv import ArxivKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create a knowledge base with the ArXiv documents
knowledge_base = ArxivKnowledgeBase(
 queries=["Generative AI", "Machine Learning"],
 # Table name: ai.arxiv_documents
 vector_db=PgVector(
 table_name="arxiv_documents",
 db_url=db_url,
 ),
)
# Load the knowledge base
knowledge_base.load(recreate=False)

# Create an agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

# Ask the agent about the knowledge base
agent.print_response(
 "Ask me about generative ai from the knowledge base", markdown=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/arxiv_kb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/arxiv_kb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Combined Knowledge Base
Source: https://docs.agno.com/examples/concepts/knowledge/combined-kb

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.csv import CSVKnowledgeBase
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create CSV knowledge base
csv_kb = CSVKnowledgeBase(
 path=Path("data/csvs"),
 vector_db=PgVector(
 table_name="csv_documents",
 db_url=db_url,
 ),
)

# Create PDF URL knowledge base
pdf_url_kb = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="pdf_documents",
 db_url=db_url,
 ),
)

# Create Website knowledge base
website_kb = WebsiteKnowledgeBase(
 urls=["https://docs.agno.com/introduction"],
 max_links=10,
 vector_db=PgVector(
 table_name="website_documents",
 db_url=db_url,
 ),
)

# Create Local PDF knowledge base
local_pdf_kb = PDFKnowledgeBase(
 path="data/pdfs",
 vector_db=PgVector(
 table_name="pdf_documents",
 db_url=db_url,
 ),
)

# Combine knowledge bases
knowledge_base = CombinedKnowledgeBase(
 sources=[
 csv_kb,
 pdf_url_kb,
 website_kb,
 local_pdf_kb,
 ],
 vector_db=PgVector(
 table_name="combined_documents",
 db_url=db_url,
 ),
)

# Initialize the Agent with the combined knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

knowledge_base.load(recreate=False)

# Use the agent
agent.print_response("Ask me about something from the knowledge base", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector pypdf agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/combined_kb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/combined_kb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# CSV Knowledge Base
Source: https://docs.agno.com/examples/concepts/knowledge/csv-kb

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.csv import CSVKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = CSVKnowledgeBase(
 path=Path("data/csvs"),
 vector_db=PgVector(
 table_name="csv_documents",
 db_url=db_url,
 ),
 num_documents=5, # Number of documents to return on 
)
# Load the knowledge base
knowledge_base.load(recreate=False)

# Initialize the Agent with the knowledge_base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

# Use the agent
agent.print_response("Ask me about something from the knowledge base", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/csv_kb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/csv_kb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# CSV URL Knowledge Base
Source: https://docs.agno.com/examples/concepts/knowledge/csv-url-kb

## Code

```python
from agno.agent import Agent
from agno.knowledge.csv_url import CSVUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = CSVUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/csvs/employees.csv"],
 vector_db=PgVector(table_name="csv_documents", db_url=db_url),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "What is the average salary of employees in the Marketing department?",
 markdown=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/csv_url_kb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/csv_url_kb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Document Knowledge Base
Source: https://docs.agno.com/examples/concepts/knowledge/doc-kb

## Code

```python
from agno.agent import Agent
from agno.document.base import Document
from agno.knowledge.document import DocumentKnowledgeBase
from agno.vectordb.pgvector import PgVector

fun_facts = """
- Earth is the third planet from the Sun and the only known astronomical object to support life.
- Approximately 71% of Earth's surface is covered by water, with the Pacific Ocean being the largest.
- The Earth's atmosphere is composed mainly of nitrogen (78%) and oxygen (21%), with traces of other gases.
- Earth rotates on its axis once every 24 hours, leading to the cycle of day and night.
- The planet has one natural satellite, the Moon, which influences tides and stabilizes Earth's axial tilt.
- Earth's tectonic plates are constantly shifting, leading to geological activities like earthquakes and volcanic eruptions.
- The highest point on Earth is Mount Everest, standing at 8,848 meters (29,029 feet) above sea level.
- The deepest part of the ocean is the Mariana Trench, reaching depths of over 11,000 meters (36,000 feet).
- Earth has a diverse range of ecosystems, from rainforests and deserts to coral reefs and tundras.
- The planet's magnetic field protects life by deflecting harmful solar radiation and cosmic rays.
"""

# Load documents from the data/docs directory
documents = [Document(content=fun_facts)]

# Database connection URL
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create a knowledge base with the loaded documents
knowledge_base = DocumentKnowledgeBase(
 documents=documents,
 vector_db=PgVector(
 table_name="documents",
 db_url=db_url,
 ),
)

# Load the knowledge base
knowledge_base.load(recreate=False)

# Create an agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
)

# Ask the agent about the knowledge base
agent.print_response(
 "Ask me about something from the knowledge base about earth", markdown=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/doc_kb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/doc_kb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# DOCX Knowledge Base
Source: https://docs.agno.com/examples/concepts/knowledge/docx-kb

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.docx import DocxKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create a knowledge base with the DOCX files from the data/docs directory
knowledge_base = DocxKnowledgeBase(
 path=Path("data/docs"),
 vector_db=PgVector(
 table_name="docx_documents",
 db_url=db_url,
 ),
)
# Load the knowledge base
knowledge_base.load(recreate=False)

# Create an agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

# Ask the agent about the knowledge base
agent.print_response("Ask me about something from the knowledge base", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy 'psycopg[binary]' pgvector python-docx agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/docx_kb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/docx_kb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic filtering with Docx
Source: https://docs.agno.com/examples/concepts/knowledge/filters/docx/agentic_filtering

Learn how to do agentic knowledge filtering using Docx documents with user-specific metadata.

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.docx import DocxKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.DOCX
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = DocxKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with Agent using filters from query automatically
# -----------------------------------------------------------------------------------

# Enable agentic filtering
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 enable_agentic_knowledge_filters=True,
)

# Query for Jordan Mitchell's experience and skills with filters in query so that Agent can automatically pick them up
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills with jordan_mitchell as user id and document type cv",
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/docx/agentic_filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/docx/agentic_filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering with Docx
Source: https://docs.agno.com/examples/concepts/knowledge/filters/docx/filtering

Learn how to filter knowledge base searches using Docx documents with user-specific metadata.

## Code

```python
"""
User-Level Knowledge Filtering Example

This cookbook demonstrates how to use knowledge filters to restrict knowledge base searches to specific users, document types, or any other metadata attributes.

Key concepts demonstrated:
1. Loading documents with user-specific metadata
2. Filtering knowledge base searches by user ID
3. Combining multiple filter criteria
4. Comparing results across different filter combinations

You can pass filters in the following ways:
1. If you pass on Agent only, we use that for all runs
2. If you pass on run/print_response only, we use that for that run
3. If you pass on both, we override with the filters passed on run/print_response for that run
"""

from agno.agent import Agent
from agno.knowledge.docx import DocxKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.DOCX
)

# Initialize LanceDB
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb",
)

# Now use the downloaded paths in knowledge base initialization
knowledge_base = DocxKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base and filters
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)

# Query for Jordan Mitchell's experience and skills
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# # Option 2: Filters on the run/print_response
# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )

# # Query for Taylor Brooks as a candidate
# agent.print_response(
# "Tell me about Taylor Brooks as a candidate",
# knowledge_filters={"user_id": "taylor_brooks"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/docx/filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/docx/filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on load with Docx
Source: https://docs.agno.com/examples/concepts/knowledge/filters/docx/filtering_on_load

Learn how to filter knowledge base at load time using Docx documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.docx import DocxKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.DOCX
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When loading the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

# Initialize the DocxKnowledgeBase
knowledge_base = DocxKnowledgeBase(
 vector_db=vector_db,
 num_documents=5,
)

knowledge_base.load_document(
 path=downloaded_cv_paths[0],
 metadata={"user_id": "jordan_mitchell", "document_type": "cv", "year": 2025},
 recreate=True, # Set to True only for the first run, then set to False
)

# Load second document with user_2 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[1],
 metadata={"user_id": "taylor_brooks", "document_type": "cv", "year": 2025},
)

# Load second document with user_3 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[2],
 metadata={"user_id": "morgan_lee", "document_type": "cv", "year": 2025},
)

# Load second document with user_4 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[3],
 metadata={"user_id": "casey_jordan", "document_type": "cv", "year": 2025},
)

# Load second document with user_5 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[4],
 metadata={"user_id": "alex_rivera", "document_type": "cv", "year": 2025},
)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------
# Uncomment the example you want to run

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )
# agent.print_response(
# "Tell me about Jordan Mitchell's experience and skills",
# knowledge_filters = {"user_id": "jordan_mitchell"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/docx/filtering_on_load.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/docx/filtering_on_load.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Knowledge filtering using Traditional RAG
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering-traditional-RAG

Learn how to filter knowledge in Traditional RAG using metadata like user IDs, document types, and years. This example demonstrates how to set up a knowledge base with filters and query it effectively.

## Code

```python filtering-traditional-RAG.py
from agno.agent import Agent
from agno.knowledge.text import TextKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.TXT
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
knowledge_base = TextKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations

# Option 1: Filters on the Agent
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=False,
 add_references=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)

# Query for Jordan Mitchell's experience and skills
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# Option 2: Filters on the run/print_response
# agent = Agent(
# knowledge=knowledge_base,
# add_references=True,
# search_knowledge=False,
# )

# Query for Taylor Brooks as a candidate
# agent.print_response(
# "Tell me about Taylor Brooks as a candidate",
# knowledge_filters={"user_id": "taylor_brooks"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno lancedb openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python filtering-traditional-RAG.py
 ```

 ```bash Windows
 python filtering-traditional-RAG.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on ChromaDB
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_chroma_db

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in ChromaDB.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.chroma import ChromaDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize ChromaDB
vector_db = ChromaDb(collection="recipes", path="tmp/chromadb", persistent_client=True)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno chromadb openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_chroma_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_chroma_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on LanceDB
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_lance_db

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in LanceDB.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno lancedb openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_lance_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_lance_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on MilvusDB
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_milvus_db

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in MilvusDB.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.milvus import Milvus

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize Milvus vector db
vector_db = Milvus(
 collection="recipes",
 uri="tmp/milvus.db",
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno pymilvus openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_milvus.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_milvus.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on MongoDB
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_mongo_db

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in MongoDB.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.mongodb import MongoDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

mdb_connection_string = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=MongoDb(
 collection_name="filters",
 db_url=mdb_connection_string,
 search_index_name="filters",
 ),
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno pymongo openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_mongo_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_mongo_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on PgVector
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_pgvector

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in PgVector.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.pgvector import PgVector

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize PgVector
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

vector_db = PgVector(table_name="recipes", db_url=db_url)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno sqlalchemy psycopg openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_pgvector.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_pgvector.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on Pinecone
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_pinecone

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in Pinecone.

## Code

```python
from os import getenv

from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.pineconedb import PineconeDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize Pinecone
api_key = getenv("PINECONE_API_KEY")
index_name = "thai-recipe-index"

vector_db = PineconeDb(
 name=index_name,
 dimension=1536,
 metric="cosine",
 spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
 api_key=api_key,
)

# Step 1: Initialize knowledge base with documents and metadata
knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True, upsert=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "hey"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno pinecone pinecone-text openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_pinecone.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_pinecone.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on Qdrant
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_qdrant_db

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in Qdrant.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.qdrant import Qdrant

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

COLLECTION_NAME = "filtering-cv"

vector_db = Qdrant(collection=COLLECTION_NAME, url="http://localhost:6333")
# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno qdrant-client openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_qdrant_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_qdrant_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on Weaviate
Source: https://docs.agno.com/examples/concepts/knowledge/filters/filtering_weaviate

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata in Weaviate.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

vector_db = Weaviate(
 collection="recipes",
 vector_index=VectorIndex.HNSW,
 distance=Distance.COSINE,
 local=False, # Set to False if using Weaviate Cloud and True if using local instance
)

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno weaviate-client openai
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/filtering_weaviate.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/filtering_weaviate.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic filtering with Json
Source: https://docs.agno.com/examples/concepts/knowledge/filters/json/agentic_filtering

Learn how to do agentic knowledge filtering using Json documents with user-specific metadata.

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.json import JSONKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.JSON
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = JSONKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with Agent using filters from query automatically
# -----------------------------------------------------------------------------------

# Enable agentic filtering
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 enable_agentic_knowledge_filters=True,
)

# Query for Jordan Mitchell's experience and skills with filters in query so that Agent can automatically pick them up
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills with jordan_mitchell as user id and document type cv",
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/json/agentic_filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/json/agentic_filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering with Json
Source: https://docs.agno.com/examples/concepts/knowledge/filters/json/filtering

Learn how to filter knowledge base searches using Json documents with user-specific metadata.

## Code

```python
"""
User-Level Knowledge Filtering Example

This cookbook demonstrates how to use knowledge filters to restrict knowledge base searches to specific users, document types, or any other metadata attributes.

Key concepts demonstrated:
1. Loading documents with user-specific metadata
2. Filtering knowledge base searches by user ID
3. Combining multiple filter criteria
4. Comparing results across different filter combinations

You can pass filters in the following ways:
1. If you pass on Agent only, we use that for all runs
2. If you pass on run/print_response only, we use that for that run
3. If you pass on both, we override with the filters passed on run/print_response for that run
"""

from agno.agent import Agent
from agno.knowledge.json import JSONKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.JSON
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = JSONKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base and filters
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)

# Query for Jordan Mitchell' experience and skills
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# # Option 2: Filters on the run/print_response
# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )

# # Query for Taylor Brooks as a candidate
# agent.print_response(
# "Tell me about Taylor Brooks as a candidate",
# knowledge_filters={"user_id": "taylor_brooks"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/json/filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/json/filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on load with Json
Source: https://docs.agno.com/examples/concepts/knowledge/filters/json/filtering_on_load

Learn how to filter knowledge base at load time using Json documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.json import JSONKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.JSON
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When loading the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

# Initialize the JSONKnowledgeBase
knowledge_base = JSONKnowledgeBase(
 vector_db=vector_db,
 num_documents=5,
)

knowledge_base.load_document(
 path=downloaded_cv_paths[0],
 metadata={"user_id": "jordan_mitchell", "document_type": "cv", "year": 2025},
 recreate=True, # Set to True only for the first run, then set to False
)

# Load second document with user_2 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[1],
 metadata={"user_id": "taylor_brooks", "document_type": "cv", "year": 2025},
)

# Load second document with user_3 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[2],
 metadata={"user_id": "morgan_lee", "document_type": "cv", "year": 2025},
)

# Load second document with user_4 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[3],
 metadata={"user_id": "casey_jordan", "document_type": "cv", "year": 2025},
)

# Load second document with user_5 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[4],
 metadata={"user_id": "alex_rivera", "document_type": "cv", "year": 2025},
)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------
# Uncomment the example you want to run

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )
# agent.print_response(
# "Tell me about Jordan Mitchell's experience and skills",
# knowledge_filters = {"user_id": "jordan_mitchell"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/json/filtering_on_load.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/json/filtering_on_load.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic filtering with Pdf
Source: https://docs.agno.com/examples/concepts/knowledge/filters/pdf/agentic_filtering

Learn how to do agentic knowledge filtering using Pdf documents with user-specific metadata.

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with Agent using filters from query automatically
# -----------------------------------------------------------------------------------

# Enable agentic filtering
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 enable_agentic_knowledge_filters=True,
)

# Query for Jordan Mitchell's experience and skills with filters in query so that Agent can automatically pick them up
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills with jordan_mitchell as user id and document type cv",
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/pdf/agentic_filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/pdf/agentic_filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering with Pdf
Source: https://docs.agno.com/examples/concepts/knowledge/filters/pdf/filtering

Learn how to filter knowledge base searches using Pdf documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
knowledge_base = PDFKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations

# Option 1: Filters on the Agent
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
)

agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 knowledge_filters={"user_id": "jordan_mitchell"},
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/pdf/filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/pdf/filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on load with Pdf
Source: https://docs.agno.com/examples/concepts/knowledge/filters/pdf/filtering_on_load

Learn how to filter knowledge base at load time using Pdf documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.PDF
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When loading the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

# Initialize the PDFKnowledgeBase
knowledge_base = PDFKnowledgeBase(
 vector_db=vector_db,
 num_documents=5,
)

knowledge_base.load_document(
 path=downloaded_cv_paths[0],
 metadata={"user_id": "jordan_mitchell", "document_type": "cv", "year": 2025},
 recreate=True, # Set to True only for the first run, then set to False
)

# Load second document with user_2 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[1],
 metadata={"user_id": "taylor_brooks", "document_type": "cv", "year": 2025},
)

# Load second document with user_3 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[2],
 metadata={"user_id": "morgan_lee", "document_type": "cv", "year": 2025},
)

# Load second document with user_4 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[3],
 metadata={"user_id": "casey_jordan", "document_type": "cv", "year": 2025},
)

# Load second document with user_5 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[4],
 metadata={"user_id": "alex_rivera", "document_type": "cv", "year": 2025},
)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------
# Uncomment the example you want to run

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/pdf/filtering_on_load.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/pdf/filtering_on_load.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic filtering with Pdf-Url
Source: https://docs.agno.com/examples/concepts/knowledge/filters/pdf_url/agentic_filtering

Learn how to do agentic knowledge filtering using Pdf-Url documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = PDFUrlKnowledgeBase(
 urls=[
 {
 "url": "https://agno-public.s3.amazonaws.com/recipes/thai_recipes_short.pdf",
 "metadata": {
 "cuisine": "Thai",
 "source": "Thai Cookbook",
 "region": "Southeast Asia",
 },
 },
 {
 "url": "https://agno-public.s3.amazonaws.com/recipes/cape_recipes_short_2.pdf",
 "metadata": {
 "cuisine": "Cape",
 "source": "Cape Cookbook",
 "region": "South Africa",
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with Agent using filters from query automatically
# -----------------------------------------------------------------------------------

# Enable agentic filtering
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 enable_agentic_knowledge_filters=True,
)

# Query for Jordan Mitchell's experience and skills with filters in query so that Agent can automatically pick them up
agent.print_response(
 "How to make Pad Thai, refer from document with cuisine Thai and source Thai Cookbook",
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/pdf_url/agentic_filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/pdf_url/agentic_filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering with Pdf-Url
Source: https://docs.agno.com/examples/concepts/knowledge/filters/pdf_url/filtering

Learn how to filter knowledge base searches using Pdf-Url documents with user-specific metadata.

## Code

```python
"""
User-Level Knowledge Filtering Example with PDF URLs

This cookbook demonstrates how to use knowledge filters with PDF documents accessed via URLs,
showing how to restrict knowledge base searches to specific cuisines, sources, or any other metadata attributes.

Key concepts demonstrated:
1. Loading PDF documents from URLs with specific metadata
2. Filtering knowledge base searches by cuisine type
3. Combining multiple filter criteria
4. Comparing results across different filter combinations

You can pass filters in the following ways:
1. If you pass on Agent only, we use that for all runs
2. If you pass on run/print_response only, we use that for that run
3. If you pass on both, we override with the filters passed on run/print_response for that run
"""

from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with URLs and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include cuisine type, source, region, or any other attributes

knowledge_base = PDFUrlKnowledgeBase(
 urls=[
 {
 "url": "https://agno-public.s3.amazonaws.com/recipes/thai_recipes_short.pdf",
 "metadata": {
 "cuisine": "Thai",
 "source": "Thai Cookbook",
 "region": "Southeast Asia",
 },
 },
 {
 "url": "https://agno-public.s3.amazonaws.com/recipes/cape_recipes_short_2.pdf",
 "metadata": {
 "cuisine": "Cape",
 "source": "Cape Cookbook",
 "region": "South Africa",
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base and filters
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 # This will only return information from documents with Thai cuisine
 knowledge_filters={"cuisine": "Thai"},
)

# Query for Thai recipes
agent.print_response(
 "Tell me how to make Pad Thai",
 markdown=True,
)

# # Option 2: Filters on the run/print_response
# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )

# # Query for Cape Malay recipes
# agent.print_response(
# "Tell me how to make Cape Malay Curry",
# knowledge_filters={"cuisine": "Cape"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/pdf_url/filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/pdf_url/filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on load with Pdf-Url
Source: https://docs.agno.com/examples/concepts/knowledge/filters/pdf_url/filtering_on_load

Learn how to filter knowledge base at load time using Pdf-Url documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When loading the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

# Initialize knowledge base
knowledge_base = PDFUrlKnowledgeBase(
 vector_db=vector_db,
)

knowledge_base.load_document(
 url="https://agno-public.s3.amazonaws.com/recipes/thai_recipes_short.pdf",
 metadata={"cuisine": "Thai", "source": "Thai Cookbook"},
 recreate=False, # only use at the first run, True/False
)

knowledge_base.load_document(
 url="https://agno-public.s3.amazonaws.com/recipes/cape_recipes_short_2.pdf",
 metadata={"cuisine": "Cape", "source": "Cape Cookbook"},
)

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={
 "cuisine": "Thai"
 }, # This will only return information from documents associated with Thai cuisine
)
agent.print_response(
 "Tell me how to make Pad Thai",
 markdown=True,
)

# # # Option 2: Filters on the run/print_response
# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )
# agent.print_response(
# "Tell me how to make Cape Malay Curry",
# knowledge_filters={"cuisine": "Cape"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/pdf_url/filtering_on_load.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/pdf_url/filtering_on_load.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic filtering with Text
Source: https://docs.agno.com/examples/concepts/knowledge/filters/text/agentic_filtering

Learn how to do agentic knowledge filtering using Text documents with user-specific metadata.

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.knowledge.text import TextKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.TXT
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = TextKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with Agent using filters from query automatically
# -----------------------------------------------------------------------------------

# Enable agentic filtering
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 enable_agentic_knowledge_filters=True,
)

# Query for Jordan Mitchell's experience and skills with filters in query so that Agent can automatically pick them up
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills with jordan_mitchell as user id and document type cv",
 markdown=True,
)
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/text/agentic_filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/text/agentic_filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering with Text
Source: https://docs.agno.com/examples/concepts/knowledge/filters/text/filtering

Learn how to filter knowledge base searches using Text documents with user-specific metadata.

## Code

```python
"""
User-Level Knowledge Filtering Example

This cookbook demonstrates how to use knowledge filters to restrict knowledge base searches to specific users, document types, or any other metadata attributes.

Key concepts demonstrated:
1. Loading documents with user-specific metadata
2. Filtering knowledge base searches by user ID
3. Combining multiple filter criteria
4. Comparing results across different filter combinations

You can pass filters in the following ways:
1. If you pass on Agent only, we use that for all runs
2. If you pass on run/print_response only, we use that for that run
3. If you pass on both, we override with the filters passed on run/print_response for that run
"""

from agno.agent import Agent
from agno.knowledge.text import TextKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.TXT
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When initializing the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

knowledge_base = TextKnowledgeBase(
 path=[
 {
 "path": downloaded_cv_paths[0],
 "metadata": {
 "user_id": "jordan_mitchell",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[1],
 "metadata": {
 "user_id": "taylor_brooks",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[2],
 "metadata": {
 "user_id": "morgan_lee",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[3],
 "metadata": {
 "user_id": "casey_jordan",
 "document_type": "cv",
 "year": 2025,
 },
 },
 {
 "path": downloaded_cv_paths[4],
 "metadata": {
 "user_id": "alex_rivera",
 "document_type": "cv",
 "year": 2025,
 },
 },
 ],
 vector_db=vector_db,
)

# Load all documents into the vector database
knowledge_base.load(recreate=True)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base and filters
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)

# Query for Jordan Mitchell's experience and skills
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# # Option 2: Filters on the run/print_response
# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )

# # Query for Taylor Brooks as a candidate
# agent.print_response(
# "Tell me about Taylor Brooks as a candidate",
# knowledge_filters={"user_id": "taylor_brooks"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/text/filtering.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/text/filtering.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Filtering on load with Text
Source: https://docs.agno.com/examples/concepts/knowledge/filters/text/filtering_on_load

Learn how to filter knowledge base at load time using Text documents with user-specific metadata.

## Code

```python
from agno.agent import Agent
from agno.knowledge.text import TextKnowledgeBase
from agno.utils.media import (
 SampleDataFileExtension,
 download_knowledge_filters_sample_data,
)
from agno.vectordb.lancedb import LanceDb

# Download all sample CVs and get their paths
downloaded_cv_paths = download_knowledge_filters_sample_data(
 num_files=5, file_extension=SampleDataFileExtension.TXT
)

# Initialize LanceDB
# By default, it stores data in /tmp/lancedb
vector_db = LanceDb(
 table_name="recipes",
 uri="tmp/lancedb", # You can change this path to store data elsewhere
)

# Step 1: Initialize knowledge base with documents and metadata
# ------------------------------------------------------------------------------
# When loading the knowledge base, we can attach metadata that will be used for filtering
# This metadata can include user IDs, document types, dates, or any other attributes

# Initialize the TextKnowledgeBase
knowledge_base = TextKnowledgeBase(
 vector_db=vector_db,
 num_documents=5,
)

knowledge_base.load_document(
 path=downloaded_cv_paths[0],
 metadata={"user_id": "jordan_mitchell", "document_type": "cv", "year": 2025},
 recreate=True, # Set to True only for the first run, then set to False
)

# Load second document with user_2 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[1],
 metadata={"user_id": "taylor_brooks", "document_type": "cv", "year": 2025},
)

# Load second document with user_3 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[2],
 metadata={"user_id": "morgan_lee", "document_type": "cv", "year": 2025},
)

# Load second document with user_4 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[3],
 metadata={"user_id": "casey_jordan", "document_type": "cv", "year": 2025},
)

# Load second document with user_5 metadata
knowledge_base.load_document(
 path=downloaded_cv_paths[4],
 metadata={"user_id": "alex_rivera", "document_type": "cv", "year": 2025},
)

# Step 2: Query the knowledge base with different filter combinations
# ------------------------------------------------------------------------------
# Uncomment the example you want to run

# Option 1: Filters on the Agent
# Initialize the Agent with the knowledge base
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 knowledge_filters={"user_id": "jordan_mitchell"},
)
agent.print_response(
 "Tell me about Jordan Mitchell's experience and skills",
 markdown=True,
)

# agent = Agent(
# knowledge=knowledge_base,
# search_knowledge=True,
# )
# agent.print_response(
# "Tell me about Jordan Mitchell's experience and skills",
# knowledge_filters = {"user_id": "jordan_mitchell"},
# markdown=True,
# )
```

## Usage

<Steps>
 <Step title="Install libraries">
 ```bash
 pip install -U agno openai lancedb
 ```
 </Step>

 <Step title="Run the example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/filters/text/filtering_on_load.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/filters/text/filtering_on_load.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Built-in Memory
Source: https://docs.agno.com/examples/concepts/memory/00-built-in-memory

## Code

```python cookbook/agent_concepts/memory/00_builtin_memory.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from rich.pretty import pprint

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 # Set add_history_to_messages=true to add the previous chat history to the messages sent to the Model.
 add_history_to_messages=True,
 # Number of historical responses to add to the messages.
 num_history_responses=3,
 description="You are a helpful assistant that always responds in a polite, upbeat and positive manner.",
)

# -*- Create a run
agent.print_response("Share a 2 sentence horror story", stream=True)
# -*- Print the messages in the memory
pprint(
 [
 m.model_dump(include={"role", "content"})
 for m in agent.get_messages_for_session()
 ]
)

# -*- Ask a follow up question that continues the conversation
agent.print_response("What was my first message?", stream=True)
# -*- Print the messages in the memory
pprint(
 [
 m.model_dump(include={"role", "content"})
 for m in agent.get_messages_for_session()
 ]
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/00_builtin_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/00_builtin_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Standalone Memory Operations
Source: https://docs.agno.com/examples/concepts/memory/01-standalone-memory

This example shows how to manually add, retrieve, delete, and replace user memories.

## Code

```python cookbook/agent_concepts/memory/01_standalone_memory.py
from agno.memory.v2 import Memory, UserMemory
from rich.pretty import pprint

memory = Memory()

# Add a memory for the default user
memory.add_user_memory(
 memory=UserMemory(memory="The user's name is John Doe", topics=["name"]),
)
print("Memories:")
pprint(memory.memories)

# Add memories for Jane Doe
jane_doe_id = "jane_doe@example.com"
print(f"\nUser: {jane_doe_id}")
memory_id_1 = memory.add_user_memory(
 memory=UserMemory(memory="The user's name is Jane Doe", topics=["name"]),
 user_id=jane_doe_id,
)
memory_id_2 = memory.add_user_memory(
 memory=UserMemory(memory="She likes to play tennis", topics=["hobbies"]),
 user_id=jane_doe_id,
)
memories = memory.get_user_memories(user_id=jane_doe_id)
print("Memories:")
pprint(memories)

# Delete a memory
print("\nDeleting memory")
memory.delete_user_memory(user_id=jane_doe_id, memory_id=memory_id_2)
print("Memory deleted\n")
memories = memory.get_user_memories(user_id=jane_doe_id)
print("Memories:")
pprint(memories)

# Replace a memory
print("\nReplacing memory")
memory.replace_user_memory(
 memory_id=memory_id_1,
 memory=UserMemory(memory="The user's name is Jane Mary Doe", topics=["name"]),
 user_id=jane_doe_id,
)
print("Memory replaced")
memories = memory.get_user_memories(user_id=jane_doe_id)
print("Memories:")
pprint(memories)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno rich
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/01_standalone_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/01s̄_standalone_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Persistent Memory with SQLite
Source: https://docs.agno.com/examples/concepts/memory/02-persistent-memory

This example shows how to use the Memory class to create a persistent memory.

Every time you run this, the `Memory` object will be re-initialized from the DB.

## Code

```python cookbook/agent_concepts/memory/02_persistent_memory.py
from typing import List

from agno.memory.v2.db.schema import MemoryRow
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.memory.v2.schema import UserMemory

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
memory = Memory(db=memory_db)

john_doe_id = "john_doe@example.com"

# Run 1
memory.add_user_memory(
 memory=UserMemory(memory="The user's name is John Doe", topics=["name"]),
 user_id=john_doe_id,
)

# Run this the 2nd time
# memory.add_user_memory(
# memory=UserMemory(memory="The user works at a softward company called Agno", topics=["name"]),
# user_id=john_doe_id,
# )

memories: List[MemoryRow] = memory_db.read_memories()
print("All the DB memories:")
for i, m in enumerate(memories):
 print(f"{i}: {m.memory['memory']} ({m.last_updated})")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/02_persistent_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/02_persistent_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Custom Memory Creation
Source: https://docs.agno.com/examples/concepts/memory/03-custom-memory-creation

This example demonstrates how to create user memories with an Agent by providing either text or a list of messages. The Agent uses a custom memory manager to capture and store relevant details.

## Code

```python cookbook/agent_concepts/memory/04_custom_memory_creation.py
from agno.memory.v2 import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.manager import MemoryManager
from agno.models.anthropic.claude import Claude
from agno.models.google import Gemini
from agno.models.message import Message
from rich.pretty import pprint

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
# Reset for this example
memory_db.clear()

memory = Memory(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory_manager=MemoryManager(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory_capture_instructions="""\
 Memories should only include details about the user's academic interests.
 Only include which subjects they are interested in.
 Ignore names, hobbies, and personal interests.
 """,
 ),
 db=memory_db,
)

john_doe_id = "john_doe@example.com"

memory.create_user_memories(
 message="""\
My name is John Doe.

I enjoy hiking in the mountains on weekends,
reading science fiction novels before bed,
cooking new recipes from different cultures,
playing chess with friends.

I am interested to learn about the history of the universe and other astronomical topics.
""",
 user_id=john_doe_id,
)

memories = memory.get_user_memories(user_id=john_doe_id)
print("John Doe's memories:")
pprint(memories)

# Use default memory manager
memory = Memory(model=Claude(id="claude-3-5-sonnet-latest"), db=memory_db)
jane_doe_id = "jane_doe@example.com"

# Send a history of messages and add memories
memory.create_user_memories(
 messages=[
 Message(role="user", content="Hi, how are you?"),
 Message(role="assistant", content="I'm good, thank you!"),
 Message(role="user", content="What are you capable of?"),
 Message(
 role="assistant",
 content="I can help you with your homework and answer questions about the universe.",
 ),
 Message(role="user", content="My name is Jane Doe"),
 Message(role="user", content="I like to play chess"),
 Message(
 role="user",
 content="Actually, forget that I like to play chess. I more enjoy playing table top games like dungeons and dragons",
 ),
 Message(
 role="user",
 content="I'm also interested in learning about the history of the universe and other astronomical topics.",
 ),
 Message(role="assistant", content="That is great!"),
 Message(
 role="user",
 content="I am really interested in physics. Tell me about quantum mechanics?",
 ),
 ],
 user_id=jane_doe_id,
)

memories = memory.get_user_memories(user_id=jane_doe_id)
print("Jane Doe's memories:")
pprint(memories)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno rich
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/04_custom_memory_creation.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/04_custom_memory_creation.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Memory 
Source: https://docs.agno.com/examples/concepts/memory/04-memory-
This example demonstrates how to search for user memories using different retrieval methods

* last\_n: Retrieves the last n memories
* first\_n: Retrieves the first n memories
* semantic: Retrieves memories using semantic 
## Code

```python cookbook/agent_concepts/memory/05_memory_search.py
from agno.memory.v2 import Memory, UserMemory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.models.google.gemini import Gemini
from rich.pretty import pprint

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")
# Reset for this example
memory_db.clear()

memory = Memory(model=Gemini(id="gemini-2.0-flash-exp"), db=memory_db)

john_doe_id = "john_doe@example.com"
memory.add_user_memory(
 memory=UserMemory(memory="The user enjoys hiking in the mountains on weekends"),
 user_id=john_doe_id,
)
memory.add_user_memory(
 memory=UserMemory(
 memory="The user enjoys reading science fiction novels before bed"
 ),
 user_id=john_doe_id,
)
print("John Doe's memories:")
pprint(memory.memories)

memories = memory.search_user_memories(
 user_id=john_doe_id, limit=1, retrieval_method="last_n"
)
print("\nJohn Doe's last_n memories:")
pprint(memories)

memories = memory.search_user_memories(
 user_id=john_doe_id, limit=1, retrieval_method="first_n"
)
print("\nJohn Doe's first_n memories:")
pprint(memories)

memories = memory.search_user_memories(
 user_id=john_doe_id,
 query="What does the user like to do on weekends?",
 retrieval_method="agentic",
)
print("\nJohn Doe's memories similar to the query (agentic):")
pprint(memories)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/05_memory_search.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/05_memory_search.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent With Memory
Source: https://docs.agno.com/examples/concepts/memory/05-agent-with-memory

This example shows you how to use persistent memory with an Agent.

After each run, user memories are created/updated.

To enable this, set `enable_user_memories=True` in the Agent config.

## Code

```python cookbook/agent_concepts/memory/06_agent_with_memory.py
from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from rich.pretty import pprint
from utils import print_chat_history

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

# No need to set the model, it gets set by the agent to the agent's model
memory = Memory(db=memory_db)

# Reset the memory for this example
memory.clear()

session_id = "session_1"
john_doe_id = "john_doe@example.com"

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 memory=memory,
 storage=SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
 ),
 enable_user_memories=True,
)

agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=john_doe_id,
 session_id=session_id,
)

agent.print_response(
 "What are my hobbies?", stream=True, user_id=john_doe_id, session_id=session_id
)

# -*- Print the chat history
session_run = memory.runs[session_id][-1]
print_chat_history(session_run)

memories = memory.get_user_memories(user_id=john_doe_id)
print("John Doe's memories:")
pprint(memories)

agent.print_response(
 "Ok i dont like hiking anymore, i like to play soccer instead.",
 stream=True,
 user_id=john_doe_id,
 session_id=session_id,
)

# -*- Print the chat history
session_run = memory.runs[session_id][-1]
print_chat_history(session_run)

# You can also get the user memories from the agent
memories = agent.get_user_memories(user_id=john_doe_id)
print("John Doe's memories:")
pprint(memories)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/06_agent_with_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/06_agent_with_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic Memory
Source: https://docs.agno.com/examples/concepts/memory/06-agentic-memory

This example shows you how to use persistent memory with an Agent.

During each run the Agent can create/update/delete user memories.

To enable this, set `enable_agentic_memory=True` in the Agent config.

## Code

```python cookbook/agent_concepts/memory/07_agentic_memory.py
from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from rich.pretty import pprint

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

# No need to set the model, it gets set by the agent to the agent's model
memory = Memory(db=memory_db)

# Reset the memory for this example
memory.clear()

john_doe_id = "john_doe@example.com"

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 memory=memory,
 enable_agentic_memory=True,
)

agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=john_doe_id,
)

agent.print_response("What are my hobbies?", stream=True, user_id=john_doe_id)

memories = memory.get_user_memories(user_id=john_doe_id)
print("Memories about John Doe:")
pprint(memories)

agent.print_response(
 "Remove all existing memories of me.",
 stream=True,
 user_id=john_doe_id,
)

memories = memory.get_user_memories(user_id=john_doe_id)
print("Memories about John Doe:")
pprint(memories)

agent.print_response(
 "My name is John Doe and I like to paint.", stream=True, user_id=john_doe_id
)

memories = memory.get_user_memories(user_id=john_doe_id)
print("Memories about John Doe:")
pprint(memories)

agent.print_response(
 "I don't pain anymore, i draw instead.", stream=True, user_id=john_doe_id
)

memories = memory.get_user_memories(user_id=john_doe_id)

print("Memories about John Doe:")
pprint(memories)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/07_agentic_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/07_agentic_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Session Summaries
Source: https://docs.agno.com/examples/concepts/memory/07-agent-with-summaries

This example demonstrates how to create session summaries.

To enable this, set `enable_session_summaries=True` in the Agent config.

## Code

```python cookbook/agent_concepts/memory/08_agent_with_summaries.py

from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.memory.v2.summarizer import SessionSummarizer
from agno.models.anthropic.claude import Claude
from rich.pretty import pprint

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(
 db=memory_db,
 summarizer=SessionSummarizer(model=Claude(id="claude-3-5-sonnet-20241022")),
)

# Reset the memory for this example
memory.clear()

# No session and user ID is specified, so they are generated automatically
agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 memory=memory,
 enable_user_memories=True,
 enable_session_summaries=True,
)

agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
)

agent.print_response(
 "What are my hobbies?",
 stream=True,
)

memories = memory.get_user_memories()
print("John Doe's memories:")
pprint(memories)
session_summary = agent.get_session_summary()
pprint(session_summary)

# Now lets do a new session with a different user
session_id_2 = "1002"
mark_gonzales_id = "mark@example.com"

agent.print_response(
 "My name is Mark Gonzales and I like anime and video games.",
 stream=True,
 user_id=mark_gonzales_id,
 session_id=session_id_2,
)

agent.print_response(
 "What are my hobbies?",
 stream=True,
 user_id=mark_gonzales_id,
 session_id=session_id_2,
)

memories = memory.get_user_memories(user_id=mark_gonzales_id)
print("Mark Gonzales's memories:")
pprint(memories)

# We can get the session summary from memory as well
session_summary = memory.get_session_summary(
 session_id=session_id_2, user_id=mark_gonzales_id
)
pprint(session_summary)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/08_agent_with_summaries.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/08_agent_with_summaries.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Multiple Agents Sharing Memory
Source: https://docs.agno.com/examples/concepts/memory/08-agents-share-memory

In this example, we have two agents that share the same memory.

## Code

```python cookbook/agent_concepts/memory/09_agents_share_memory.py

from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google.gemini import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from rich.pretty import pprint

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

# No need to set the model, it gets set by the agent to the agent's model
memory = Memory(db=memory_db)

# Reset the memory for this example
memory.clear()

john_doe_id = "john_doe@example.com"

chat_agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 description="You are a helpful assistant that can chat with users",
 memory=memory,
 enable_user_memories=True,
)

chat_agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=john_doe_id,
)

chat_agent.print_response("What are my hobbies?", stream=True, user_id=john_doe_id)

research_agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 description="You are a research assistant that can help users with their research questions",
 tools=[DuckDuckGoTools(cache_results=True)],
 memory=memory,
 enable_user_memories=True,
)

research_agent.print_response(
 "I love asking questions about quantum computing. What is the latest news on quantum computing?",
 stream=True,
 user_id=john_doe_id,
)

memories = memory.get_user_memories(user_id=john_doe_id)
print("Memories about John Doe:")
pprint(memories)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai duckduckgo-
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/09_agents_share_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/09_agents_share_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Custom Memory
Source: https://docs.agno.com/examples/concepts/memory/09-custom-memory

This example shows how you can configure the Memory Manager and Summarizer models individually.

In this example, we use OpenRouter and LLama 3.3-70b-instruct for the memory manager and Claude 3.5 Sonnet for the summarizer, while using Gemini for the Agent.

We also set custom system prompts for the memory manager and summarizer.

## Code

```python cookbook/agent_concepts/memory/10_custom_memory.py
from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory, MemoryManager, SessionSummarizer
from agno.models.anthropic.claude import Claude
from agno.models.google.gemini import Gemini
from agno.models.openrouter.openrouter import OpenRouter
from rich.pretty import pprint

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

# You can also override the entire `system_message` for the memory manager
memory_manager = MemoryManager(
 model=OpenRouter(id="meta-llama/llama-3.3-70b-instruct"),
 additional_instructions="""
 IMPORTANT: Don't store any memories about the user's name. Just say "The User" instead of referencing the user's name.
 """,
)

# You can also override the entire `system_message` for the session summarizer
session_summarizer = SessionSummarizer(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 additional_instructions="""
 Make the summary very informal and conversational.
 """,
)

memory = Memory(
 db=memory_db,
 memory_manager=memory_manager,
 summarizer=session_summarizer,
)

# Reset the memory for this example
memory.clear()

john_doe_id = "john_doe@example.com"

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory=memory,
 enable_user_memories=True,
 enable_session_summaries=True,
 user_id=john_doe_id,
)

agent.print_response(
 "My name is John Doe and I like to swim and play soccer.", stream=True
)

agent.print_response("I dont like to swim", stream=True)

memories = memory.get_user_memories(user_id=john_doe_id)

print("John Doe's memories:")
pprint(memories)

summary = agent.get_session_summary()
print("Session summary:")
pprint(summary)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno rich
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/10_custom_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/10_custom_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Multi-User Multi-Session Chat
Source: https://docs.agno.com/examples/concepts/memory/10-multi-user-multi-session-chat

This example demonstrates how to run a multi-user, multi-session chat.

In this example, we have 3 users and 4 sessions.

* User 1 has 2 sessions.
* User 2 has 1 session.
* User 3 has 1 session.

## Code

```python cookbook/agent_concepts/memory/11_multi_user_multi_session_chat.py

import asyncio

from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google.gemini import Gemini
from agno.storage.sqlite import SqliteStorage

agent_storage = SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
)
memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(db=memory_db)

# Reset the memory for this example
memory.clear()

user_1_id = "user_1@example.com"
user_2_id = "user_2@example.com"
user_3_id = "user_3@example.com"

user_1_session_1_id = "user_1_session_1"
user_1_session_2_id = "user_1_session_2"
user_2_session_1_id = "user_2_session_1"
user_3_session_1_id = "user_3_session_1"

chat_agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 storage=agent_storage,
 memory=memory,
 enable_user_memories=True,
)

async def run_chat_agent():
 await chat_agent.aprint_response(
 "My name is Mark Gonzales and I like anime and video games.",
 user_id=user_1_id,
 session_id=user_1_session_1_id,
 )
 await chat_agent.aprint_response(
 "I also enjoy reading manga and playing video games.",
 user_id=user_1_id,
 session_id=user_1_session_1_id,
 )

 # Chat with user 1 - Session 2
 await chat_agent.aprint_response(
 "I'm going to the movies tonight.",
 user_id=user_1_id,
 session_id=user_1_session_2_id,
 )

 # Chat with user 2
 await chat_agent.aprint_response(
 "Hi my name is John Doe.", user_id=user_2_id, session_id=user_2_session_1_id
 )
 await chat_agent.aprint_response(
 "I'm planning to hike this weekend.",
 user_id=user_2_id,
 session_id=user_2_session_1_id,
 )

 # Chat with user 3
 await chat_agent.aprint_response(
 "Hi my name is Jane Smith.", user_id=user_3_id, session_id=user_3_session_1_id
 )
 await chat_agent.aprint_response(
 "I'm going to the gym tomorrow.",
 user_id=user_3_id,
 session_id=user_3_session_1_id,
 )

 # Continue the conversation with user 1
 # The agent should take into account all memories of user 1.
 await chat_agent.aprint_response(
 "What do you suggest I do this weekend?",
 user_id=user_1_id,
 session_id=user_1_session_1_id,
 )

if __name__ == "__main__":
 # Chat with user 1 - Session 1
 asyncio.run(run_chat_agent())

 user_1_memories = memory.get_user_memories(user_id=user_1_id)
 print("User 1's memories:")
 for i, m in enumerate(user_1_memories):
 print(f"{i}: {m.memory}")

 user_2_memories = memory.get_user_memories(user_id=user_2_id)
 print("User 2's memories:")
 for i, m in enumerate(user_2_memories):
 print(f"{i}: {m.memory}")

 user_3_memories = memory.get_user_memories(user_id=user_3_id)
 print("User 3's memories:")
 for i, m in enumerate(user_3_memories):
 print(f"{i}: {m.memory}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai anthropic
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/11_multi_user_multi_session_chat.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/11_multi_user_multi_session_chat.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Multi-User Multi-Session Chat Concurrent
Source: https://docs.agno.com/examples/concepts/memory/11-multi-user-multi-session-chat-concurrent

This example shows how to run a multi-user, multi-session chat concurrently. In this example, we have 3 users and 4 sessions:

* User 1 has 2 sessions.
* User 2 has 1 session.
* User 3 has 1 session.

## Code

```python cookbook/agent_concepts/memory/12_multi_user_multi_session_chat_concurrent.py
import asyncio

from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.anthropic.claude import Claude
from agno.models.google.gemini import Gemini
from agno.storage.sqlite import SqliteStorage

agent_storage = SqliteStorage(
 table_name="agent_sessions", db_file="tmp/persistent_memory.db"
)
memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(model=Claude(id="claude-3-5-sonnet-20241022"), db=memory_db)

# Reset the memory for this example
memory.clear()

user_1_id = "user_1@example.com"
user_2_id = "user_2@example.com"
user_3_id = "user_3@example.com"

user_1_session_1_id = "user_1_session_1"
user_1_session_2_id = "user_1_session_2"
user_2_session_1_id = "user_2_session_1"
user_3_session_1_id = "user_3_session_1"

chat_agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 storage=agent_storage,
 memory=memory,
 enable_user_memories=True,
)

async def user_1_conversation():
 """Handle conversation with user 1 across multiple sessions"""
 # User 1 - Session 1
 await chat_agent.arun(
 "My name is Mark Gonzales and I like anime and video games.",
 user_id=user_1_id,
 session_id=user_1_session_1_id,
 )
 await chat_agent.arun(
 "I also enjoy reading manga and playing video games.",
 user_id=user_1_id,
 session_id=user_1_session_1_id,
 )

 # User 1 - Session 2
 await chat_agent.arun(
 "I'm going to the movies tonight.",
 user_id=user_1_id,
 session_id=user_1_session_2_id,
 )

 # Continue the conversation in session 1
 await chat_agent.arun(
 "What do you suggest I do this weekend?",
 user_id=user_1_id,
 session_id=user_1_session_1_id,
 )

 print("User 1 Done")

async def user_2_conversation():
 """Handle conversation with user 2"""
 await chat_agent.arun(
 "Hi my name is John Doe.", user_id=user_2_id, session_id=user_2_session_1_id
 )
 await chat_agent.arun(
 "I'm planning to hike this weekend.",
 user_id=user_2_id,
 session_id=user_2_session_1_id,
 )
 print("User 2 Done")

async def user_3_conversation():
 """Handle conversation with user 3"""
 await chat_agent.arun(
 "Hi my name is Jane Smith.", user_id=user_3_id, session_id=user_3_session_1_id
 )
 await chat_agent.arun(
 "I'm going to the gym tomorrow.",
 user_id=user_3_id,
 session_id=user_3_session_1_id,
 )
 print("User 3 Done")

async def run_concurrent_chat_agent():
 """Run all user conversations concurrently"""
 await asyncio.gather(
 user_1_conversation(), user_2_conversation(), user_3_conversation()
 )

if __name__ == "__main__":
 # Run all conversations concurrently
 asyncio.run(run_concurrent_chat_agent())

 user_1_memories = memory.get_user_memories(user_id=user_1_id)
 print("User 1's memories:")
 for i, m in enumerate(user_1_memories):
 print(f"{i}: {m.memory}")

 user_2_memories = memory.get_user_memories(user_id=user_2_id)
 print("User 2's memories:")
 for i, m in enumerate(user_2_memories):
 print(f"{i}: {m.memory}")

 user_3_memories = memory.get_user_memories(user_id=user_3_id)
 print("User 3's memories:")
 for i, m in enumerate(user_3_memories):
 print(f"{i}: {m.memory}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno google-generativeai anthropic
 ```
 </Step>

 <Step title="Set your API keys">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/12_multi_user_multi_session_chat_concurrent.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/12_multi_user_multi_session_chat_concurrent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Memory References
Source: https://docs.agno.com/examples/concepts/memory/12-memory-references

This example shows how to use the `add_memory_references` parameter in the Agent config to
add references to the user memories to the Agent.

## Code

```12_memory_references.py
from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory, UserMemory
from agno.models.google.gemini import Gemini

memory_db = SqliteMemoryDb(table_name="memory", db_file="tmp/memory.db")

memory = Memory(db=memory_db)

memory.add_user_memory(
 memory=UserMemory(memory="I like to play soccer", topics=["soccer"]),
 user_id="john_doe@example.com",
)

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory=memory,
 add_memory_references=True, # Add pre existing memories to the Agent but don't create new ones
)

# Alternatively, you can create/update user memories but not add them to the Agent
# agent = Agent(
# model=Gemini(id="gemini-2.0-flash-exp"),
# memory=memory,
# enable_user_memories=True,
# add_memory_references=False,
# )

agent.print_response("What are my hobbies?", user_id="john_doe@example.com")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python 12_memory_references.py
 ```

 ```bash Windows
 python 12_memory_references.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Session Summary References
Source: https://docs.agno.com/examples/concepts/memory/13-session-summary-references

This example shows how to use the `add_session_summary_references` parameter in the Agent config to
add references to the session summaries to the Agent.

## Code

```13_session_summary_references.py
from agno.agent.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.google.gemini import Gemini
from agno.storage.postgres import PostgresStorage

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

memory_db = PostgresMemoryDb(table_name="memory", db_url=db_url)

# Reset for this example
memory_db.clear()

memory = Memory(db=memory_db)

user_id = "john_doe@example.com"
session_id = "session_summaries"

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory=memory,
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 enable_session_summaries=True,
 session_id=session_id,
)

# This will create a new session summary
agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 user_id=user_id,
)

# You can use existing session summaries from session storage without creating or updating any new ones.
agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 memory=memory,
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 add_session_summary_references=True,
 session_id=session_id,
)

agent.print_response("What are my hobbies?", user_id=user_id)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python 13_session_summary_references.py
 ```

 ```bash Windows
 python 13_session_summary_references.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# MongoDB Memory Storage
Source: https://docs.agno.com/examples/concepts/memory/db/mem-mongodb-memory

## Code

```python cookbook/agent_concepts/memory/mongodb_memory.py
"""
This example shows how to use the Memory class with MongoDB storage.
"""

import asyncio
import os

from agno.agent.agent import Agent
from agno.memory.v2.db.mongodb import MongoMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai.chat import OpenAIChat

# Get MongoDB connection string from environment
# Format: mongodb://username:password@localhost:27017/
mongo_url = "mongodb://localhost:27017/"
database_name = "agno_memory"

# Create MongoDB memory database
memory_db = MongoMemoryDb(
 connection_string=mongo_url,
 database_name=database_name,
 collection_name="memories" # Collection name to use in the database
)

# Create memory instance with MongoDB backend
memory = Memory(db=memory_db)

# This will create the collection if it doesn't exist
memory.clear()

# Create agent with memory
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 memory=memory,
 enable_user_memories=True,
)

async def run_example():
 # Use the agent with MongoDB-backed memory
 await agent.aprint_response(
 "My name is Jane Smith and I enjoy painting and photography.",
 user_id="jane@example.com",
 )
 
 await agent.aprint_response(
 "What are my creative interests?",
 user_id="jane@example.com",
 )
 
 # Display the memories stored in MongoDB
 memories = memory.get_user_memories(user_id="jane@example.com")
 print("Memories stored in MongoDB:")
 for i, m in enumerate(memories):
 print(f"{i}: {m.memory}")

if __name__ == "__main__":
 asyncio.run(run_example())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai pymongo
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac/Linux
 python cookbook/agent_concepts/memory/mongodb_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/mongodb_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PostgreSQL Memory Storage
Source: https://docs.agno.com/examples/concepts/memory/db/mem-postgres-memory

## Code

```python cookbook/agent_concepts/memory/postgres_memory.py
"""
This example shows how to use the Memory class with PostgreSQL storage.
"""

from agno.agent.agent import Agent
from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai.chat import OpenAIChat
from agno.storage.postgres import PostgresStorage

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

memory = Memory(db=PostgresMemoryDb(table_name="agent_memories", db_url=db_url))

session_id = "postgres_memories"
user_id = "postgres_user"

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 memory=memory,
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 enable_user_memories=True,
 enable_session_summaries=True,
)

agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=user_id,
 session_id=session_id,
)

agent.print_response(
 "What are my hobbies?", stream=True, user_id=user_id, session_id=session_id
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai sqlalchemy 'psycopg[binary]'
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac/Linux
 python cookbook/agent_concepts/memory/postgres_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/postgres_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Redis Memory Storage
Source: https://docs.agno.com/examples/concepts/memory/db/mem-redis-memory

## Code

```python cookbook/agent_concepts/memory/redis_memory.py
"""
This example shows how to use the Memory class with Redis storage.
"""

from agno.agent.agent import Agent
from agno.memory.v2.db.redis import RedisMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.redis import RedisStorage

# Create Redis memory database
memory_db = RedisMemoryDb(
 prefix="agno_memory", # Prefix for Redis keys to namespace the memories
 host="localhost", # Redis host address
 port=6379, # Redis port number
)

# Create memory instance with Redis backend
memory = Memory(db=memory_db)

# This will clear any existing memories
memory.clear()

# Session and user identifiers
session_id = "redis_memories"
user_id = "redis_user"

# Create agent with memory and Redis storage
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 memory=memory,
 storage=RedisStorage(prefix="agno_test", host="localhost", port=6379),
 enable_user_memories=True,
 enable_session_summaries=True,
)

# First interaction - introducing personal information
agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=user_id,
 session_id=session_id,
)

# Second interaction - testing if memory was stored
agent.print_response(
 "What are my hobbies?", 
 stream=True, 
 user_id=user_id, 
 session_id=session_id
)

# Display the memories stored in Redis
memories = memory.get_user_memories(user_id=user_id)
print("Memories stored in Redis:")
for i, m in enumerate(memories):
 print(f"{i}: {m.memory}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai redis
 ```
 </Step>

 <Step title="Run Redis">
 ```bash
 docker run --name my-redis -p 6379:6379 -d redis
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac/Linux
 python cookbook/agent_concepts/memory/redis_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/redis_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# SQLite Memory Storage
Source: https://docs.agno.com/examples/concepts/memory/db/mem-sqlite-memory

## Code

```python cookbook/agent_concepts/memory/sqlite_memory.py
"""
This example shows how to use the Memory class with SQLite storage.
"""

from agno.agent.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

# Create SQLite memory database
memory_db = SqliteMemoryDb(
 table_name="agent_memories", # Table name to use in the database
 db_file="tmp/memory.db", # Path to SQLite database file
)

# Create memory instance with SQLite backend
memory = Memory(db=memory_db)

# This will create the table if it doesn't exist
memory.clear()

# Session and user identifiers
session_id = "sqlite_memories"
user_id = "sqlite_user"

# Create agent with memory and SQLite storage
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 memory=memory,
 storage=SqliteStorage(
 table_name="agent_sessions", 
 db_file="tmp/memory.db"
 ),
 enable_user_memories=True,
 enable_session_summaries=True,
)

# First interaction - introducing personal information
agent.print_response(
 "My name is John Doe and I like to hike in the mountains on weekends.",
 stream=True,
 user_id=user_id,
 session_id=session_id,
)

# Second interaction - testing if memory was stored
agent.print_response(
 "What are my hobbies?", 
 stream=True, 
 user_id=user_id, 
 session_id=session_id
)

# Display the memories stored in SQLite
memories = memory.get_user_memories(user_id=user_id)
print("Memories stored in SQLite:")
for i, m in enumerate(memories):
 print(f"{i}: {m.memory}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac/Linux
 python cookbook/agent_concepts/memory/sqlite_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/sqlite_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Mem0 Memory
Source: https://docs.agno.com/examples/concepts/memory/mem0-memory

## Code

```python cookbook/agent_concepts/memory/mem0_memory.py
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.utils.pprint import pprint_run_response
from mem0 import MemoryClient

client = MemoryClient()

user_id = "agno"
messages = [
 {"role": "user", "content": "My name is John Billings."},
 {"role": "user", "content": "I live in NYC."},
 {"role": "user", "content": "I'm going to a concert tomorrow."},
]
# Comment out the following line after running the script once
client.add(messages, user_id=user_id)

agent = Agent(
 model=OpenAIChat(),
 context={"memory": client.get_all(user_id=user_id)},
 add_context=True,
)
run: RunResponse = agent.run("What do you know about me?")

pprint_run_response(run)

messages = [{"role": i.role, "content": str(i.content)} for i in (run.messages or [])]
client.add(messages, user_id=user_id)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai mem0 agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/memory/mem0_memory.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/memory/mem0_memory.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Input Output
Source: https://docs.agno.com/examples/concepts/multimodal/audio-input-output

## Code

```python
import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content

agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "wav"},
 ),
 markdown=True,
)

agent.run(
 "What's in these recording?",
 audio=[Audio(content=wav_data, format="wav")],
)

if agent.run_response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.content, filename="tmp/result.wav"
 )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/audio_input_output.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/audio_input_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Multi-turn Audio Agent
Source: https://docs.agno.com/examples/concepts/multimodal/audio-multi-turn

## Code

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "wav"},
 ),
 debug_mode=True,
 add_history_to_messages=True,
)

agent.run("Is a golden retriever a good family dog?")
if agent.run_response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.content, filename="tmp/answer_1.wav"
 )

agent.run("Why do you say they are loyal?")
if agent.run_response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.content, filename="tmp/answer_2.wav"
 )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/audio_multi_turn.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/audio_multi_turn.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Sentiment Analysis Agent
Source: https://docs.agno.com/examples/concepts/multimodal/audio-sentiment-analysis

## Code

```python
import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

url = "https://agno-public.s3.amazonaws.com/demo_data/sample_conversation.wav"

response = requests.get(url)
audio_content = response.content

agent.print_response(
 "Give a sentiment analysis of this audio conversation. Use speaker A, speaker B to identify speakers.",
 audio=[Audio(content=audio_content)],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install google-genai
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/audio_sentiment_analysis.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/audio_sentiment_analysis.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Streaming Agent
Source: https://docs.agno.com/examples/concepts/multimodal/audio-streaming

## Code

```python
import base64
import wave
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import Iterator

# Audio Configuration
SAMPLE_RATE = 24000 # Hz (24kHz)
CHANNELS = 1 # Mono
SAMPLE_WIDTH = 2 # Bytes (16 bits)

agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={
 "voice": "alloy",
 "format": "pcm16", # Required for streaming
 },
 ),
 debug_mode=True,
 add_history_to_messages=True,
)

# Question with streaming
output_stream: Iterator[RunResponse] = agent.run(
 "Is a golden retriever a good family dog?", 
 stream=True
)

with wave.open("tmp/answer_1.wav", "wb") as wav_file:
 wav_file.setnchannels(CHANNELS)
 wav_file.setsampwidth(SAMPLE_WIDTH)
 wav_file.setframerate(SAMPLE_RATE)
 
 for response in output_stream:
 if response.response_audio:
 if response.response_audio.transcript:
 print(response.response_audio.transcript, end="", flush=True)
 if response.response_audio.content:
 try:
 pcm_bytes = base64.b64decode(response.response_audio.content)
 wav_file.writeframes(pcm_bytes)
 except Exception as e:
 print(f"Error decoding audio: {e}")
print()
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/audio_streaming.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/audio_streaming.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio to text Agent
Source: https://docs.agno.com/examples/concepts/multimodal/audio-to-text

## Code

```python
import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

url = "https://agno-public.s3.us-east-1.amazonaws.com/demo_data/QA-01.mp3"

response = requests.get(url)
audio_content = response.content

agent.print_response(
 "Give a transcript of this audio conversation. Use speaker A, speaker B to identify speakers.",
 audio=[Audio(content=audio_content)],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install google-genai
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/audio_to_text.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/audio_to_text.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Blog to Podcast Agent
Source: https://docs.agno.com/examples/concepts/multimodal/blog-to-podcast

## Code

```python
import os
from uuid import uuid4
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.eleven_labs import ElevenLabsTools
from agno.tools.firecrawl import FirecrawlTools
from agno.agent import Agent, RunResponse
from agno.utils.audio import write_audio_to_file
from agno.utils.log import logger

url = "https://www.bcg.com/capabilities/artificial-intelligence/ai-agents"

blog_to_podcast_agent = Agent(
 name="Blog to Podcast Agent",
 agent_id="blog_to_podcast_agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 ElevenLabsTools(
 voice_id="JBFqnCBsd6RMkjVDRZzb",
 model_id="eleven_multilingual_v2",
 target_directory="audio_generations",
 ),
 FirecrawlTools(),
 ],
 description="You are an AI agent that can generate audio using the ElevenLabs API.",
 instructions=[
 "When the user provides a blog URL:",
 "1. Use FirecrawlTools to scrape the blog content",
 "2. Create a concise summary of the blog content that is NO MORE than 2000 characters long", 
 "3. The summary should capture the main points while being engaging and conversational",
 "4. Use the ElevenLabsTools to convert the summary to audio",
 "You don't need to find the appropriate voice first, I already specified the voice to user",
 "Ensure the summary is within the 2000 character limit to avoid ElevenLabs API limits",
 ],
 markdown=True,
 debug_mode=True,
)

podcast: RunResponse = blog_to_podcast_agent.run(
 f"Convert the blog content to a podcast: {url}"
)

save_dir = "audio_generations"

if podcast.audio is not None and len(podcast.audio) > 0:
 try:
 os.makedirs(save_dir, exist_ok=True)
 filename = f"{save_dir}/sample_podcast{uuid4()}.wav"
 write_audio_to_file(
 audio=podcast.audio[0].base64_audio,
 filename=filename
 )
 print(f"Audio saved successfully to: {filename}")
 except Exception as e:
 print(f"Error saving audio file: {e}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 export ELEVEN_LABS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai elevenlabs firecrawl-py agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/blog_to_podcast.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/blog_to_podcast.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Generate Images with Intermediate Steps
Source: https://docs.agno.com/examples/concepts/multimodal/generate-image

## Code

```python
from typing import Iterator

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.dalle import DalleTools
from agno.utils.common import dataclass_to_dict
from rich.pretty import pprint

image_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DalleTools()],
 description="You are an AI agent that can create images using DALL-E.",
 instructions=[
 "When the user asks you to create an image, use the DALL-E tool to create an image.",
 "The DALL-E tool will return an image URL.",
 "Return the image URL in your response in the following format: `![image description](image URL)`",
 ],
 markdown=True,
)

run_stream: Iterator[RunResponse] = image_agent.run(
 "Create an image of a yellow siamese cat",
 stream=True,
 stream_intermediate_steps=True,
)
for chunk in run_stream:
 pprint(dataclass_to_dict(chunk, exclude={"messages"}))
 print("---" * 20)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai rich agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/generate_image_with_intermediate_steps.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/generate_image_with_intermediate_steps.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Generate Music using Models Lab
Source: https://docs.agno.com/examples/concepts/multimodal/generate-music-agent

## Code

```python
import os
from uuid import uuid4

import requests
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.models_labs import FileType, ModelsLabTools
from agno.utils.log import logger

agent = Agent(
 name="ModelsLab Music Agent",
 agent_id="ml_music_agent",
 model=OpenAIChat(id="gpt-4o"),
 show_tool_calls=True,
 tools=[ModelsLabTools(wait_for_completion=True, file_type=FileType.MP3)],
 description="You are an AI agent that can generate music using the ModelsLabs API.",
 instructions=[
 "When generating music, use the `generate_media` tool with detailed prompts that specify:",
 "- The genre and style of music (e.g., classical, jazz, electronic)",
 "- The instruments and sounds to include",
 "- The tempo, mood and emotional qualities",
 "- The structure (intro, verses, chorus, bridge, etc.)",
 "Create rich, descriptive prompts that capture the desired musical elements.",
 "Focus on generating high-quality, complete instrumental pieces.",
 ],
 markdown=True,
 debug_mode=True,
)

music: RunResponse = agent.run("Generate a 30 second classical music piece")

save_dir = "audio_generations"

if music.audio is not None and len(music.audio) > 0:
 url = music.audio[0].url
 response = requests.get(url)
 os.makedirs(save_dir, exist_ok=True)
 filename = f"{save_dir}/sample_music{uuid4()}.wav"
 with open(filename, "wb") as f:
 f.write(response.content)
 logger.info(f"Music saved to {filename}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 export MODELS_LAB_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/generate_music_agent.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/generate_music_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Generate Video using Models Lab
Source: https://docs.agno.com/examples/concepts/multimodal/generate-video-models-lab

## Code

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.models_labs import ModelsLabTools

video_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[ModelsLabTools()],
 description="You are an AI agent that can generate videos using the ModelsLabs API.",
 instructions=[
 "When the user asks you to create a video, use the `generate_media` tool to create the video.",
 "The video will be displayed in the UI automatically below your response, so you don't need to show the video URL in your response.",
 "Politely and courteously let the user know that the video has been generated and will be displayed below as soon as its ready.",
 ],
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
)

video_agent.print_response("Generate a video of a cat playing with a ball")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 export MODELS_LAB_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/generate_video_using_models_lab.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/generate_video_using_models_lab.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Generate Video using Replicate
Source: https://docs.agno.com/examples/concepts/multimodal/generate-video-replicate

## Code

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.replicate import ReplicateTools

video_agent = Agent(
 name="Video Generator Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 ReplicateTools(
 model="tencent/hunyuan-video:847dfa8b01e739637fc76f480ede0c1d76408e1d694b830b5dfb8e547bf98405"
 )
 ],
 description="You are an AI agent that can generate videos using the Replicate API.",
 instructions=[
 "When the user asks you to create a video, use the `generate_media` tool to create the video.",
 "Return the URL as raw to the user.",
 "Don't convert video URL to markdown or anything else.",
 ],
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
)

video_agent.print_response("Generate a video of a horse in the dessert.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 export REPLICATE_API_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai replicate agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/generate_video_using_replicate.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/generate_video_using_replicate.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image to Audio Agent
Source: https://docs.agno.com/examples/concepts/multimodal/image-to-audio

## Code

```python
from pathlib import Path

from agno.agent import Agent, RunResponse
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file
from rich import print
from rich.text import Text

image_agent = Agent(model=OpenAIChat(id="gpt-4o"))

image_path = Path(__file__).parent.joinpath("sample.jpg")
image_story: RunResponse = image_agent.run(
 "Write a 3 sentence fiction story about the image",
 images=[Image(filepath=image_path)],
)
formatted_text = Text.from_markup(
 f":sparkles: [bold magenta]Story:[/bold magenta] {image_story.content} :sparkles:"
)
print(formatted_text)

audio_agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "wav"},
 ),
)

audio_story: RunResponse = audio_agent.run(
 f"Narrate the story with flair: {image_story.content}"
)
if audio_story.response_audio is not None:
 write_audio_to_file(
 audio=audio_story.response_audio.content, filename="tmp/sample_story.wav"
 )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai rich agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/image_to_audio.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/image_to_audio.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image to Image Agent
Source: https://docs.agno.com/examples/concepts/multimodal/image-to-image

## Code

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.fal import FalTools

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 agent_id="image-to-image",
 name="Image to Image Agent",
 tools=[FalTools()],
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
 instructions=[
 "You have to use the `image_to_image` tool to generate the image.",
 "You are an AI agent that can generate images using the Fal AI API.",
 "You will be given a prompt and an image URL.",
 "You have to return the image URL as provided, don't convert it to markdown or anything else.",
 ],
)

agent.print_response(
 "a cat dressed as a wizard with a background of a mystic forest. Make it look like 'https://fal.media/files/koala/Chls9L2ZnvuipUTEwlnJC.png'",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 export FAL_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai fal agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/image_to_image_agent.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/image_to_image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image to Text Agent
Source: https://docs.agno.com/examples/concepts/multimodal/image-to-text

## Code

```python
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 agent_id="image-to-text",
 name="Image to Text Agent",
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
 instructions=[
 "You are an AI agent that can generate text descriptions based on an image.",
 "You have to return a text response describing the image.",
 ],
)
image_path = Path(__file__).parent.joinpath("sample.jpg")
agent.print_response(
 "Write a 3 sentence fiction story about the image",
 images=[Image(filepath=image_path)],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/image_to_text_agent.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/image_to_text_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Video Caption Agent
Source: https://docs.agno.com/examples/concepts/multimodal/video-caption

## Code

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.moviepy_video import MoviePyVideoTools
from agno.tools.openai import OpenAITools

video_tools = MoviePyVideoTools(
 process_video=True, generate_captions=True, embed_captions=True
)

openai_tools = OpenAITools()

video_caption_agent = Agent(
 name="Video Caption Generator Agent",
 model=OpenAIChat(
 id="gpt-4o",
 ),
 tools=[video_tools, openai_tools],
 description="You are an AI agent that can generate and embed captions for videos.",
 instructions=[
 "When a user provides a video, process it to generate captions.",
 "Use the video processing tools in this sequence:",
 "1. Extract audio from the video using extract_audio",
 "2. Transcribe the audio using transcribe_audio",
 "3. Generate SRT captions using create_srt",
 "4. Embed captions into the video using embed_captions",
 ],
 markdown=True,
)

video_caption_agent.print_response(
 "Generate captions for {video with location} and embed them in the video"
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai moviepy ffmpeg agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/video_caption_agent.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/video_caption_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Video to Shorts Agent
Source: https://docs.agno.com/examples/concepts/multimodal/video-to-shorts

## Code

```python
import subprocess
import time
from pathlib import Path

from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini
from agno.utils.log import logger
from google.generativeai import get_file, upload_file

video_path = Path(__file__).parent.joinpath("sample.mp4")
output_dir = Path("tmp/shorts")

agent = Agent(
 name="Video2Shorts",
 description="Process videos and generate engaging shorts.",
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
 debug_mode=True,
 instructions=[
 "Analyze the provided video directly—do NOT reference or analyze any external sources or YouTube videos.",
 "Identify engaging moments that meet the specified criteria for short-form content.",
 """Provide your analysis in a **table format** with these columns:
 - Start Time | End Time | Description | Importance Score""",
 "Ensure all timestamps use MM:SS format and importance scores range from 1-10. ",
 "Focus only on segments between 15 and 60 seconds long.",
 "Base your analysis solely on the provided video content.",
 "Deliver actionable insights to improve the identified segments for short-form optimization.",
 ],
)

# Upload and process video
video_file = upload_file(video_path)
while video_file.state.name == "PROCESSING":
 time.sleep(2)
 video_file = get_file(video_file.name)

# Multimodal Query for Video Analysis
query = """
You are an expert in video content creation, specializing in crafting engaging short-form content for platforms like YouTube Shorts and Instagram Reels. Your task is to analyze the provided video and identify segments that maximize viewer engagement.

For each video, you'll:

1. Identify key moments that will capture viewers' attention, focusing on:
 - High-energy sequences
 - Emotional peaks
 - Surprising or unexpected moments
 - Strong visual and audio elements
 - Clear narrative segments with compelling storytelling

2. Extract segments that work best for short-form content, considering:
 - Optimal length (strictly 15–60 seconds)
 - Natural start and end points that ensure smooth transitions
 - Engaging pacing that maintains viewer attention
 - Audio-visual harmony for an immersive experience
 - Vertical format compatibility and adjustments if necessary

3. Provide a detailed analysis of each segment, including:
 - Precise timestamps (Start Time | End Time in MM:SS format)
 - A clear description of why the segment would be engaging
 - Suggestions on how to enhance the segment for short-form content
 - An importance score (1-10) based on engagement potential

Your goal is to identify moments that are visually compelling, emotionally engaging, and perfectly optimized for short-form platforms.
"""

# Generate Video Analysis
response = agent.run(query, videos=[Video(content=video_file)])

# Create output directory
output_dir = Path(output_dir)
output_dir.mkdir(parents=True, exist_ok=True)

# Extract and cut video segments
def extract_segments(response_text):
 import re

 segments_pattern = r"\|\s*(\d+:\d+)\s*\|\s*(\d+:\d+)\s*\|\s*(.*?)\s*\|\s*(\d+)\s*\|"
 segments: list[dict] = []

 for match in re.finditer(segments_pattern, str(response_text)):
 start_time = match.group(1)
 end_time = match.group(2)
 description = match.group(3)
 score = int(match.group(4))

 start_seconds = sum(x * int(t) for x, t in zip([60, 1], start_time.split(":")))
 end_seconds = sum(x * int(t) for x, t in zip([60, 1], end_time.split(":")))
 duration = end_seconds - start_seconds

 if 15 <= duration <= 60 and score > 7:
 output_path = output_dir / f"short_{len(segments) + 1}.mp4"

 command = [
 "ffmpeg",
 "-ss",
 str(start_seconds),
 "-i",
 video_path,
 "-t",
 str(duration),
 "-vf",
 "scale=1080:1920,setsar=1:1",
 "-c:v",
 "libx264",
 "-c:a",
 "aac",
 "-y",
 str(output_path),
 ]

 try:
 subprocess.run(command, check=True)
 segments.append(
 {"path": output_path, "description": description, "score": score}
 )
 except subprocess.CalledProcessError:
 print(f"Failed to process segment: {start_time} - {end_time}")

 return segments

logger.debug(f"{response.content}")

# Process segments
shorts = extract_segments(response.content)

# Print results
print("\n--- Generated Shorts ---")
for short in shorts:
 print(f"Short at {short['path']}")
 print(f"Description: {short['description']}")
 print(f"Engagement Score: {short['score']}/10\n")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U opencv-python google-generativeai sqlalchemy ffmpeg-python agno
 ```
 </Step>

 <Step title="Install ffmpeg">
 <CodeGroup>
 ```bash Mac
 brew install ffmpeg
 ```

 ```bash Windows
 # Install ffmpeg using chocolatey or download from https://ffmpeg.org/download.html
 choco install ffmpeg
 ```
 </CodeGroup>
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/multimodal/video_to_shorts.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/multimodal/video_to_shorts.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Arize Phoenix via OpenInference
Source: https://docs.agno.com/examples/concepts/observability/arize-phoenix-via-openinference

## Overview

This example demonstrates how to instrument your Agno agent with OpenInference and send traces to Arize Phoenix.

## Code

```python
import asyncio
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from phoenix.otel import register

# Set environment variables for Arize Phoenix
os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('ARIZE_PHOENIX_API_KEY')}"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"

# Configure the Phoenix tracer
tracer_provider = register(
 project_name="agno-stock-price-agent", # Default is 'default'
 auto_instrument=True, # Automatically use the installed OpenInference instrumentation
)

# Create and configure the agent
agent = Agent(
 name="Stock Price Agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[YFinanceTools()],
 instructions="You are a stock price agent. Answer questions in the style of a stock analyst.",
 debug_mode=True,
)

# Use the agent
agent.print_response("What is the current price of Tesla?")
```

## Usage

<Steps>
 <Step title="Install Dependencies">
 ```bash
 pip install agno arize-phoenix openai openinference-instrumentation-agno opentelemetry-sdk opentelemetry-exporter-otlp
 ```
 </Step>

 <Step title="Set Environment Variables">
 ```bash
 export ARIZE_PHOENIX_API_KEY=<your-key>
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/arize_phoenix_via_openinference.py
 ```

 ```bash Windows
 python cookbook/observability/arize_phoenix_via_openinference.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Arize Phoenix via OpenInference (Local Collector)
Source: https://docs.agno.com/examples/concepts/observability/arize-phoenix-via-openinference-local

## Overview

This example demonstrates how to instrument your Agno agent with OpenInference and send traces to a local Arize Phoenix collector.

## Code

```python
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from phoenix.otel import register

# Set the local collector endpoint for Arize Phoenix
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"

# Configure the Phoenix tracer
tracer_provider = register(
 project_name="agno-stock-price-agent", # Default is 'default'
 auto_instrument=True, # Automatically use the installed OpenInference instrumentation
)

# Create and configure the agent
agent = Agent(
 name="Stock Price Agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[YFinanceTools()],
 instructions="You are a stock price agent. Answer questions in the style of a stock analyst.",
 debug_mode=True,
)

# Use the agent
agent.print_response("What is the current price of Tesla?")
```

## Usage

<Steps>
 <Step title="Install Dependencies">
 ```bash
 pip install agno arize-phoenix openai openinference-instrumentation-agno opentelemetry-sdk opentelemetry-exporter-otlp
 ```
 </Step>

 <Step title="Start Local Collector">
 Run the following command to start the local collector:

 ```bash
 phoenix serve
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/arize_phoenix_via_openinference_local.py
 ```

 ```bash Windows
 python cookbook/observability/arize_phoenix_via_openinference_local.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Langfuse via OpenInference
Source: https://docs.agno.com/examples/concepts/observability/langfuse_via_openinference

## Overview

This example demonstrates how to instrument your Agno agent with OpenInference and send traces to Langfuse.

## Code

```python
import base64
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

LANGFUSE_AUTH = base64.b64encode(
 f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
 "https://us.cloud.langfuse.com/api/public/otel" # 🇺🇸 US data region
)
# os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]="https://cloud.langfuse.com/api/public/otel" # 🇪🇺 EU data region
# os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]="http://localhost:3000/api/public/otel" # 🏠 Local deployment (>= v3.22.0)

os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# Start instrumenting agno
AgnoInstrumentor().instrument()

agent = Agent(
 name="Stock Price Agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[YFinanceTools()],
 instructions="You are a stock price agent. Answer questions in the style of a stock analyst.",
 debug_mode=True,
)

agent.print_response("What is the current price of Tesla?")
```

## Usage

<Steps>
 <Step title="Install Dependencies">
 ```bash
 pip install agno openai langfuse opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-agno
 ```
 </Step>

 <Step title="Set Environment Variables">
 ```bash
 export LANGFUSE_PUBLIC_KEY=<your-public-key>
 export LANGFUSE_SECRET_KEY=<your-secret-key>
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/langfuse_via_openinference.py
 ```

 ```bash Windows
 python cookbook/observability/langfuse_via_openinference.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Notes

* **Data Regions**: Adjust the `OTEL_EXPORTER_OTLP_ENDPOINT` for your data region or local deployment as needed:
 * `https://us.cloud.langfuse.com/api/public/otel` for the US region
 * `https://cloud.langfuse.com/api/public/otel` for the EU region
 * `http://localhost:3000/api/public/otel` for local deployment

# Langfuse via OpenLIT
Source: https://docs.agno.com/examples/concepts/observability/langfuse_via_openlit

## Overview

This example demonstrates how to use Langfuse via OpenLIT to trace model calls.

## Code

```python
import base64
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

LANGFUSE_AUTH = base64.b64encode(
 f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
).decode()

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = (
 "https://us.cloud.langfuse.com/api/public/otel" # 🇺🇸 US data region
)
# os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]="https://cloud.langfuse.com/api/public/otel" # 🇪🇺 EU data region
# os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]="http://localhost:3000/api/public/otel" # 🏠 Local deployment (>= v3.22.0)

os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

trace_provider = TracerProvider()
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

# Sets the global default tracer provider
from opentelemetry import trace

trace.set_tracer_provider(trace_provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)

import openlit

# Initialize OpenLIT instrumentation. The disable_batch flag is set to true to process traces immediately.
openlit.init(tracer=tracer, disable_batch=True)

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[DuckDuckGoTools()],
 markdown=True,
 debug_mode=True,
)

agent.print_response("What is currently trending on Twitter?")
```

## Usage

<Steps>
 <Step title="Install Dependencies">
 ```bash
 pip install agno openai langfuse openlit opentelemetry-sdk opentelemetry-exporter-otlp
 ```
 </Step>

 <Step title="Set Environment Variables">
 ```bash
 export LANGFUSE_PUBLIC_KEY=<your-public-key>
 export LANGFUSE_SECRET_KEY=<your-secret-key>
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/langfuse_via_openlit.py
 ```

 ```bash Windows
 python cookbook/observability/langfuse_via_openlit.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Notes

* **Data Regions**: Adjust the `OTEL_EXPORTER_OTLP_ENDPOINT` for your data region or local deployment as needed:
 * `https://us.cloud.langfuse.com/api/public/otel` for the US region
 * `https://cloud.langfuse.com/api/public/otel` for the EU region
 * `http://localhost:3000/api/public/otel` for local deployment

# LangSmith
Source: https://docs.agno.com/examples/concepts/observability/langsmith-via-openinference

## Overview

This example demonstrates how to instrument your Agno agent with OpenInference and send traces to LangSmith.

## Code

```python
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# Set the endpoint and headers for LangSmith
endpoint = "https://eu.api.smith.langchain.com/otel/v1/traces"
headers = {
 "x-api-key": os.getenv("LANGSMITH_API_KEY"),
 "Langsmith-Project": os.getenv("LANGSMITH_PROJECT"),
}

# Configure the tracer provider
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
 SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint, headers=headers))
)
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# Start instrumenting agno
AgnoInstrumentor().instrument()

# Create and configure the agent
agent = Agent(
 name="Stock Market Agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[DuckDuckGoTools()],
 markdown=True,
 debug_mode=True,
)

# Use the agent
agent.print_response("What is news on the stock market?")
```

## Usage

<Steps>
 <Step title="Install Dependencies">
 ```bash
 pip install agno openai openinference-instrumentation-agno opentelemetry-sdk opentelemetry-exporter-otlp
 ```
 </Step>

 <Step title="Set Environment Variables">
 ```bash
 export LANGSMITH_API_KEY=<your-key>
 export LANGSMITH_TRACING=true
 export LANGSMITH_ENDPOINT=https://eu.api.smith.langchain.com # or https://api.smith.langchain.com for US
 export LANGSMITH_PROJECT=<your-project-name>
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/langsmith_via_openinference.py
 ```

 ```bash Windows
 python cookbook/observability/langsmith_via_openinference.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Notes

* **Data Regions**: Choose the appropriate `LANGSMITH_ENDPOINT` based on your data region.

# Langtrace
Source: https://docs.agno.com/examples/concepts/observability/langtrace-op

## Overview

This example demonstrates how to instrument your Agno agent with Langtrace for tracing and monitoring.

## Code

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from langtrace_python_sdk import langtrace
from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span

# Initialize Langtrace
langtrace.init()

# Create and configure the agent
agent = Agent(
 name="Stock Price Agent",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[YFinanceTools()],
 instructions="You are a stock price agent. Answer questions in the style of a stock analyst.",
 debug_mode=True,
)

# Use the agent
agent.print_response("What is the current price of Tesla?")
```

## Usage

<Steps>
 <Step title="Install Dependencies">
 ```bash
 pip install agno openai langtrace-python-sdk
 ```
 </Step>

 <Step title="Set Environment Variables">
 ```bash
 export LANGTRACE_API_KEY=<your-key>
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/langtrace_op.py
 ```

 ```bash Windows
 python cookbook/observability/langtrace_op.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Notes

* **Initialization**: Call `langtrace.init()` to initialize Langtrace before using the agent.

# Weave
Source: https://docs.agno.com/examples/concepts/observability/weave-op

## Overview

This example demonstrates how to use Weave by Weights & Biases (WandB) to log model calls from your Agno agent.

## Code

```python
import weave
from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Create and configure the agent
agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True, debug_mode=True)

# Initialize Weave with your project name
weave.init("agno")

# Define a function to run the agent, decorated with weave.op()
@weave.op()
def run(content: str):
 return agent.run(content)

# Use the function to log a model call
run("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Step title="Install Weave">
 ```bash
 pip install agno openai weave
 ```
 </Step>

 <Step title="Authenticate with WandB">
 * Go to [WandB](https://wandb.ai) and copy your API key from [here](https://wandb.ai/authorize).
 * Enter your API key in the terminal when prompted, or export it as an environment variable:

 ```bash
 export WANDB_API_KEY=<your-api-key>
 ```
 </Step>

 <Step title="Run the Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/observability/weave_op.py
 ```

 ```bash Windows
 python cookbook/observability/weave_op.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Notes

* **Initialization**: Call `weave.init("project-name")` to initialize Weave with your project name.
* **Decorators**: Use `@weave.op()` to decorate functions you want to log with Weave.

# Agent Extra Metrics
Source: https://docs.agno.com/examples/concepts/others/agent_extra_metrics

This example shows how to get special token metrics like audio, cached and reasoning tokens.

## Code

```python cookbook/agent_concepts/other/agent_extra_metrics.py
import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.openai import OpenAIChat

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content

agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "sage", "format": "wav"},
 ),
 markdown=True,
 debug_mode=True,
)
agent.print_response(
 "What's in these recording?",
 audio=[Audio(content=wav_data, format="wav")],
)
# Showing input audio, output audio and total audio tokens metrics
print(f"Input audio tokens: {agent.run_response.metrics['input_audio_tokens']}")
print(f"Output audio tokens: {agent.run_response.metrics['output_audio_tokens']}")
print(f"Audio tokens: {agent.run_response.metrics['audio_tokens']}")

agent = Agent(
 model=OpenAIChat(id="o3-mini"),
 markdown=True,
 telemetry=False,
 monitoring=False,
 debug_mode=True,
)
agent.print_response(
 "Solve the trolley problem. Evaluate multiple ethical frameworks. Include an ASCII diagram of your solution.",
 stream=False,
)
# Showing reasoning tokens metrics
print(f"Reasoning tokens: {agent.run_response.metrics['reasoning_tokens']}")

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"), markdown=True, telemetry=False, monitoring=False
)
agent.run("Share a 2 sentence horror story" * 150)
agent.print_response("Share a 2 sentence horror story" * 150)
# Showing cached tokens metrics
print(f"Cached tokens: {agent.run_response.metrics['cached_tokens']}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U requests openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/agent_extra_metrics.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/agent_extra_metrics.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent Metrics
Source: https://docs.agno.com/examples/concepts/others/agent_metrics

This example shows how to get the metrics of an agent run.

## Code

```python cookbook/agent_concepts/other/agent_metrics.py
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from agno.utils.pprint import pprint_run_response
from rich.pretty import pprint

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[YFinanceTools(stock_price=True)],
 markdown=True,
 show_tool_calls=True,
)

run_stream: Iterator[RunResponse] = agent.run(
 "What is the stock price of NVDA", stream=True
)
pprint_run_response(run_stream, markdown=True)

# Print metrics per message
if agent.run_response.messages:
 for message in agent.run_response.messages:
 if message.role == "assistant":
 if message.content:
 print(f"Message: {message.content}")
 elif message.tool_calls:
 print(f"Tool calls: {message.tool_calls}")
 print("---" * 5, "Metrics", "---" * 5)
 pprint(message.metrics)
 print("---" * 20)

# Print the metrics
print("---" * 5, "Aggregated Metrics", "---" * 5)
pprint(agent.run_response.metrics)
# Print the session metrics
print("---" * 5, "Session Metrics", "---" * 5)
pprint(agent.session_metrics)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno yfinance rich
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/agent_metrics.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/agent_metrics.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Datetime Instructions
Source: https://docs.agno.com/examples/concepts/others/datetime_instructions

This example shows how to add the current date and time to the instructions of an agent.

## Code

```python cookbook/agent_concepts/other/datetime_instructions.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 add_datetime_to_instructions=True,
 timezone_identifier="Etc/UTC",
)
agent.print_response(
 "What is the current date and time? What is the current time in NYC?"
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/datetime_instructions.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/datetime_instructions.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Input High Fidelity
Source: https://docs.agno.com/examples/concepts/others/image_input_high_fidelity

This example shows how to use high fidelity images in an agent.

## Code

```python cookbook/agent_concepts/other/image_input_high_fidelity.py
from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 markdown=True,
)

agent.print_response(
 "What's in these images",
 images=[
 Image(
 url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
 detail="high",
 )
 ],
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/image_input_high_fidelity.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/image_input_high_fidelity.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Input as Dictionary
Source: https://docs.agno.com/examples/concepts/others/input_as_dict

This example shows how to pass a dictionary of messages as input to an agent.

## Code

```python cookbook/agent_concepts/other/input_as_dict.py
from agno.agent import Agent

Agent().print_response(
 {
 "role": "user",
 "content": [
 {"type": "text", "text": "What's in this image?"},
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
 },
 },
 ],
 },
 stream=True,
 markdown=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/input_as_dict.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/input_as_dict.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Input as List
Source: https://docs.agno.com/examples/concepts/others/input_as_list

This example shows how to pass a list of messages as input to an agent.

## Code

```python cookbook/agent_concepts/other/input_as_list.py
from agno.agent import Agent

Agent().print_response(
 [
 {"type": "text", "text": "What's in this image?"},
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
 },
 },
 ],
 stream=True,
 markdown=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/input_as_list.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/input_as_list.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Input as Message
Source: https://docs.agno.com/examples/concepts/others/input_as_message

This example shows how to pass a message as input to an agent.

## Code

```python cookbook/agent_concepts/other/input_as_message.py
from agno.agent import Agent, Message

Agent().print_response(
 Message(
 role="user",
 content=[
 {"type": "text", "text": "What's in this image?"},
 {
 "type": "image_url",
 "image_url": {
 "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
 },
 },
 ],
 ),
 stream=True,
 markdown=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/input_as_message.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/input_as_message.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Input as Messages List
Source: https://docs.agno.com/examples/concepts/others/input_as_messages_list

This example shows how to pass a list of messages as input to an agent.

## Code

```python cookbook/agent_concepts/other/input_as_messages_list.py
from agno.agent import Agent, Message

Agent().print_response(
 messages=[
 Message(
 role="user",
 content=[
 {"type": "text", "text": "Hi! My name is John."},
 ],
 ),
 Message(
 role="user",
 content=[
 {"type": "text", "text": "What are you capable of?"},
 ],
 ),
 ],
 stream=True,
 markdown=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/input_as_messages_list.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/input_as_messages_list.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Instructions
Source: https://docs.agno.com/examples/concepts/others/instructions

This example shows how to provide specific instructions to an agent.

## Code

```python cookbook/agent_concepts/other/instructions.py
from agno.agent import Agent

agent = Agent(instructions="Share a 2 sentence story about")
agent.print_response("Love in the year 12000.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/instructions.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/instructions.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Instructions via Function
Source: https://docs.agno.com/examples/concepts/others/instructions_via_function

This example shows how to pass a function as instructions to an agent.

## Code

```python cookbook/agent_concepts/other/instructions_via_function.py
from typing import List
from agno.agent import Agent

def get_instructions(agent: Agent) -> List[str]:
 return [
 f"Your name is {agent.name}!",
 "Talk in haiku's!",
 "Use poetry to answer questions.",
 ]

agent = Agent(
 name="AgentX",
 instructions=get_instructions,
 markdown=True,
 show_tool_calls=True,
)
agent.print_response("Who are you?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/instructions_via_function.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/instructions_via_function.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Intermediate Steps
Source: https://docs.agno.com/examples/concepts/others/intermediate_steps

This example shows how to use intermediate steps in an agent.

## Code

```python cookbook/agent_concepts/other/intermediate_steps.py
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools
from rich.pretty import pprint

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[YFinanceTools(stock_price=True)],
 markdown=True,
 show_tool_calls=True,
)

run_stream: Iterator[RunResponse] = agent.run(
 "What is the stock price of NVDA", stream=True, stream_intermediate_steps=True
)
for chunk in run_stream:
 pprint(chunk.to_dict())
 print("---" * 20)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno yfinance rich
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/intermediate_steps.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/intermediate_steps.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Location Instructions
Source: https://docs.agno.com/examples/concepts/others/location_instructions

Add the current location to the instructions of an agent.

This example shows how to add the current location to the instructions of an agent.

## Code

```python cookbook/agent_concepts/other/location_instructions.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 add_location_to_instructions=True,
)
agent.print_response(
 "What is current news about my city?"
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/location_instructions.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/location_instructions.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Response as Variable
Source: https://docs.agno.com/examples/concepts/others/response_as_variable

This example shows how to use the response of an agent as a variable.

## Code

```python cookbook/agent_concepts/other/response_as_variable.py
from typing import Iterator
from rich.pretty import pprint
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions=["Use tables where possible"],
 show_tool_calls=True,
 markdown=True,
)

run_response: RunResponse = agent.run("What is the stock price of NVDA")
pprint(run_response)

# run_response_strem: Iterator[RunResponse] = agent.run("What is the stock price of NVDA", stream=True)
# for response in run_response_strem:
# pprint(response)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno yfinance rich
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/response_as_variable.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/response_as_variable.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Scenario Testing
Source: https://docs.agno.com/examples/concepts/others/scenario_testing

This example shows how to use the [scenario](https://github.com/langwatch/scenario) testing library to test an agent.

## Code

```python cookbook/agent_concepts/other/scenario_testing.py
import pytest
from scenario import Scenario, TestingAgent, scenario_cache

Scenario.configure(testing_agent=TestingAgent(model="openai/gpt-4o-mini"))

@pytest.mark.agent_test
@pytest.mark.asyncio
async def test_vegetarian_recipe_agent():
 agent = VegetarianRecipeAgent()

 def vegetarian_recipe_agent(message, context):
 # Call your agent here
 return agent.run(message)

 # Define the scenario
 scenario = Scenario(
 "User is looking for a dinner idea",
 agent=vegetarian_recipe_agent,
 success_criteria=[
 "Recipe agent generates a vegetarian recipe",
 "Recipe includes a list of ingredients",
 "Recipe includes step-by-step cooking instructions",
 ],
 failure_criteria=[
 "The recipe is not vegetarian or includes meat",
 "The agent asks more than two follow-up questions",
 ],
 )

 # Run the scenario and get results
 result = await scenario.run()

 # Assert for pytest to know whether the test passed
 assert result.success

# Example agent implementation
from agno.agent import Agent
from agno.models.openai import OpenAIChat

class VegetarianRecipeAgent:
 def __init__(self):
 self.history = []

 @scenario_cache()
 def run(self, message: str):
 self.history.append({"role": "user", "content": message})

 agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 markdown=True,
 debug_mode=True,
 instructions="You are a vegetarian recipe agent",
 )

 response = agent.run(message)
 result = response.content
 print(result)
 self.history.append(result)

 return {"message": result}
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno scenario pytest pytest-asyncio
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 pytest cookbook/agent_concepts/other/scenario_testing.py
 ```

 ```bash Windows
 pytest cookbook/agent_concepts/other/scenario_testing.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Success Criteria
Source: https://docs.agno.com/examples/concepts/others/success_criteria

This example shows how to set the success criteria of an agent.

## Code

```python cookbook/agent_concepts/other/success_criteria.py
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.thinking import ThinkingTools

puzzle_master = Agent(
 model=Gemini(id="gemini-2.0-flash"),
 tools=[ThinkingTools(add_instructions=True)],
 instructions="You are a puzzle master for small logic puzzles.",
 show_tool_calls=False,
 markdown=False,
 stream_intermediate_steps=False,
 success_criteria="The puzzle has been solved correctly with all drinks uniquely assigned.",
)

prompt = """
Create a small logic puzzle:
Three friends—Alice, Bob, and Carol—each choose a different drink from tea, coffee, and milk.
Clues:
1. Alice does not drink tea.
2. The person who drinks coffee is not Carol.
Ask: Who drinks which beverage?
"""

puzzle_master.print_response(prompt, stream=True, show_reasoning=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-generativeai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/other/success_criteria.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/other/success_criteria.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic RAG with Agent UI
Source: https://docs.agno.com/examples/concepts/rag/agentic-rag-agent-ui

## Code

```python
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.playground import Playground, serve_playground_app
from agno.storage.postgres import PostgresStorage
from agno.vectordb.pgvector import PgVector, SearchType

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Use PgVector as the vector database and store embeddings in the `ai.recipes` table
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)

rag_agent = Agent(
 name="RAG Agent",
 agent_id="rag-agent",
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Add a tool to search the knowledge base which enables agentic RAG.
 # This is enabled by default when `knowledge` is provided to the Agent.
 search_knowledge=True,
 # Add a tool to read chat history.
 read_chat_history=True,
 # Store the agent sessions in the `ai.rag_agent_sessions` table
 storage=PostgresStorage(table_name="rag_agent_sessions", db_url=db_url),
 instructions=[
 "Always search your knowledge base first and use it if available.",
 "Share the page number or source URL of the information you used in your response.",
 "If health benefits are mentioned, include them in the response.",
 "Important: Use tables where possible.",
 ],
 markdown=True,
)

app = Playground(agents=[rag_agent]).get_app()

if __name__ == "__main__":
 # Load the knowledge base: Comment after first run as the knowledge base is already loaded
 knowledge_base.load(upsert=True)

 serve_playground_app("agentic_rag_agent_ui:app", reload=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai sqlalchemy 'psycopg[binary]' pgvector 'fastapi[standard]' agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/agentic_rag_agent_ui.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/agentic_rag_agent_ui.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic RAG with LanceDB
Source: https://docs.agno.com/examples/concepts/rag/agentic-rag-lancedb

## Code

```python
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType

# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Use LanceDB as the vector database and store embeddings in the `recipes` table
 vector_db=LanceDb(
 table_name="recipes",
 uri="tmp/lancedb",
 search_type=SearchType.vector,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Add a tool to search the knowledge base which enables agentic RAG.
 # This is enabled by default when `knowledge` is provided to the Agent.
 search_knowledge=True,
 show_tool_calls=True,
 markdown=True,
)
agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai lancedb tantivy pypdf sqlalchemy agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/agentic_rag_lancedb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/agentic_rag_lancedb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic RAG with PgVector
Source: https://docs.agno.com/examples/concepts/rag/agentic-rag-pgvector

## Code

```python
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.pgvector import PgVector, SearchType

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Use PgVector as the vector database and store embeddings in the `ai.recipes` table
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load(upsert=True)

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Add a tool to search the knowledge base which enables agentic RAG.
 # This is enabled by default when `knowledge` is provided to the Agent.
 search_knowledge=True,
 show_tool_calls=True,
 markdown=True,
)
agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai sqlalchemy 'psycopg[binary]' pgvector agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/agentic_rag_pgvector.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/agentic_rag_pgvector.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic RAG with Reranking
Source: https://docs.agno.com/examples/concepts/rag/agentic-rag-with-reranking

## Code

```python
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.reranker.cohere import CohereReranker
from agno.vectordb.lancedb import LanceDb, SearchType

# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Use LanceDB as the vector database and store embeddings in the `recipes` table
 vector_db=LanceDb(
 table_name="recipes",
 uri="tmp/lancedb",
 search_type=SearchType.vector,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 reranker=CohereReranker(model="rerank-multilingual-v3.0"), # Add a reranker
 ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Add a tool to search the knowledge base which enables agentic RAG.
 # This is enabled by default when `knowledge` is provided to the Agent.
 search_knowledge=True,
 show_tool_calls=True,
 markdown=True,
)
agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export COHERE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai lancedb tantivy pypdf sqlalchemy agno cohere
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/agentic_rag_with_reranking.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/agentic_rag_with_reranking.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# RAG with LanceDB and SQLite
Source: https://docs.agno.com/examples/concepts/rag/rag-with-lance-db-and-sqlite

## Code

```python
from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.ollama import Ollama
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb

# Define the database URL where the vector database will be stored
db_url = "/tmp/lancedb"

# Configure the language model
model = Ollama(id="llama3.1:8b")

# Create Ollama embedder
embedder = OllamaEmbedder(id="nomic-embed-text", dimensions=768)

# Create the vector database
vector_db = LanceDb(
 table_name="recipes", # Table name in the vector database
 uri=db_url, # Location to initiate/create the vector database
 embedder=embedder, # Without using this, it will use OpenAIChat embeddings by default
)

# Create a knowledge base from a PDF URL using LanceDb for vector storage and OllamaEmbedder for embedding
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

# Load the knowledge base without recreating it if it already exists in Vector LanceDB
knowledge_base.load(recreate=False)

# Set up SQL storage for the agent's data
storage = SqliteStorage(table_name="recipes", db_file="data.db")
storage.create() # Create the storage if it doesn't exist

# Initialize the Agent with various configurations including the knowledge base and storage
agent = Agent(
 session_id="session_id", # use any unique identifier to identify the run
 user_id="user", # user identifier to identify the user
 model=model,
 knowledge=knowledge_base,
 storage=storage,
 show_tool_calls=True,
 debug_mode=True, # Enable debug mode for additional information
)

# Use the agent to generate and print a response to a query, formatted in Markdown
agent.print_response(
 "What is the first step of making Gluai Buat Chi from the knowledge base?",
 markdown=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the installation instructions at [Ollama's website](https://ollama.ai)
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U lancedb sqlalchemy agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/rag_with_lance_db_and_sqlite.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/rag_with_lance_db_and_sqlite.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Traditional RAG with LanceDB
Source: https://docs.agno.com/examples/concepts/rag/traditional-rag-lancedb

## Code

```python
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb, SearchType

# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Use LanceDB as the vector database and store embeddings in the `recipes` table
 vector_db=LanceDb(
 table_name="recipes",
 uri="tmp/lancedb",
 search_type=SearchType.vector,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Enable RAG by adding references from AgentKnowledge to the user prompt.
 add_references=True,
 # Set as False because Agents default to `search_knowledge=True`
 search_knowledge=False,
 show_tool_calls=True,
 markdown=True,
)
agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai lancedb tantivy pypdf sqlalchemy agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/traditional_rag_lancedb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/traditional_rag_lancedb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Traditional RAG with PgVector
Source: https://docs.agno.com/examples/concepts/rag/traditional-rag-pgvector

## Code

```python
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.pgvector import PgVector, SearchType

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 # Use PgVector as the vector database and store embeddings in the `ai.recipes` table
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load(upsert=True)

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 # Enable RAG by adding context from the `knowledge` to the user prompt.
 add_references=True,
 # Set as False because Agents default to `search_knowledge=True`
 search_knowledge=False,
 markdown=True,
)
agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai sqlalchemy 'psycopg[binary]' pgvector pypdf agno
 ```
 </Step>

 <Step title="Run PgVector">
 ```bash
 docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agnohq/pgvector:16
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/rag/traditional_rag_pgvector.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/rag/traditional_rag_pgvector.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Reasoning Agent
Source: https://docs.agno.com/examples/concepts/reasoning/agents/basic-cot

This is a basic reasoning agent with chain of thought reasoning.

## Code

```python cookbook/reasoning/agents/analyse_treaty_of_versailles.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

task = (
 "Analyze the key factors that led to the signing of the Treaty of Versailles in 1919. "
 "Discuss the political, economic, and social impacts of the treaty on Germany and how it "
 "contributed to the onset of World War II. Provide a nuanced assessment that includes "
 "multiple historical perspectives."
)

reasoning_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning=True,
 markdown=True,
)
reasoning_agent.print_response(task, stream=True, show_full_reasoning=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/agents/analyse_treaty_of_versailles.py
 ```

 ```bash Windows
 python cookbook/reasoning/agents/analyse_treaty_of_versailles.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Capture Reasoning Content
Source: https://docs.agno.com/examples/concepts/reasoning/agents/capture-reasoning-content-cot

This example demonstrates how to access and print the `reasoning_content`
when using either `reasoning=True` or setting a specific `reasoning_model`.

## Code

```python cookbook/reasoning/agents/capture_reasoning_content_default_COT.py

from agno.agent import Agent
from agno.models.openai import OpenAIChat

print("\n=== Example 1: Using reasoning=True (default COT) ===\n")

# Create agent with reasoning=True (default model COT)
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning=True,
 markdown=True,
)

# Run the agent (non-streaming)
print("Running with reasoning=True (non-streaming)...")
response = agent.run("What is the sum of the first 10 natural numbers?")

# Print the reasoning_content
print("\n--- reasoning_content from response ---")
if hasattr(response, "reasoning_content") and response.reasoning_content:
 print(response.reasoning_content)
else:
 print("No reasoning_content found in response")

print("\n\n=== Example 2: Using a custom reasoning_model ===\n")

# Create agent with a specific reasoning_model
agent_with_reasoning_model = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning_model=OpenAIChat(id="gpt-4o"), # Should default to manual COT
 markdown=True,
)

# Run the agent (non-streaming)
print("Running with reasoning_model specified (non-streaming)...")
response = agent_with_reasoning_model.run(
 "What is the sum of the first 10 natural numbers?"
)

# Print the reasoning_content
print("\n--- reasoning_content from response ---")
if hasattr(response, "reasoning_content") and response.reasoning_content:
 print(response.reasoning_content)
else:
 print("No reasoning_content found in response")

print("\n\n=== Example 3: Streaming with reasoning=True ===\n")

# Create a fresh agent for streaming
streaming_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning=True,
 markdown=True,
)

# Print response (which includes processing streaming responses)
print("Running with reasoning=True (streaming)...")
streaming_agent.print_response(
 "What is the value of 5! (factorial)?",
 stream=True,
 show_full_reasoning=True,
)

# Access reasoning_content from the agent's run_response after streaming
print("\n--- reasoning_content from agent.run_response after streaming ---")
if (
 hasattr(streaming_agent, "run_response")
 and streaming_agent.run_response
 and hasattr(streaming_agent.run_response, "reasoning_content")
 and streaming_agent.run_response.reasoning_content
):
 print(streaming_agent.run_response.reasoning_content)
else:
 print("No reasoning_content found in agent.run_response after streaming")

print("\n\n=== Example 4: Streaming with reasoning_model ===\n")

# Create a fresh agent with reasoning_model for streaming
streaming_agent_with_model = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning_model=OpenAIChat(id="gpt-4o"),
 markdown=True,
)

# Print response (which includes processing streaming responses)
print("Running with reasoning_model specified (streaming)...")
streaming_agent_with_model.print_response(
 "What is the value of 5! (factorial)?",
 stream=True,
 show_full_reasoning=True,
)

# Access reasoning_content from the agent's run_response after streaming
print("\n--- reasoning_content from agent.run_response after streaming ---")
if (
 hasattr(streaming_agent_with_model, "run_response")
 and streaming_agent_with_model.run_response
 and hasattr(streaming_agent_with_model.run_response, "reasoning_content")
 and streaming_agent_with_model.run_response.reasoning_content
):
 print(streaming_agent_with_model.run_response.reasoning_content)
else:
 print("No reasoning_content found in agent.run_response after streaming")

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/agents/capture_reasoning_content_default_COT.py
 ```

 ```bash Windows
 python cookbook/reasoning/agents/capture_reasoning_content_default_COT.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Non-Reasoning Model Agent
Source: https://docs.agno.com/examples/concepts/reasoning/agents/non-reasoning-model

This example demonstrates how it works when you pass a non-reasoning model as a reasoning model.
It defaults to using the default OpenAI reasoning model.
We recommend using the appropriate reasoning model or passing `reasoning=True` to use the default Chain-of-Thought reasoning.

## Code

```python cookbook/reasoning/agents/default_chain_of_thought.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

reasoning_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning_model=OpenAIChat(
 id="gpt-4o", max_tokens=1200
 ), # Should default to manual COT because it is not a native reasoning model
 markdown=True,
)
reasoning_agent.print_response(
 "Give me steps to write a python script for fibonacci series",
 stream=True,
 show_full_reasoning=True,
)

# It uses the default model of the Agent
reasoning_agent = Agent(
 model=OpenAIChat(id="gpt-4o", max_tokens=1200),
 reasoning=True,
 markdown=True,
)
reasoning_agent.print_response(
 "Give me steps to write a python script for fibonacci series",
 stream=True,
 show_full_reasoning=True,
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/agents/default_chain_of_thought.py
 ```

 ```bash Windows
 python cookbook/reasoning/agents/default_chain_of_thought.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Azure AI Foundry
Source: https://docs.agno.com/examples/concepts/reasoning/models/azure-ai-foundary/azure-ai-foundary

## Code

```python cookbook/reasoning/models/azure_ai_foundry/reasoning_model_deepseek.py
import os

from agno.agent import Agent
from agno.models.azure import AzureAIFoundry

agent = Agent(
 model=AzureAIFoundry(id="gpt-4o"),
 reasoning=True,
 reasoning_model=AzureAIFoundry(
 id="DeepSeek-R1",
 azure_endpoint=os.getenv("AZURE_ENDPOINT"),
 api_key=os.getenv("AZURE_API_KEY"),
 ),
)

agent.print_response(
 "Solve the trolley problem. Evaluate multiple ethical frameworks. "
 "Include an ASCII diagram of your solution.",
 stream=True,
)

```

## Usage

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export AZURE_API_KEY=xxx
 export AZURE_ENDPOINT=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U azure-ai-inference agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/azure_ai_foundry/reasoning_model_deepseek.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/azure_ai_foundry/reasoning_model_deepseek.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Azure OpenAI o1
Source: https://docs.agno.com/examples/concepts/reasoning/models/azure-openai/o1

## Code

```python cookbook/reasoning/models/azure_openai/o1.py
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI

agent = Agent(model=AzureOpenAI(id="o1"))
agent.print_response(
 "Solve the trolley problem. Evaluate multiple ethical frameworks. "
 "Include an ASCII diagram of your solution.",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export AZURE_OPENAI_API_KEY=xxx
 export AZURE_OPENAI_ENDPOINT=xxx
 export AZURE_DEPLOYMENT=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/azure_openai/o1.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/azure_openai/o1.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Azure OpenAI o3
Source: https://docs.agno.com/examples/concepts/reasoning/models/azure-openai/o3-tools

## Code

```python ccookbook/reasoning/models/azure_openai/o3_mini_with_tools.py
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=AzureOpenAI(id="o3"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions="Use tables to display data.",
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Write a report comparing NVDA to TSLA", stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export AZURE_OPENAI_API_KEY=xxx
 export AZURE_OPENAI_ENDPOINT=xxx
 export AZURE_DEPLOYMENT=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python ccookbook/reasoning/models/azure_openai/o3_mini_with_tools.py
 ```

 ```bash Windows
 python ccookbook/reasoning/models/azure_openai/o3_mini_with_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Azure OpenAI GPT 4.1
Source: https://docs.agno.com/examples/concepts/reasoning/models/azure-openai/reasoning-model-gpt4-1

## Code

```python cookbook/reasoning/models/azure_openai/reasoning_model_gpt_4_1.py
from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI

agent = Agent(
 model=AzureOpenAI(id="gpt-4o-mini"), reasoning_model=AzureOpenAI(id="gpt-4.1")
)
agent.print_response(
 "Solve the trolley problem. Evaluate multiple ethical frameworks. "
 "Include an ASCII diagram of your solution.",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export AZURE_OPENAI_API_KEY=xxx
 export AZURE_OPENAI_ENDPOINT=xxx
 export AZURE_DEPLOYMENT=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/azure_openai/reasoning_model_gpt_4_1.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/azure_openai/reasoning_model_gpt_4_1.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# DeepSeek Reasoner
Source: https://docs.agno.com/examples/concepts/reasoning/models/deepseek/trolley-problem

## Code

```python cookbook/reasoning/models/deepseek/trolley_problem.py
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat

task = (
 "You are a philosopher tasked with analyzing the classic 'Trolley Problem'. In this scenario, a runaway trolley "
 "is barreling down the tracks towards five people who are tied up and unable to move. You are standing next to "
 "a large stranger on a footbridge above the tracks. The only way to save the five people is to push this stranger "
 "off the bridge onto the tracks below. This will kill the stranger, but save the five people on the tracks. "
 "Should you push the stranger to save the five people? Provide a well-reasoned answer considering utilitarian, "
 "deontological, and virtue ethics frameworks. "
 "Include a simple ASCII art diagram to illustrate the scenario."
)

reasoning_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 reasoning_model=DeepSeek(id="deepseek-reasoner"),
 markdown=True,
)
reasoning_agent.print_response(task, stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export DEEPSEEK_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/deepseek/trolley_problem.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/deepseek/trolley_problem.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Groq DeepSeek R1
Source: https://docs.agno.com/examples/concepts/reasoning/models/groq/groq-basic

## Code

```python cookbook/reasoning/models/groq/9_11_or_9_9.py
from agno.agent import Agent
from agno.models.groq import Groq

agent = Agent(
 model=Groq(
 id="deepseek-r1-distill-llama-70b", temperature=0.6, max_tokens=1024, top_p=0.95
 ),
 markdown=True,
)
agent.print_response("9.11 and 9.9 -- which is bigger?", stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GROQ_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U groq agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/groq/9_11_or_9_9.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/groq/9_11_or_9_9.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Groq Claude + DeepSeek R1
Source: https://docs.agno.com/examples/concepts/reasoning/models/groq/groq-plus-claude

## Code

```python cookbook/reasoning/models/groq/deepseek_plus_claude.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.groq import Groq

deepseek_plus_claude = Agent(
 model=Claude(id="claude-3-7-sonnet-20250219"),
 reasoning_model=Groq(
 id="deepseek-r1-distill-llama-70b", temperature=0.6, max_tokens=1024, top_p=0.95
 ),
)
deepseek_plus_claude.print_response("9.11 and 9.9 -- which is bigger?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GROQ_API_KEY=xxx
 export ANTHROPIC_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U groq anthropic agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/groq/deepseek_plus_claude.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/groq/deepseek_plus_claude.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Ollama DeepSeek R1
Source: https://docs.agno.com/examples/concepts/reasoning/models/ollama/ollama-basic

## Code

```python cookbook/reasoning/models/ollama/reasoning_model_deepseek.py
from agno.agent import Agent
from agno.models.ollama.chat import Ollama

agent = Agent(
 model=Ollama(id="llama3.2:latest"),
 reasoning_model=Ollama(id="deepseek-r1:14b", max_tokens=4096),
)
agent.print_response(
 "Solve the trolley problem. Evaluate multiple ethical frameworks. "
 "Include an ASCII diagram of your solution.",
 stream=True,
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.2:latest
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ollama agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/ollama/reasoning_model_deepseek.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/ollama/reasoning_model_deepseek.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# OpenAI o1 pro
Source: https://docs.agno.com/examples/concepts/reasoning/models/openai/o1-pro

## Code

```python cookbook/reasoning/models/openai/o1_pro.py
from agno.agent import Agent
from agno.models.openai import OpenAIResponses

agent = Agent(model=OpenAIResponses(id="o1-pro"))
agent.print_response(
 "Solve the trolley problem. Evaluate multiple ethical frameworks. "
 "Include an ASCII diagram of your solution.",
 stream=True,
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/openai/o1_pro.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/openai/o1_pro.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# OpenAI o3-mini
Source: https://docs.agno.com/examples/concepts/reasoning/models/openai/o3-mini-tools

## Code

```python cookbook/reasoning/models/openai/o3_mini_with_tools.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=OpenAIChat(id="o3-mini"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions="Use tables to display data.",
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Write a report comparing NVDA to TSLA", stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/openai/o3_mini_with_tools.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/openai/o3_mini_with_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# OpenAI o3-mini with reasoning effort
Source: https://docs.agno.com/examples/concepts/reasoning/models/openai/reasoning-effort

## Code

```python cookbook/reasoning/models/openai/reasoning_effort.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=OpenAIChat(id="o3-mini", reasoning_effort="high"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions="Use tables to display data.",
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Write a report comparing NVDA to TSLA", stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/openai/reasoning_effort.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/openai/reasoning_effort.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# xAI Grok 3 Mini
Source: https://docs.agno.com/examples/concepts/reasoning/models/xai/reasoning-effort

## Code

```python cookbook/reasoning/models/xai/reasoning_effort.py
from agno.agent import Agent
from agno.models.xai import xAI
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=xAI(id="grok-3-mini-fast", reasoning_effort="high"),
 tools=[
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 )
 ],
 instructions="Use tables to display data.",
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Write a report comparing NVDA to TSLA", stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export XAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/models/xai/reasoning_effort.py
 ```

 ```bash Windows
 python cookbook/reasoning/models/xai/reasoning_effort.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Team with Knowledge Tools
Source: https://docs.agno.com/examples/concepts/reasoning/teams/knowledge-tool-team

This is a team reasoning example with knowledge tools.

<Tip>
 Enabling the reasoning option on the team leader helps optimize delegation and enhances multi-agent collaboration by selectively invoking deeper reasoning when required.
</Tip>

## Code

```python cookbook/reasoning/teams/knowledge_tool_team.py
from textwrap import dedent

from agno.agent import Agent
from agno.knowledge.url import UrlKnowledge
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.knowledge import KnowledgeTools
from agno.tools.yfinance import YFinanceTools
from agno.vectordb.lancedb import LanceDb, SearchType

agno_docs = UrlKnowledge(
 urls=["https://www.paulgraham.com/read.html"],
 # Use LanceDB as the vector database and store embeddings in the `agno_docs` table
 vector_db=LanceDb(
 uri="tmp/lancedb",
 table_name="agno_docs",
 search_type=SearchType.hybrid,
 ),
)

knowledge_tools = KnowledgeTools(
 knowledge=agno_docs,
 think=True,
 search=True,
 analyze=True,
 add_few_shot=True,
)

web_agent = Agent(
 name="Web Search Agent",
 role="Handle web search requests",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[DuckDuckGoTools()],
 instructions="Always include sources",
 add_datetime_to_instructions=True,
)

finance_agent = Agent(
 name="Finance Agent",
 role="Handle financial data requests",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[
 YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)
 ],
 add_datetime_to_instructions=True,
)

team_leader = Team(
 name="Reasoning Finance Team",
 mode="coordinate",
 model=OpenAIChat(id="gpt-4o"),
 members=[
 web_agent,
 finance_agent,
 ],
 tools=[knowledge_tools],
 instructions=[
 "Only output the final answer, no other text.",
 "Use tables to display data",
 ],
 markdown=True,
 show_members_responses=True,
 enable_agentic_context=True,
 add_datetime_to_instructions=True,
 success_criteria="The team has successfully completed the task.",
 debug_mode=True,
)

def run_team(task: str):
 # Comment out after first run
 agno_docs.load(recreate=True)
 team_leader.print_response(
 task,
 stream=True,
 stream_intermediate_steps=True,
 show_full_reasoning=True,
 )

if __name__ == "__main__":
 run_team("What does Paul Graham talk about the need to read in this essay?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/teams/knowledge_tool_team.py
 ```

 ```bash Windows
 python cookbook/reasoning/teams/knowledge_tool_team.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Team with Reasoning Tools
Source: https://docs.agno.com/examples/concepts/reasoning/teams/reasoning-tool-team

This is a multi-agent team reasoning example with reasoning tools.

<Tip>
 Enabling the reasoning option on the team leader helps optimize delegation and enhances multi-agent collaboration by selectively invoking deeper reasoning when required.
</Tip>

## Code

```python cookbook/reasoning/teams/reasoning_finance_team.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
 name="Web Search Agent",
 role="Handle web search requests",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[DuckDuckGoTools()],
 instructions="Always include sources",
 add_datetime_to_instructions=True,
)

finance_agent = Agent(
 name="Finance Agent",
 role="Handle financial data requests",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[
 YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)
 ],
 instructions=[
 "You are a financial data specialist. Provide concise and accurate data.",
 "Use tables to display stock prices, fundamentals (P/E, Market Cap), and recommendations.",
 "Clearly state the company name and ticker symbol.",
 "Briefly summarize recent company-specific news if available.",
 "Focus on delivering the requested financial data points clearly.",
 ],
 add_datetime_to_instructions=True,
)

team_leader = Team(
 name="Reasoning Finance Team Leader",
 mode="coordinate",
 model=Claude(id="claude-3-7-sonnet-latest"),
 members=[
 web_agent,
 finance_agent,
 ],
 tools=[ReasoningTools(add_instructions=True)],
 instructions=[
 "Only output the final answer, no other text.",
 "Use tables to display data",
 ],
 markdown=True,
 show_members_responses=True,
 enable_agentic_context=True,
 add_datetime_to_instructions=True,
 success_criteria="The team has successfully completed the task.",
)

def run_team(task: str):
 team_leader.print_response(
 task,
 stream=True,
 stream_intermediate_steps=True,
 show_full_reasoning=True,
 )

if __name__ == "__main__":
 run_team(
 dedent("""\
 Analyze the impact of recent US tariffs on market performance across these key sectors:
 - Steel & Aluminum: (X, NUE, AA)
 - Technology Hardware: (AAPL, DELL, HPQ)
 - Agricultural Products: (ADM, BG, INGR)
 - Automotive: (F, GM, TSLA)

 For each sector:
 1. Compare stock performance before and after tariff implementation
 2. Identify supply chain disruptions and cost impact percentages
 3. Analyze companies' strategic responses (reshoring, price adjustments, supplier diversification)
 4. Assess analyst outlook changes directly attributed to tariff policies
 """)
 )

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 export ANTHROPIC_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai anthropic agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/teams/reasoning_finance_team.py
 ```

 ```bash Windows
 python cookbook/reasoning/teams/reasoning_finance_team.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Gemini with Reasoning Tools
Source: https://docs.agno.com/examples/concepts/reasoning/tools/gemini-reasoning-tools

## Code

```python cookbook/reasoning/tools/gemini_reasoning_tools.py
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.reasoning import ReasoningTools
from agno.tools.yfinance import YFinanceTools

reasoning_agent = Agent(
 model=Gemini(id="gemini-2.5-pro-preview-03-25"),
 tools=[
 ReasoningTools(
 think=True,
 analyze=True,
 add_instructions=True,
 ),
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 ),
 ],
 instructions="Use tables where possible",
 stream_intermediate_steps=True,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
)
reasoning_agent.print_response(
 "Write a report comparing NVDA to TSLA.", show_full_reasoning=True
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-genai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/tools/gemini_reasoning_tools.py
 ```

 ```bash Windows
 python cookbook/reasoning/tools/gemini_reasoning_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Gemini with Thinking Tools
Source: https://docs.agno.com/examples/concepts/reasoning/tools/gemini-thinking-tools

## Code

```python cookbook/reasoning/tools/gemini_finance_agent.py

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.thinking import ThinkingTools
from agno.tools.yfinance import YFinanceTools

thinking_agent = Agent(
 model=Gemini(id="gemini-2.0-flash"),
 tools=[
 ThinkingTools(add_instructions=True),
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 ),
 ],
 instructions="Use tables where possible",
 show_tool_calls=True,
 markdown=True,
 stream_intermediate_steps=True,
)
thinking_agent.print_response(
 "Write a report comparing NVDA to TSLA in detail", stream=True, show_reasoning=True
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GOOGLE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-genai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/tools/gemini_finance_agent.py
 ```

 ```bash Windows
 python cookbook/reasoning/tools/gemini_finance_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Agent with Knowledge Tools
Source: https://docs.agno.com/examples/concepts/reasoning/tools/knowledge-tools

## Code

```python cookbook/reasoning/tools/knowledge_tools.py

from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.url import UrlKnowledge
from agno.models.openai import OpenAIChat
from agno.tools.knowledge import KnowledgeTools
from agno.vectordb.lancedb import LanceDb, SearchType

# Create a knowledge base containing information from a URL
agno_docs = UrlKnowledge(
 urls=["https://docs.agno.com/llms-full.txt"],
 # Use LanceDB as the vector database and store embeddings in the `agno_docs` table
 vector_db=LanceDb(
 uri="tmp/lancedb",
 table_name="agno_docs",
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)

knowledge_tools = KnowledgeTools(
 knowledge=agno_docs,
 think=True,
 search=True,
 analyze=True,
 add_few_shot=True,
)

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[knowledge_tools],
 show_tool_calls=True,
 markdown=True,
)

if __name__ == "__main__":
 # Load the knowledge base, comment after first run
 agno_docs.load(recreate=True)
 agent.print_response("How do I build multi-agent teams with Agno?", stream=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai lancedb tantivy sqlalchemy agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/tools/knowledge_tools.py
 ```

 ```bash Windows
 python cookbook/reasoning/tools/knowledge_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Agent with Reasoning Tools
Source: https://docs.agno.com/examples/concepts/reasoning/tools/reasoning-tools

This example shows how to create an agent that uses the ReasoningTools to solve
complex problems through step-by-step reasoning. The agent breaks down questions,
analyzes intermediate results, and builds structured reasoning paths to arrive at
well-justified conclusions.

## Code

```python cookbook/reasoning/tools/reasoning_tools.py

from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

reasoning_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[ReasoningTools(add_instructions=True)],
 instructions=dedent("""\
 You are an expert problem-solving assistant with strong analytical skills! 🧠
 
 Your approach to problems:
 1. First, break down complex questions into component parts
 2. Clearly state your assumptions
 3. Develop a structured reasoning path
 4. Consider multiple perspectives
 5. Evaluate evidence and counter-arguments
 6. Draw well-justified conclusions
 
 When solving problems:
 - Use explicit step-by-step reasoning
 - Identify key variables and constraints
 - Explore alternative scenarios
 - Highlight areas of uncertainty
 - Explain your thought process clearly
 - Consider both short and long-term implications
 - Evaluate trade-offs explicitly
 
 For quantitative problems:
 - Show your calculations
 - Explain the significance of numbers
 - Consider confidence intervals when appropriate
 - Identify source data reliability
 
 For qualitative reasoning:
 - Assess how different factors interact
 - Consider psychological and social dynamics
 - Evaluate practical constraints
 - Address value considerations
 \
 """),
 add_datetime_to_instructions=True,
 stream_intermediate_steps=True,
 show_tool_calls=True,
 markdown=True,
)

# Example usage with a complex reasoning problem
reasoning_agent.print_response(
 "Solve this logic puzzle: A man has to take a fox, a chicken, and a sack of grain across a river. "
 "The boat is only big enough for the man and one item. If left unattended together, the fox will "
 "eat the chicken, and the chicken will eat the grain. How can the man get everything across safely?",
 stream=True,
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/tools/reasoning_tools.py
 ```

 ```bash Windows
 python cookbook/reasoning/tools/reasoning_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Reasoning Agent with Thinking Tools
Source: https://docs.agno.com/examples/concepts/reasoning/tools/thinking-tools

## Code

```python cookbook/reasoning/tools/claude_thinking_tools.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.thinking import ThinkingTools
from agno.tools.yfinance import YFinanceTools

reasoning_agent = Agent(
 model=Claude(id="claude-3-7-sonnet-latest"),
 tools=[
 ThinkingTools(add_instructions=True),
 YFinanceTools(
 stock_price=True,
 analyst_recommendations=True,
 company_info=True,
 company_news=True,
 ),
 ],
 instructions="Use tables where possible",
 markdown=True,
)

if __name__ == "__main__":
 reasoning_agent.print_response(
 "Write a report on NVDA. Only the report, no other text.",
 stream=True,
 show_full_reasoning=True,
 stream_intermediate_steps=True,
 )

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export ANTHROPIC_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/reasoning/tools/claude_thinking_tools.py
 ```

 ```bash Windows
 python cookbook/reasoning/tools/claude_thinking_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic State Management
Source: https://docs.agno.com/examples/concepts/state/01-session-state

This is a basic agent state management example which shows how to manage and update agent state by maintaining a dynamic shopping list.

## Code

```python cookbook/agent_concepts/state/session_state.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list."""
 agent.session_state["shopping_list"].append(item)
 return f"The shopping list is now {agent.session_state['shopping_list']}"

# Create an Agent that maintains state
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Initialize the session state with a counter starting at 0
 session_state={"shopping_list": []},
 tools=[add_item],
 # You can use variables from the session state in the instructions
 instructions="Current state (shopping list) is: {shopping_list}",
 # Important: Add the state to the messages
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response("Add milk, eggs, and bread to the shopping list", stream=True)
print(f"Final session state: {agent.session_state}")

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/state/session_state.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/state/session_state.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# State in Instructions
Source: https://docs.agno.com/examples/concepts/state/02-state-in-prompt

This example demonstrates how to inject `session_state` variables directly into the agent’s instructions using `add_state_in_messages`.

## Code

```python cookbook/agent_concepts/state/state_in_prompt.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Initialize the session state with a variable
 session_state={"user_name": "John"},
 # You can use variables from the session state in the instructions
 instructions="Users name is {user_name}",
 show_tool_calls=True,
 add_state_in_messages=True,
 markdown=True,
)

agent.print_response("What is my name?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/state/state_in_prompt.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/state/state_in_prompt.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Persistant State with Storage
Source: https://docs.agno.com/examples/concepts/state/03-session-state-storage

This example demonstrates how to persist an agent’s session state using a SQLite storage, allowing continuity across multiple runs.

## Code

```python cookbook/agent_concepts/state/session_state_storage.py

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

# Define a tool that adds an item to the shopping list
def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list."""
 if item not in agent.session_state["shopping_list"]:
 agent.session_state["shopping_list"].append(item)
 return f"The shopping list is now {agent.session_state['shopping_list']}"

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Fix the session id to continue the same session across execution cycles
 session_id="fixed_id_for_demo",
 # Initialize the session state with an empty shopping list
 session_state={"shopping_list": []},
 # Add a tool that adds an item to the shopping list
 tools=[add_item],
 # Store the session state in a SQLite database
 storage=SqliteStorage(table_name="agent_sessions", db_file="tmp/data.db"),
 # Add the current shopping list from the state in the instructions
 instructions="Current shopping list is: {shopping_list}",
 # Important: Set `add_state_in_messages=True`
 # to make `{shopping_list}` available in the instructions
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response("What's on my shopping list?", stream=True)
print(f"Session state: {agent.session_state}")
agent.print_response("Add milk, eggs, and bread", stream=True)
print(f"Session state: {agent.session_state}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/state/session_state_storage.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/state/session_state_storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Multi User State
Source: https://docs.agno.com/examples/concepts/state/04-session-state-user-id

This example demonstrates how to maintain state for each user in a multi-user environment

## Code

```python cookbook/agent_concepts/state/session_state_user_id.py
import json

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.utils.log import log_info

# In-memory database to store user shopping lists
# Organized by user ID and session ID
shopping_list = {}

def add_item(agent: Agent, item: str) -> str:
 """Add an item to the current user's shopping list."""
 current_user_id = agent.session_state["current_user_id"]
 current_session_id = agent.session_state["current_session_id"]
 shopping_list.setdefault(current_user_id, {}).setdefault(
 current_session_id, []
 ).append(item)
 return f"Item {item} added to the shopping list"

def remove_item(agent: Agent, item: str) -> str:
 """Remove an item from the current user's shopping list."""
 current_user_id = agent.session_state["current_user_id"]
 current_session_id = agent.session_state["current_session_id"]

 if (
 current_user_id not in shopping_list
 or current_session_id not in shopping_list[current_user_id]
 ):
 return f"No shopping list found for user {current_user_id} and session {current_session_id}"

 if item not in shopping_list[current_user_id][current_session_id]:
 return f"Item '{item}' not found in the shopping list for user {current_user_id} and session {current_session_id}"

 shopping_list[current_user_id][current_session_id].remove(item)
 return f"Item {item} removed from the shopping list"

def get_shopping_list(agent: Agent) -> str:
 """Get the current user's shopping list."""
 current_user_id = agent.session_state["current_user_id"]
 current_session_id = agent.session_state["current_session_id"]
 return f"Shopping list for user {current_user_id} and session {current_session_id}: \n{json.dumps(shopping_list[current_user_id][current_session_id], indent=2)}"

# Create an Agent that maintains state
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[add_item, remove_item, get_shopping_list],
 # Reference the in-memory database
 instructions=[
 "Current User ID: {current_user_id}",
 "Current Session ID: {current_session_id}",
 ],
 # Important: Add the state in the instructions
 add_state_in_messages=True,
 markdown=True,
)

user_id_1 = "john_doe"
user_id_2 = "mark_smith"
user_id_3 = "carmen_sandiago"

# Example usage
agent.print_response(
 "Add milk, eggs, and bread to the shopping list",
 stream=True,
 user_id=user_id_1,
 session_id="user_1_session_1",
)
agent.print_response(
 "Add tacos to the shopping list",
 stream=True,
 user_id=user_id_2,
 session_id="user_2_session_1",
)
agent.print_response(
 "Add apples and grapesto the shopping list",
 stream=True,
 user_id=user_id_3,
 session_id="user_3_session_1",
)
agent.print_response(
 "Remove milk from the shopping list",
 stream=True,
 user_id=user_id_1,
 session_id="user_1_session_1",
)
agent.print_response(
 "Add minced beef to the shopping list",
 stream=True,
 user_id=user_id_2,
 session_id="user_2_session_1",
)

# What is on Mark Smith's shopping list?
agent.print_response(
 "What is on Mark Smith's shopping list?",
 stream=True,
 user_id=user_id_2,
 session_id="user_2_session_1",
)

# New session, so new shopping list
agent.print_response(
 "Add chicken and soup to my list.",
 stream=True,
 user_id=user_id_2,
 session_id="user_3_session_2",
)

print(f"Final shopping lists: \n{json.dumps(shopping_list, indent=2)}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/state/session_state_user_id.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/state/session_state_user_id.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# State Management Across Multiple Runs
Source: https://docs.agno.com/examples/concepts/state/05-session-state-full-example

This example demonstrates how to build a stateful agent that can manage its state across multiple runs.

## Code

```python cookbook/agent_concepts/state/shopping_list.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Define tools to manage our shopping list
def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list and return confirmation."""
 # Add the item if it's not already in the list
 if item.lower() not in [i.lower() for i in agent.session_state["shopping_list"]]:
 agent.session_state["shopping_list"].append(item)
 return f"Added '{item}' to the shopping list"
 else:
 return f"'{item}' is already in the shopping list"

def remove_item(agent: Agent, item: str) -> str:
 """Remove an item from the shopping list by name."""
 # Case-insensitive 
 for i, list_item in enumerate(agent.session_state["shopping_list"]):
 if list_item.lower() == item.lower():
 agent.session_state["shopping_list"].pop(i)
 return f"Removed '{list_item}' from the shopping list"

 return f"'{item}' was not found in the shopping list"

def list_items(agent: Agent) -> str:
 """List all items in the shopping list."""
 shopping_list = agent.session_state["shopping_list"]

 if not shopping_list:
 return "The shopping list is empty."

 items_text = "\n".join([f"- {item}" for item in shopping_list])
 return f"Current shopping list:\n{items_text}"

# Create a Shopping List Manager Agent that maintains state
agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 # Initialize the session state with an empty shopping list
 session_state={"shopping_list": []},
 tools=[add_item, remove_item, list_items],
 # You can use variables from the session state in the instructions
 instructions=dedent("""\
 Your job is to manage a shopping list.

 The shopping list starts empty. You can add items, remove items by name, and list all items.

 Current shopping list: {shopping_list}
 """),
 add_state_in_messages=True,
 markdown=True,
)

# Example usage
agent.print_response("Add milk, eggs, and bread to the shopping list", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("I got bread", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("I need apples and oranges", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response("whats on my list?", stream=True)
print(f"Session state: {agent.session_state}")

agent.print_response(
 "Clear everything from my list and start over with just bananas and yogurt",
 stream=True,
)
print(f"Session state: {agent.session_state}")

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/state/shopping_list.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/state/shopping_list.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Team with Shared State
Source: https://docs.agno.com/examples/concepts/state/06-team-session-state

This example demonstrates how a team of agents can collaboratively manage and update a shared session state.

## Code

```python cookbook/teams/team_with_shared_state.py
from agno.agent.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.team import Team

# Define tools to manage our shopping list
def add_item(agent: Agent, item: str) -> str:
 """Add an item to the shopping list and return confirmation.

 Args:
 item (str): The item to add to the shopping list.
 """
 # Add the item if it's not already in the list
 if item.lower() not in [
 i.lower() for i in agent.team_session_state["shopping_list"]
 ]:
 agent.team_session_state["shopping_list"].append(item)
 return f"Added '{item}' to the shopping list"
 else:
 return f"'{item}' is already in the shopping list"

def remove_item(agent: Agent, item: str) -> str:
 """Remove an item from the shopping list by name.

 Args:
 item (str): The item to remove from the shopping list.
 """
 # Case-insensitive 
 for i, list_item in enumerate(agent.team_session_state["shopping_list"]):
 if list_item.lower() == item.lower():
 agent.team_session_state["shopping_list"].pop(i)
 return f"Removed '{list_item}' from the shopping list"

 return f"'{item}' was not found in the shopping list. Current shopping list: {agent.team_session_state['shopping_list']}"

def remove_all_items(agent: Agent) -> str:
 """Remove all items from the shopping list."""
 agent.team_session_state["shopping_list"] = []
 return "All items removed from the shopping list"

shopping_list_agent = Agent(
 name="Shopping List Agent",
 role="Manage the shopping list",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[add_item, remove_item, remove_all_items],
 instructions=[
 "Find information about the company in the wikipedia",
 ],
)

def list_items(team: Team) -> str:
 """List all items in the shopping list."""
 shopping_list = team.session_state["shopping_list"]

 if not shopping_list:
 return "The shopping list is empty."

 items_text = "\n".join([f"- {item}" for item in shopping_list])
 return f"Current shopping list:\n{items_text}"

shopping_team = Team(
 name="Shopping List Team",
 mode="coordinate",
 model=OpenAIChat(id="gpt-4o-mini"),
 session_state={"shopping_list": []},
 tools=[list_items],
 members=[
 shopping_list_agent,
 ],
 show_tool_calls=True,
 markdown=True,
 instructions=[
 "You are a team that manages a shopping list.",
 "If you need to add or remove items from the shopping list, forward the full request to the shopping list agent (don't break it up into multiple requests).",
 "If you need to list the items in the shopping list, use the list_items tool.",
 "If the user got something from the shopping list, it means it can be removed from the shopping list.",
 ],
 show_members_responses=True,
)

# Example usage
shopping_team.print_response(
 "Add milk, eggs, and bread to the shopping list", stream=True
)
print(f"Session state: {shopping_team.session_state}")

shopping_team.print_response("I got bread", stream=True)
print(f"Session state: {shopping_team.session_state}")

shopping_team.print_response("I need apples and oranges", stream=True)
print(f"Session state: {shopping_team.session_state}")

shopping_team.print_response("whats on my list?", stream=True)
print(f"Session state: {shopping_team.session_state}")

shopping_team.print_response(
 "Clear everything from my list and start over with just bananas and yogurt",
 stream=True,
)
print(f"Session state: {shopping_team.session_state}")

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/teams/team_with_shared_state.py
 ```

 ```bash Windows
 python cookbook/teams/team_with_shared_state.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# DynamoDB Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/dynamodb

Agno supports using DynamoDB as a storage backend for Agents using the `DynamoDbStorage` class.

## Usage

You need to provide `aws_access_key_id` and `aws_secret_access_key` parameters to the `DynamoDbStorage` class.

```python dynamodb_storage_for_agent.py
from agno.storage.dynamodb import DynamoDbStorage

# AWS Credentials
AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")

storage = DynamoDbStorage(
 # store sessions in the ai.sessions table
 table_name="agent_sessions",
 # region_name: DynamoDB region name
 region_name="us-east-1",
 # aws_access_key_id: AWS access key id
 aws_access_key_id=AWS_ACCESS_KEY_ID,
 # aws_secret_access_key: AWS secret access key
 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# Add storage to the Agent
agent = Agent(storage=storage)
```

## Params

<Snippet file="storage-dynamodb-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/dynamodb_storage/dynamodb_storage_for_agent.py)

# JSON Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/json

Agno supports using local JSON files as a storage backend for Agents using the `JsonStorage` class.

## Usage

```python json_storage_for_agent.py
"""Run `pip install duckduckgo-search openai` to install dependencies."""

from agno.agent import Agent
from agno.storage.json import JsonStorage
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 storage=JsonStorage(dir_path="tmp/agent_sessions_json"),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Params

<Snippet file="storage-json-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/json_storage/json_storage_for_agent.py)

# Mongo Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/mongodb

Agno supports using MongoDB as a storage backend for Agents using the `MongoDbStorage` class.

## Usage

You need to provide either `db_url` or `client`. The following example uses `db_url`.

```python mongodb_storage_for_agent.py
from agno.storage.mongodb import MongoDbStorage

db_url = "mongodb://ai:ai@localhost:27017/agno"

# Create a storage backend using the Mongo database
storage = MongoDbStorage(
 # store sessions in the agent_sessions collection
 collection_name="agent_sessions",
 db_url=db_url,
)

# Add storage to the Agent
agent = Agent(storage=storage)
```

## Params

<Snippet file="storage-mongodb-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/mongodb_storage/mongodb_storage_for_agent.py)

# Postgres Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/postgres

Agno supports using PostgreSQL as a storage backend for Agents using the `PostgresStorage` class.

## Usage

### Run PgVector

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **PgVector** on port **5532** using:

```bash
docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agno/pgvector:16
```

```python postgres_storage_for_agent.py
from agno.storage.postgres import PostgresStorage

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create a storage backend using the Postgres database
storage = PostgresStorage(
 # store sessions in the ai.sessions table
 table_name="agent_sessions",
 # db_url: Postgres database URL
 db_url=db_url,
)

# Add storage to the Agent
agent = Agent(storage=storage)
```

## Params

<Snippet file="storage-postgres-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/postgres_storage/postgres_storage_for_agent.py)

# Redis Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/redis

Agno supports using Redis as a storage backend for Agents using the `RedisStorage` class.

## Usage

### Run Redis

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **Redis** on port **6379** using:

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

```python redis_storage_for_agent.py
from agno.agent import Agent
from agno.storage.redis import RedisStorage
from agno.tools.duckduckgo import DuckDuckGoTools

# Initialize Redis storage with default local connection
storage = RedisStorage(
 # Prefix for Redis keys to namespace the sessions
 prefix="agno_test",
 # Redis host address
 host="localhost",
 # Redis port number
 port=6379,
)

# Create agent with Redis storage
agent = Agent(
 storage=storage,
)
```

## Params

<Snippet file="storage-redis-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/redis_storage/redis_storage_for_agent.py)

# Singlestore Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/singlestore

Agno supports using Singlestore as a storage backend for Agents using the `SingleStoreStorage` class.

## Usage

Obtain the credentials for Singlestore from [here](https://portal.singlestore.com/)

```python singlestore_storage_for_agent.py
from os import getenv

from sqlalchemy.engine import create_engine

from agno.agent import Agent
from agno.storage.singlestore import SingleStoreStorage

# SingleStore Configuration
USERNAME = getenv("SINGLESTORE_USERNAME")
PASSWORD = getenv("SINGLESTORE_PASSWORD")
HOST = getenv("SINGLESTORE_HOST")
PORT = getenv("SINGLESTORE_PORT")
DATABASE = getenv("SINGLESTORE_DATABASE")
SSL_CERT = getenv("SINGLESTORE_SSL_CERT", None)

# SingleStore DB URL
db_url = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
if SSL_CERT:
 db_url += f"&ssl_ca={SSL_CERT}&ssl_verify_cert=true"

# Create a database engine
db_engine = create_engine(db_url)

# Create a storage backend using the Singlestore database
storage = SingleStoreStorage(
 # store sessions in the ai.sessions table
 table_name="agent_sessions",
 # db_engine: Singlestore database engine
 db_engine=db_engine,
 # schema: Singlestore schema
 schema=DATABASE,
)

# Add storage to the Agent
agent = Agent(storage=storage)
```

## Params

<Snippet file="storage-s2-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/singlestore_storage/singlestore_storage_for_agent.py)

# Sqlite Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/sqlite

Agno supports using Sqlite as a storage backend for Agents using the `SqliteStorage` class.

## Usage

You need to provide either `db_url`, `db_file` or `db_engine`. The following example uses `db_file`.

```python sqlite_storage_for_agent.py
from agno.storage.sqlite import SqliteStorage

# Create a storage backend using the Sqlite database
storage = SqliteStorage(
 # store sessions in the ai.sessions table
 table_name="agent_sessions",
 # db_file: Sqlite database file
 db_file="tmp/data.db",
)

# Add storage to the Agent
agent = Agent(storage=storage)
```

## Params

<Snippet file="storage-sqlite-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/sqllite_storage/sqlite_storage_for_agent.py)

# YAML Agent Storage
Source: https://docs.agno.com/examples/concepts/storage/agent_storage/yaml

Agno supports using local YAML files as a storage backend for Agents using the `YamlStorage` class.

## Usage

```python yaml_storage_for_agent.py
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.storage.yaml import YamlStorage

agent = Agent(
 storage=YamlStorage(path="tmp/agent_sessions_yaml"),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)

agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Params

<Snippet file="storage-yaml-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/yaml_storage/yaml_storage_for_agent.py)

# DynamoDB Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/dynamodb

Agno supports using DynamoDB as a storage backend for Teams using the `DynamoDbStorage` class.

## Usage

You need to provide `aws_access_key_id` and `aws_secret_access_key` parameters to the `DynamoDbStorage` class.

```python dynamodb_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.dynamodb import DynamoDbStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=DynamoDbStorage(table_name="team_sessions", region_name="us-east-1"),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-dynamodb-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/dynamodb_storage/dynamodb_storage_for_team.py)

# JSON Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/json

Agno supports using local JSON files as a storage backend for Teams using the `JsonStorage` class.

## Usage

```python json_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.json import JsonStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=JsonStorage(dir_path="tmp/team_sessions_json"),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-json-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/json_storage/json_storage_for_team.py)

# Mongo Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/mongodb

Agno supports using MongoDB as a storage backend for Teams using the `MongoDbStorage` class.

## Usage

You need to provide either `db_url` or `client`. The following example uses `db_url`.

```python mongodb_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.mongodb import MongoDbStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

# MongoDB connection settings
db_url = "mongodb://localhost:27017"

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=MongoDbStorage(
 collection_name="team_sessions", db_url=db_url, db_name="agno"
 ),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-mongodb-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/mongodb_storage/mongodb_storage_for_team.py)

# Postgres Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/postgres

Agno supports using PostgreSQL as a storage backend for Teams using the `PostgresStorage` class.

## Usage

### Run PgVector

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **PgVector** on port **5532** using:

```bash
docker run -d \
 -e POSTGRES_DB=ai \
 -e POSTGRES_USER=ai \
 -e POSTGRES_PASSWORD=ai \
 -e PGDATA=/var/lib/postgresql/data/pgdata \
 -v pgvolume:/var/lib/postgresql/data \
 -p 5532:5432 \
 --name pgvector \
 agno/pgvector:16
```

```python postgres_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=PostgresStorage(
 table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
 ),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")

```

## Params

<Snippet file="storage-postgres-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/postgres_storage/postgres_storage_for_team.py)

# Redis Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/redis

Agno supports using Redis as a storage backend for Teams using the `RedisStorage` class.

## Usage

### Run Redis

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **Redis** on port **6379** using:

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

```python redis_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno redis` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.redis import RedisStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

# Initialize Redis storage with default local connection
storage = RedisStorage(
 # Prefix for Redis keys to namespace the sessions
 prefix="agno_test",
 # Redis host address
 host="localhost",
 # Redis port number
 port=6379,
)

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=storage,
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-redis-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/redis_storage/redis_storage_for_team.py)

# Singlestore Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/singlestore

Agno supports using Singlestore as a storage backend for Teams using the `SingleStoreStorage` class.

## Usage

Obtain the credentials for Singlestore from [here](https://portal.singlestore.com/)

```python singlestore_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

import os
from os import getenv
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.singlestore import SingleStoreStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.utils.certs import download_cert
from pydantic import BaseModel
from sqlalchemy.engine import create_engine

# Configure SingleStore DB connection
USERNAME = getenv("SINGLESTORE_USERNAME")
PASSWORD = getenv("SINGLESTORE_PASSWORD")
HOST = getenv("SINGLESTORE_HOST")
PORT = getenv("SINGLESTORE_PORT")
DATABASE = getenv("SINGLESTORE_DATABASE")
SSL_CERT = getenv("SINGLESTORE_SSL_CERT", None)

# Download the certificate if SSL_CERT is not provided
if not SSL_CERT:
 SSL_CERT = download_cert(
 cert_url="https://portal.singlestore.com/static/ca/singlestore_bundle.pem",
 filename="singlestore_bundle.pem",
 )
 if SSL_CERT:
 os.environ["SINGLESTORE_SSL_CERT"] = SSL_CERT

# SingleStore DB URL
db_url = (
 f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
)
if SSL_CERT:
 db_url += f"&ssl_ca={SSL_CERT}&ssl_verify_cert=true"

# Create a DB engine
db_engine = create_engine(db_url)

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=SingleStoreStorage(
 table_name="agent_sessions",
 db_engine=db_engine,
 schema=DATABASE,
 auto_upgrade_schema=True,
 ),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-s2-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/singlestore_storage/singlestore_storage_for_team.py)

# Sqlite Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/sqlite

Agno supports using Sqlite as a storage backend for Teams using the `SqliteStorage` class.

## Usage

You need to provide either `db_url`, `db_file` or `db_engine`. The following example uses `db_file`.

```python sqlite_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=SqliteStorage(
 table_name="team_sessions", db_file="tmp/data.db", auto_upgrade_schema=True
 ),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-sqlite-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/sqllite_storage/sqlite_storage_for_team.py)

# YAML Team Storage
Source: https://docs.agno.com/examples/concepts/storage/team_storage/yaml

Agno supports using local YAML files as a storage backend for Teams using the `YamlStorage` class.

## Usage

```python yaml_storage_for_team.py
"""
Run: `pip install openai duckduckgo-search newspaper4k lxml_html_clean agno` to install the dependencies
"""

from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.yaml import YamlStorage
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from pydantic import BaseModel

class Article(BaseModel):
 title: str
 summary: str
 reference_links: List[str]

hn_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Gets top stories from hackernews.",
 tools=[HackerNewsTools()],
)

web_searcher = Agent(
 name="Web Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a topic",
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher],
 storage=YamlStorage(dir_path="tmp/team_sessions_yaml"),
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the web searcher to search for each story to get more information.",
 "Finally, provide a thoughtful and engaging summary.",
 ],
 response_model=Article,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

hn_team.print_response("Write an article about the top 2 stories on hackernews")
```

## Params

<Snippet file="storage-yaml-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/yaml_storage/yaml_storage_for_team.py)

# DynamoDB Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/dynamodb

Agno supports using DynamoDB as a storage backend for Workflows using the `DynamoDbStorage` class.

## Usage

You need to provide `aws_access_key_id` and `aws_secret_access_key` parameters to the `DynamoDbStorage` class.

```python dynamodb_storage_for_workflow.py
import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.dynamodb import DynamoDbStorage
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

class HackerNewsReporter(Workflow):
 description: str = (
 "Get the top stories from Hacker News and write a report on them."
 )

 hn_agent: Agent = Agent(
 description="Get the top stories from hackernews. "
 "Share all possible information, including url, score, title and summary if available.",
 show_tool_calls=True,
 )

 writer: Agent = Agent(
 tools=[Newspaper4kTools()],
 description="Write an engaging report on the top stories from hackernews.",
 instructions=[
 "You will be provided with top stories and their links.",
 "Carefully read each article and think about the contents",
 "Then generate a final New York Times worthy article",
 "Break the article into sections and provide key takeaways at the end.",
 "Make sure the title is catchy and engaging.",
 "Share score, title, url and summary of every article.",
 "Give the section relevant titles and provide details/facts/processes in each section."
 "Ignore articles that you cannot read or understand.",
 "REMEMBER: you are writing for the New York Times, so the quality of the article is important.",
 ],
 )

 def get_top_hackernews_stories(self, num_stories: int = 10) -> str:
 """Use this function to get top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to return. Defaults to 10.

 Returns:
 str: JSON string of top stories.
 """

 # Fetch top story IDs
 response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
 story_ids = response.json()

 # Fetch story details
 stories = []
 for story_id in story_ids[:num_stories]:
 story_response = httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
 )
 story = story_response.json()
 story["username"] = story["by"]
 stories.append(story)
 return json.dumps(stories)

 def run(self, num_stories: int = 5) -> Iterator[RunResponse]:
 # Set the tools for hn_agent here to avoid circular reference
 self.hn_agent.tools = [self.get_top_hackernews_stories]

 logger.info(f"Getting top {num_stories} stories from HackerNews.")
 top_stories: RunResponse = self.hn_agent.run(num_stories=num_stories)
 if top_stories is None or not top_stories.content:
 yield RunResponse(
 run_id=self.run_id, content="Sorry, could not get the top stories."
 )
 return

 logger.info("Reading each story and writing a report.")
 yield from self.writer.run(top_stories.content, stream=True)

if __name__ == "__main__":
 # Run workflow
 report: Iterator[RunResponse] = HackerNewsReporter(
 storage=DynamoDbStorage(
 table_name="workflow_sessions", region_name="us-east-1"
 ),
 debug_mode=False,
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="storage-dynamodb-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/dynamodb_storage/dynamodb_storage_for_workflow.py)

# JSON Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/json

Agno supports using local JSON files as a storage backend for Workflows using the `JsonStorage` class.

## Usage

```python json_storage_for_workflow.py
import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.json import JsonStorage
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

class HackerNewsReporter(Workflow):
 description: str = (
 "Get the top stories from Hacker News and write a report on them."
 )

 hn_agent: Agent = Agent(
 description="Get the top stories from hackernews. "
 "Share all possible information, including url, score, title and summary if available.",
 show_tool_calls=True,
 )

 writer: Agent = Agent(
 tools=[Newspaper4kTools()],
 description="Write an engaging report on the top stories from hackernews.",
 instructions=[
 "You will be provided with top stories and their links.",
 "Carefully read each article and think about the contents",
 "Then generate a final New York Times worthy article",
 "Break the article into sections and provide key takeaways at the end.",
 "Make sure the title is catchy and engaging.",
 "Share score, title, url and summary of every article.",
 "Give the section relevant titles and provide details/facts/processes in each section."
 "Ignore articles that you cannot read or understand.",
 "REMEMBER: you are writing for the New York Times, so the quality of the article is important.",
 ],
 )

 def get_top_hackernews_stories(self, num_stories: int = 10) -> str:
 """Use this function to get top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to return. Defaults to 10.

 Returns:
 str: JSON string of top stories.
 """

 # Fetch top story IDs
 response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
 story_ids = response.json()
