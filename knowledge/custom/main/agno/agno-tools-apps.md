
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
 storage=JsonStorage(dir_path="tmp/workflow_sessions_json"), debug_mode=False
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="storage-json-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/json_storage/json_storage_for_workflow.py)

# MongoDB Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/mongodb

Agno supports using MongoDB as a storage backend for Workflows using the `MongoDbStorage` class.

## Usage

### Run MongoDB

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **MongoDB** on port **27017** using:

```bash
docker run --name mongodb -d -p 27017:27017 mongodb/mongodb-community-server:latest
```

```python mongodb_storage_for_workflow.py
import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.mongodb import MongoDbStorage
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

db_url = "mongodb://localhost:27017"

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
 storage = MongoDbStorage(
 collection_name="agent_sessions", db_url=db_url, db_name="agno"
 )
 storage.drop()
 report: Iterator[RunResponse] = HackerNewsReporter(
 storage=storage, debug_mode=False
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="workflow-storage-mongodb-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/mongodb_storage/mongodb_storage_for_workflow.py)

# Postgres Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/postgres

Agno supports using PostgreSQL as a storage backend for Workflows using the `PostgresStorage` class.

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

```python postgres_storage_for_workflow.py
import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.postgres import PostgresStorage
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

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
 storage = PostgresStorage(table_name="agent_sessions", db_url=db_url)
 storage.drop()
 report: Iterator[RunResponse] = HackerNewsReporter(
 storage=storage, debug_mode=False
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="workflow-storage-postgres-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/postgres_storage/postgres_storage_for_workflow.py)

# Redis Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/redis

Agno supports using Redis as a storage backend for Workflows using the `RedisStorage` class.

## Usage

### Run Redis

Install [docker desktop](https://docs.docker.com/desktop/install/mac-install/) and run **Redis** on port **6379** using:

```bash
docker run --name my-redis -p 6379:6379 -d redis
```

```python redis_storage_for_workflow.py
"""
Run: `pip install openai httpx newspaper4k redis agno` to install the dependencies
"""

import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.redis import RedisStorage
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

# Initialize Redis storage with default local connection
storage = RedisStorage(
 # Prefix for Redis keys to namespace the sessions
 prefix="agno_test",
 # Redis host address
 host="localhost",
 # Redis port number
 port=6379,
)

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
 storage=storage, debug_mode=False
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="storage-redis-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/redis_storage/redis_storage_for_workflow.py)

# Singlestore Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/singlestore

Agno supports using Singlestore as a storage backend for Workflows using the `SingleStoreStorage` class.

## Usage

Obtain the credentials for Singlestore from [here](https://portal.singlestore.com/)

```python singlestore_storage_for_workflow.py
import json
import os
from os import getenv
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.singlestore import SingleStoreStorage
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.certs import download_cert
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow
from sqlalchemy.engine import create_engine

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
 db_url = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
 if SSL_CERT:
 db_url += f"&ssl_ca={SSL_CERT}&ssl_verify_cert=true"

 # Create a DB engine
 db_engine = create_engine(db_url)
 # Run workflow
 report: Iterator[RunResponse] = HackerNewsReporter(
 storage=SingleStoreStorage(
 table_name="workflow_sessions",
 mode="workflow",
 db_engine=db_engine,
 schema=DATABASE,
 ),
 debug_mode=False,
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="storage-s2-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/singlestore_storage/singlestore_storage_for_workflow.py)

# SQLite Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/sqlite

Agno supports using SQLite as a storage backend for Workflows using the `SqliteStorage` class.

## Usage

```python sqlite_storage_for_workflow

import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.sqlite import SqliteStorage
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
 storage = SqliteStorage(table_name="workflow_sessions", db_file="tmp/data.db")
 report: Iterator[RunResponse] = HackerNewsReporter(
 storage=storage, debug_mode=False
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="workflow-storage-sqlite-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/sqllite_storage/sqlite_storage_for_workflow.py)

# YAML Workflow Storage
Source: https://docs.agno.com/examples/concepts/storage/workflow_storage/yaml

Agno supports using local YAML files as a storage backend for Workflows using the `YamlStorage` class.

## Usage

```python yaml_storage_for_workflow.py
import json
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.run.response import RunResponse
from agno.storage.yaml import YamlStorage
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
 storage=YamlStorage(dir_path="tmp/workflow_sessions_yaml"), debug_mode=False
 ).run(num_stories=5)
 # Print the report
 pprint_run_response(report, markdown=True, show_time=True)
```

## Params

<Snippet file="storage-yaml-params.mdx" />

## Developer Resources

* View [Cookbook](https://github.com/agno-agi/agno/blob/main/cookbook/storage/yaml_storage/yaml_storage_for_workflow.py)

# CSV Tools
Source: https://docs.agno.com/examples/concepts/tools/database/csv

## Code

```python cookbook/tools/csv_tools.py
from pathlib import Path

import httpx
from agno.agent import Agent
from agno.tools.csv_toolkit import CsvTools

url = "https://agno-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv"
response = httpx.get(url)

imdb_csv = Path(__file__).parent.joinpath("imdb.csv")
imdb_csv.parent.mkdir(parents=True, exist_ok=True)
imdb_csv.write_bytes(response.content)

agent = Agent(
 tools=[CsvTools(csvs=[imdb_csv])],
 markdown=True,
 show_tool_calls=True,
 instructions=[
 "First always get the list of files",
 "Then check the columns in the file",
 "Then run the query to answer the question",
 ],
)
agent.cli_app(stream=False)
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
 pip install -U httpx openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/csv_tools.py
 ```

 ```bash Windows
 python cookbook/tools/csv_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# DuckDB Tools
Source: https://docs.agno.com/examples/concepts/tools/database/duckdb

## Code

```python cookbook/tools/duckdb_tools.py
from agno.agent import Agent
from agno.tools.duckdb import DuckDbTools

agent = Agent(
 tools=[DuckDbTools()],
 show_tool_calls=True,
 instructions="Use this file for Movies data: https://agno-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
)
agent.print_response(
 "What is the average rating of movies?", markdown=True, stream=False
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
 pip install -U duckdb openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/duckdb_tools.py
 ```

 ```bash Windows
 python cookbook/tools/duckdb_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/concepts/tools/database/pandas

Description:

Implemented an AI agent using the agno library with PandasTools for automated data analysis.

The agent loads a CSV file (data.csv) and performs analysis based on natural language instructions.

Enables interaction with data without manual Pandas coding, simplifying data exploration and insights extraction.

Includes setup instructions for environment variables and dependencies.

***

## title: Pandas Tools

## Code

```python cookbook/tools/pandas_tools.py
from agno.agent import Agent
from agno.tools.pandas import PandasTools

agent = Agent(
 tools=[PandasTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Load and analyze the dataset from data.csv")
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
 pip install -U pandas openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/pandas_tools.py
 ```

 ```bash Windows
 python cookbook/tools/pandas_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Postgres Tools
Source: https://docs.agno.com/examples/concepts/tools/database/postgres

## Code

```python cookbook/tools/postgres_tools.py
from agno.agent import Agent
from agno.tools.postgres import PostgresTools

agent = Agent(
 tools=[PostgresTools(db_url="postgresql://user:pass@localhost:5432/db")],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Show me all tables in the database")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set your database URL">
 ```bash
 export DATABASE_URL=postgresql://user:pass@localhost:5432/db
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U psycopg2-binary sqlalchemy openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/postgres_tools.py
 ```

 ```bash Windows
 python cookbook/tools/postgres_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# SQL Tools
Source: https://docs.agno.com/examples/concepts/tools/database/sql

## Code

```python cookbook/tools/sql_tools.py
from agno.agent import Agent
from agno.tools.sql import SQLTools

agent = Agent(
 tools=[SQLTools(db_url="sqlite:///database.db")],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Show me all tables in the database and their schemas")
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
 pip install -U sqlalchemy openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/sql_tools.py
 ```

 ```bash Windows
 python cookbook/tools/sql_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Zep Memory Tools
Source: https://docs.agno.com/examples/concepts/tools/database/zep

## Code

```python cookbook/tools/zep_tools.py
import time
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.zep import ZepTools

# Initialize the ZepTools
zep_tools = ZepTools(user_id="agno", session_id="agno-session", add_instructions=True)

# Initialize the Agent
agent = Agent(
 model=OpenAIChat(),
 tools=[zep_tools],
 context={"memory": zep_tools.get_zep_memory(memory_type="context")},
 add_context=True,
)

# Interact with the Agent so that it can learn about the user
agent.print_response("My name is John Billings")
agent.print_response("I live in NYC")
agent.print_response("I'm going to a concert tomorrow")

# Allow the memories to sync with Zep database
time.sleep(10)

# Refresh the context
agent.context["memory"] = zep_tools.get_zep_memory(memory_type="context")

# Ask the Agent about the user
agent.print_response("What do you know about me?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export ZEP_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U zep-cloud openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/zep_tools.py
 ```

 ```bash Windows
 python cookbook/tools/zep_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Zep Async Memory Tools
Source: https://docs.agno.com/examples/concepts/tools/database/zep_async

## Code

```python cookbook/tools/zep_async_tools.py
import asyncio
import time
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.zep import ZepAsyncTools

async def main():
 # Initialize the ZepAsyncTools
 zep_tools = ZepAsyncTools(
 user_id="agno", session_id="agno-async-session", add_instructions=True
 )

 # Initialize the Agent
 agent = Agent(
 model=OpenAIChat(),
 tools=[zep_tools],
 context={
 "memory": lambda: zep_tools.get_zep_memory(memory_type="context"),
 },
 add_context=True,
 )

 # Interact with the Agent
 await agent.aprint_response("My name is John Billings")
 await agent.aprint_response("I live in NYC")
 await agent.aprint_response("I'm going to a concert tomorrow")

 # Allow the memories to sync with Zep database
 time.sleep(10)

 # Refresh the context
 agent.context["memory"] = await zep_tools.get_zep_memory(memory_type="context")

 # Ask the Agent about the user
 await agent.aprint_response("What do you know about me?")

if __name__ == "__main__":
 asyncio.run(main())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export OPENAI_API_KEY=xxx
 export ZEP_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U zep-cloud openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/zep_async_tools.py
 ```

 ```bash Windows
 python cookbook/tools/zep_async_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Calculator
Source: https://docs.agno.com/examples/concepts/tools/local/calculator

## Code

```python cookbook/tools/calculator_tools.py
from agno.agent import Agent
from agno.tools.calculator import CalculatorTools

agent = Agent(
 tools=[
 CalculatorTools(
 add=True,
 subtract=True,
 multiply=True,
 divide=True,
 exponentiate=True,
 factorial=True,
 is_prime=True,
 square_root=True,
 )
 ],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("What is 10*5 then to the power of 2, do it step by step")
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
 python cookbook/tools/calculator_tools.py
 ```

 ```bash Windows
 python cookbook/tools/calculator_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Docker Tools
Source: https://docs.agno.com/examples/concepts/tools/local/docker

## Code

```python cookbook/tools/docker_tools.py
import sys
from agno.agent import Agent

try:
 from agno.tools.docker import DockerTools

 docker_tools = DockerTools(
 enable_container_management=True,
 enable_image_management=True,
 enable_volume_management=True,
 enable_network_management=True,
 )

 # Create an agent with Docker tools
 docker_agent = Agent(
 name="Docker Agent",
 instructions=[
 "You are a Docker management assistant that can perform various Docker operations.",
 "You can manage containers, images, volumes, and networks.",
 ],
 tools=[docker_tools],
 show_tool_calls=True,
 markdown=True,
 )

 # Example: List running containers
 docker_agent.print_response("List all running Docker containers", stream=True)

 # Example: List all images
 docker_agent.print_response("List all Docker images on this system", stream=True)

 # Example: Pull an image
 docker_agent.print_response("Pull the latest nginx image", stream=True)

 # Example: Run a container
 docker_agent.print_response(
 "Run an nginx container named 'web-server' on port 8080", stream=True
 )

 # Example: Get container logs
 docker_agent.print_response("Get logs from the 'web-server' container", stream=True)

 # Example: List volumes
 docker_agent.print_response("List all Docker volumes", stream=True)

 # Example: Create a network
 docker_agent.print_response(
 "Create a new Docker network called 'test-network'", stream=True
 )

 # Example: Stop and remove container
 docker_agent.print_response(
 "Stop and remove the 'web-server' container", stream=True
 )

except ValueError as e:
 print(f"\n❌ Docker Tool Error: {e}")
 print("\n🔍 Troubleshooting steps:")

 if sys.platform == "darwin": # macOS
 print("1. Ensure Docker Desktop is running")
 print("2. Check Docker Desktop settings")
 print("3. Try running 'docker ps' in terminal to verify access")

 elif sys.platform == "linux":
 print("1. Check if Docker service is running:")
 print(" systemctl status docker")
 print("2. Make sure your user has permissions to access Docker:")
 print(" sudo usermod -aG docker $USER")

 elif sys.platform == "win32":
 print("1. Ensure Docker Desktop is running")
 print("2. Check Docker Desktop settings")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Docker">
 Install Docker Desktop (for macOS/Windows) or Docker Engine (for Linux) from [Docker's official website](https://www.docker.com/products/docker-desktop).
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U docker agno
 ```
 </Step>

 <Step title="Start Docker">
 Make sure Docker is running on your system:

 * **macOS/Windows**: Start Docker Desktop application
 * **Linux**: Run `sudo systemctl start docker`
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac/Linux
 python cookbook/tools/docker_tools.py
 ```

 ```bash Windows
 python cookbook\tools\docker_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# File Tools
Source: https://docs.agno.com/examples/concepts/tools/local/file

## Code

```python cookbook/tools/file_tools.py
from pathlib import Path

from agno.agent import Agent
from agno.tools.file import FileTools

agent = Agent(tools=[FileTools(Path("tmp/file"))], show_tool_calls=True)
agent.print_response(
 "What is the most advanced LLM currently? Save the answer to a file.", markdown=True
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
 python cookbook/tools/file_tools.py
 ```

 ```bash Windows
 python cookbook/tools/file_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Python Tools
Source: https://docs.agno.com/examples/concepts/tools/local/python

## Code

```python cookbook/tools/python_tools.py
from agno.agent import Agent
from agno.tools.python import PythonTools

agent = Agent(
 tools=[PythonTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Calculate the factorial of 5 using Python")
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
 python cookbook/tools/python_tools.py
 ```

 ```bash Windows
 python cookbook/tools/python_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Shell Tools
Source: https://docs.agno.com/examples/concepts/tools/local/shell

## Code

```python cookbook/tools/shell_tools.py
from agno.agent import Agent
from agno.tools.shell import ShellTools

agent = Agent(
 tools=[ShellTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("List all files in the current directory")
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
 python cookbook/tools/shell_tools.py
 ```

 ```bash Windows
 python cookbook/tools/shell_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Sleep Tools
Source: https://docs.agno.com/examples/concepts/tools/local/sleep

## Code

```python cookbook/tools/sleep_tools.py
from agno.agent import Agent
from agno.tools.sleep import SleepTools

agent = Agent(
 tools=[SleepTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Wait for 5 seconds before continuing")
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
 python cookbook/tools/sleep_tools.py
 ```

 ```bash Windows
 python cookbook/tools/sleep_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Airbnb MCP agent
Source: https://docs.agno.com/examples/concepts/tools/mcp/airbnb

Using the [Airbnb MCP server](https://github.com/openbnb-org/mcp-server-airbnb) to create an Agent that can search for Airbnb listings:

```python
"""🏠 MCP Airbnb Agent - Search for Airbnb listings!

This example shows how to create an agent that uses MCP and Gemini 2.5 Pro to search for Airbnb listings.

Run: `pip install google-genai mcp agno` to install the dependencies
"""

import asyncio

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.mcp import MCPTools
from agno.utils.pprint import apprint_run_response

async def run_agent(message: str) -> None:
 async with MCPTools(
 "npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt"
 ) as mcp_tools:
 agent = Agent(
 model=Gemini(id="gemini-2.5-pro-exp-03-25"),
 tools=[mcp_tools],
 markdown=True,
 )

 response_stream = await agent.arun(message, stream=True)
 await apprint_run_response(response_stream, markdown=True)

if __name__ == "__main__":
 asyncio.run(
 run_agent(
 "What listings are available in San Francisco for 2 people for 3 nights from 1 to 4 August 2025?"
 )
 )

```

# GitHub MCP agent
Source: https://docs.agno.com/examples/concepts/tools/mcp/github

Using the [GitHub MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/github) to create an Agent that can explore, analyze and provide insights about GitHub repositories:

```python
"""🐙 MCP GitHub Agent - Your Personal GitHub Explorer!

This example shows how to create a GitHub agent that uses MCP to explore,
analyze, and provide insights about GitHub repositories. The agent leverages the Model
Context Protocol (MCP) to interact with GitHub, allowing it to answer questions
about issues, pull requests, repository details and more.

Example prompts to try:
- "List open issues in the repository"
- "Show me recent pull requests"
- "What are the repository statistics?"
- "Find issues labeled as bugs"
- "Show me contributor activity"

Run: `pip install agno mcp openai` to install the dependencies
Environment variables needed:
- Create a GitHub personal access token following these steps:
 - https://github.com/modelcontextprotocol/servers/tree/main/src/github#setup
- export GITHUB_TOKEN: Your GitHub personal access token
"""

import asyncio
import os
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

async def run_agent(message: str) -> None:
 """Run the GitHub agent with the given message."""

 # Initialize the MCP server
 server_params = StdioServerParameters(
 command="npx",
 args=["-y", "@modelcontextprotocol/server-github"],
 )

 # Create a client session to connect to the MCP server
 async with MCPTools(server_params=server_params) as mcp_tools:
 agent = Agent(
 tools=[mcp_tools],
 instructions=dedent("""\
 You are a GitHub assistant. Help users explore repositories and their activity.

 - Use headings to organize your responses
 - Be concise and focus on relevant information\
 """),
 markdown=True,
 show_tool_calls=True,
 )

 # Run the agent
 await agent.aprint_response(message, stream=True)

# Example usage
if __name__ == "__main__":
 # Pull request example
 asyncio.run(
 run_agent(
 "Tell me about Agno. Github repo: https://github.com/agno-agi/agno. You can read the README for more information."
 )
 )

# More example prompts to explore:
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

# Notion MCP agent
Source: https://docs.agno.com/examples/concepts/tools/mcp/notion

Using the [Notion MCP server](https://github.com/makenotion/notion-mcp-server) to create an Agent that can create, update and search for Notion pages:

```python
"""
Notion MCP Agent - Manages your documents

This example shows how to use the Agno MCP tools to interact with your Notion workspace.

1. Start by setting up a new internal integration in Notion: https://www.notion.so/profile/integrations
2. Export your new Notion key: `export NOTION_API_KEY=ntn_****`
3. Connect your relevant Notion pages to the integration. To do this, you'll need to visit that page, and click on the 3 dots, and select "Connect to integration".

Dependencies: pip install agno mcp openai

Usage:
 python cookbook/tools/mcp/notion_mcp_agent.py
"""

import asyncio
import json
import os
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

async def run_agent():
 token = os.getenv("NOTION_API_KEY")
 if not token:
 raise ValueError(
 "Missing Notion API key: provide --NOTION_API_KEY or set NOTION_API_KEY environment variable"
 )

 command = "npx"
 args = ["-y", "@notionhq/notion-mcp-server"]
 env = {
 "OPENAPI_MCP_HEADERS": json.dumps(
 {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}
 )
 }
 server_params = StdioServerParameters(command=command, args=args, env=env)

 async with MCPTools(server_params=server_params) as mcp_tools:
 agent = Agent(
 name="NotionDocsAgent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[mcp_tools],
 description="Agent to query and modify Notion docs via MCP",
 instructions=dedent("""\
 You have access to Notion documents through MCP tools.
 - Use tools to read, search, or update pages.
 - Confirm with the user before making modifications.
 """),
 markdown=True,
 show_tool_calls=True,
 )

 await agent.acli_app(
 message="You are a helpful assistant that can access Notion workspaces and pages.",
 stream=True,
 markdown=True,
 exit_on=["exit", "quit"],
 )

if __name__ == "__main__":
 asyncio.run(run_agent())
```

# Pipedream Auth
Source: https://docs.agno.com/examples/concepts/tools/mcp/pipedream_auth

This example shows how to add authorization when integrating Pipedream MCP servers with Agno Agents.

## Code

```python
"""
🔒 Using Pipedream MCP servers with authentication

This is an example of how to use Pipedream MCP servers with authentication.
This is useful if your app is interfacing with the MCP servers in behalf of your users.

1. Get your access token. You can check how in Pipedream's docs: https://pipedream.com/docs/connect/mcp/developers/
2. Get the URL of the MCP server. It will look like this: https://remote.mcp.pipedream.net/<External user id>/<MCP app slug>
3. Set the environment variables:
 - MCP_SERVER_URL: The URL of the MCP server you previously got
 - MCP_ACCESS_TOKEN: The access token you previously got
 - PIPEDREAM_PROJECT_ID: The project id of the Pipedream project you want to use
 - PIPEDREAM_ENVIRONMENT: The environment of the Pipedream project you want to use
3. Install dependencies: pip install agno mcp-sdk
"""

import asyncio
from os import getenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools, StreamableHTTPClientParams
from agno.utils.log import log_exception

mcp_server_url = getenv("MCP_SERVER_URL")
mcp_access_token = getenv("MCP_ACCESS_TOKEN")
pipedream_project_id = getenv("PIPEDREAM_PROJECT_ID")
pipedream_environment = getenv("PIPEDREAM_ENVIRONMENT")

server_params = StreamableHTTPClientParams(
 url=mcp_server_url,
 headers={
 "Authorization": f"Bearer {mcp_access_token}",
 "x-pd-project-id": pipedream_project_id,
 "x-pd-environment": pipedream_environment,
 },
)

async def run_agent(task: str) -> None:
 try:
 async with MCPTools(
 server_params=server_params, transport="streamable-http", timeout_seconds=20
 ) as mcp:
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[mcp],
 markdown=True,
 )
 await agent.aprint_response(message=task, stream=True)
 except Exception as e:
 log_exception(f"Unexpected error: {e}")

if __name__ == "__main__":
 # The agent can read channels, users, messages, etc.
 asyncio.run(run_agent("Show me the latest message in the channel #general"))
```

# Pipedream Google Calendar
Source: https://docs.agno.com/examples/concepts/tools/mcp/pipedream_google_calendar

This example shows how to use the Google Calendar Pipedream MCP server with Agno Agents.

## Code

```python
"""
🗓️ Pipedream Google Calendar MCP

This example shows how to use Pipedream MCP servers (in this case the Google Calendar one) with Agno Agents.

1. Connect your Pipedream and Google Calendar accounts: https://mcp.pipedream.com/app/google-calendar
2. Get your Pipedream MCP server url: https://mcp.pipedream.com/app/google-calendar
3. Set the MCP_SERVER_URL environment variable to the MCP server url you got above
4. Install dependencies: pip install agno mcp-sdk
"""

import asyncio
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from agno.utils.log import log_exception

mcp_server_url = os.getenv("MCP_SERVER_URL")

async def run_agent(task: str) -> None:
 try:
 async with MCPTools(
 url=mcp_server_url, transport="sse", timeout_seconds=20
 ) as mcp:
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[mcp],
 markdown=True,
 )
 await agent.aprint_response(
 message=task,
 stream=True,
 )
 except Exception as e:
 log_exception(f"Unexpected error: {e}")

if __name__ == "__main__":
 asyncio.run(
 run_agent("Tell me about all events I have in my calendar for tomorrow")
 )
```

# Pipedream LinkedIn
Source: https://docs.agno.com/examples/concepts/tools/mcp/pipedream_linkedin

This example shows how to use the LinkedIn Pipedream MCP server with Agno Agents.

## Code

```python
"""
💻 Pipedream LinkedIn MCP

This example shows how to use Pipedream MCP servers (in this case the LinkedIn one) with Agno Agents.

1. Connect your Pipedream and LinkedIn accounts: https://mcp.pipedream.com/app/linkedin
2. Get your Pipedream MCP server url: https://mcp.pipedream.com/app/linkedin
3. Set the MCP_SERVER_URL environment variable to the MCP server url you got above
4. Install dependencies: pip install agno mcp-sdk
"""

import asyncio
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from agno.utils.log import log_exception

mcp_server_url = os.getenv("MCP_SERVER_URL")

async def run_agent(task: str) -> None:
 try:
 async with MCPTools(
 url=mcp_server_url, transport="sse", timeout_seconds=20
 ) as mcp:
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[mcp],
 markdown=True,
 )
 await agent.aprint_response(
 message=task,
 stream=True,
 )
 except Exception as e:
 log_exception(f"Unexpected error: {e}")

if __name__ == "__main__":
 asyncio.run(
 run_agent("Check the Pipedream organization on LinkedIn and tell me about it")
 )
```

# Pipedream Slack
Source: https://docs.agno.com/examples/concepts/tools/mcp/pipedream_slack

This example shows how to use the Slack Pipedream MCP server with Agno Agents.

## Code

```python
"""
💬 Pipedream Slack MCP

This example shows how to use Pipedream MCP servers (in this case the Slack one) with Agno Agents.

1. Connect your Pipedream and Slack accounts: https://mcp.pipedream.com/app/slack
2. Get your Pipedream MCP server url: https://mcp.pipedream.com/app/slack
3. Set the MCP_SERVER_URL environment variable to the MCP server url you got above
4. Install dependencies: pip install agno mcp-sdk

"""

import asyncio
import os

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from agno.utils.log import log_exception

mcp_server_url = os.getenv("MCP_SERVER_URL")

async def run_agent(task: str) -> None:
 try:
 async with MCPTools(
 url=mcp_server_url, transport="sse", timeout_seconds=20
 ) as mcp:
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[mcp],
 markdown=True,
 )
 await agent.aprint_response(
 message=task,
 stream=True,
 )
 except Exception as e:
 log_exception(f"Unexpected error: {e}")

if __name__ == "__main__":
 # The agent can read channels, users, messages, etc.
 asyncio.run(run_agent("Show me the latest message in the channel #general"))

 # Use your real Slack name for this one to work!
 asyncio.run(
 run_agent("Send a message to <YOUR_NAME> saying 'Hello, I'm your Agno Agent!'")
 )
```

# Stripe MCP agent
Source: https://docs.agno.com/examples/concepts/tools/mcp/stripe

Using the [Stripe MCP server](https://github.com/stripe/agent-toolkit/tree/main/modelcontextprotocol) to create an Agent that can interact with the Stripe API:

```python
"""💵 Stripe MCP Agent - Manage Your Stripe Operations

This example demonstrates how to create an Agno agent that interacts with the Stripe API via the Model Context Protocol (MCP). This agent can create and manage Stripe objects like customers, products, prices, and payment links using natural language commands.

Setup:
2. Install Python dependencies: `pip install agno mcp-sdk`
3. Set Environment Variable: export STRIPE_SECRET_KEY=***.

Stripe MCP Docs: https://github.com/stripe/agent-toolkit
"""

import asyncio
import os
from textwrap import dedent

from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.utils.log import log_error, log_exception, log_info

async def run_agent(message: str) -> None:
 """
 Sets up the Stripe MCP server and initialize the Agno agent
 """
 # Verify Stripe API Key is available
 stripe_api_key = os.getenv("STRIPE_SECRET_KEY")
 if not stripe_api_key:
 log_error("STRIPE_SECRET_KEY environment variable not set.")
 return

 enabled_tools = "paymentLinks.create,products.create,prices.create,customers.create,customers.read"

 # handle different Operating Systems
 npx_command = "npx.cmd" if os.name == "nt" else "npx"

 try:
 # Initialize MCP toolkit with Stripe server
 async with MCPTools(
 command=f"{npx_command} -y @stripe/mcp --tools={enabled_tools} --api-key={stripe_api_key}"
 ) as mcp_toolkit:
 agent = Agent(
 name="StripeAgent",
 instructions=dedent("""\
 You are an AI assistant specialized in managing Stripe operations.
 You interact with the Stripe API using the available tools.

 - Understand user requests to create or list Stripe objects (customers, products, prices, payment links).
 - Clearly state the results of your actions, including IDs of created objects or lists retrieved.
 - Ask for clarification if a request is ambiguous.
 - Use markdown formatting, especially for links or code snippets.
 - Execute the necessary steps sequentially if a request involves multiple actions (e.g., create product, then price, then link).
 """),
 tools=[mcp_toolkit],
 markdown=True,
 show_tool_calls=True,
 )

 # Run the agent with the provided task
 log_info(f"Running agent with assignment: '{message}'")
 await agent.aprint_response(message, stream=True)

 except FileNotFoundError:
 error_msg = f"Error: '{npx_command}' command not found. Please ensure Node.js and npm/npx are installed and in your system's PATH."
 log_error(error_msg)
 except Exception as e:
 log_exception(f"An unexpected error occurred during agent execution: {e}")

if __name__ == "__main__":
 task = "Create a new Stripe product named 'iPhone'. Then create a price of $999.99 USD for it. Finally, create a payment link for that price."
 asyncio.run(run_agent(task))

# Example prompts:
"""
Customer Management:
- "Create a customer. Name: ACME Corp, Email: billing@acme.example.com"
- "List my customers."
- "Find customer by email 'jane.doe@example.com'" # Note: Requires 'customers.retrieve' or search capability

Product and Price Management:
- "Create a new product called 'Basic Plan'."
- "Create a recurring monthly price of $10 USD for product 'Basic Plan'."
- "Create a product 'Ebook Download' and a one-time price of $19.95 USD."
- "List all products." # Note: Requires 'products.list' capability
- "List all prices." # Note: Requires 'prices.list' capability

Payment Links:
- "Create a payment link for the $10 USD monthly 'Basic Plan' price."
- "Generate a payment link for the '$19.95 Ebook Download'."

Combined Tasks:
- "Create a product 'Pro Service', add a price $150 USD (one-time), and give me the payment link."
- "Register a new customer 'support@example.com' named 'Support Team'."
"""

```

# Supabase MCP agent
Source: https://docs.agno.com/examples/concepts/tools/mcp/supabase

Using the [Supabase MCP server](https://github.com/supabase-community/supabase-mcp) to create an Agent that can create projects, database schemas, edge functions, and more:

```python
"""🔑 Supabase MCP Agent - Showcase Supabase MCP Capabilities

This example demonstrates how to use the Supabase MCP server to create projects, database schemas, edge functions, and more.

Setup:
1. Install Python dependencies: `pip install agno mcp-sdk`
2. Create a Supabase Access Token: https://supabase.com/dashboard/account/tokens and set it as the SUPABASE_ACCESS_TOKEN environment variable.
"""

import asyncio
import os
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from agno.tools.reasoning import ReasoningTools
from agno.utils.log import log_error, log_exception, log_info

async def run_agent(task: str) -> None:
 token = os.getenv("SUPABASE_ACCESS_TOKEN")
 if not token:
 log_error("SUPABASE_ACCESS_TOKEN environment variable not set.")
 return

 npx_cmd = "npx.cmd" if os.name == "nt" else "npx"

 try:
 async with MCPTools(
 f"{npx_cmd} -y @supabase/mcp-server-supabase@latest --access-token={token}"
 ) as mcp:
 instructions = dedent(f"""
 You are an expert Supabase MCP architect. Given the project description:
 {task}

 Automatically perform the following steps :
 1. Plan the entire database schema based on the project description.
 2. Call `list_organizations` and select the first organization in the response.
 3. Use `get_cost(type='project')` to estimate project creation cost and mention the cost in your response.
 4. Create a new Supabase project with `create_project`, passing the confirmed cost ID.
 5. Poll project status with `get_project` until the status is `ACTIVE_HEALTHY`.
 6. Analyze the project requirements and propose a complete, normalized SQL schema (tables, columns, data types, indexes, constraints, triggers, and functions) as DDL statements.
 7. Apply the schema using `apply_migration`, naming the migration `initial_schema`.
 8. Validate the deployed schema via `list_tables` and `list_extensions`.
 8. Deploy a simple health-check edge function with `deploy_edge_function`.
 9. Retrieve and print the project URL (`get_project_url`) and anon key (`get_anon_key`).
 """)
 agent = Agent(
 model=OpenAIChat(id="o4-mini"),
 instructions=instructions,
 tools=[mcp, ReasoningTools(add_instructions=True)],
 markdown=True,
 )

 log_info(f"Running Supabase project agent for: {task}")
 await agent.aprint_response(
 message=task,
 stream=True,
 stream_intermediate_steps=True,
 show_full_reasoning=True,
 )
 except Exception as e:
 log_exception(f"Unexpected error: {e}")

if __name__ == "__main__":
 demo_description = (
 "Develop a cloud-based SaaS platform with AI-powered task suggestions, calendar syncing, predictive prioritization, "
 "team collaboration, and project analytics."
 )
 asyncio.run(run_agent(demo_description))

# Example prompts to try:
"""
A SaaS tool that helps businesses automate document processing using AI. Users can upload invoices, contracts, or PDFs and get structured data, smart summaries, and red flag alerts for compliance or anomalies. Ideal for legal teams, accountants, and enterprise back offices.

An AI-enhanced SaaS platform for streamlining the recruitment process. Features include automated candidate screening using NLP, AI interview scheduling, bias detection in job descriptions, and pipeline analytics. Designed for fast-growing startups and mid-sized HR teams.

An internal SaaS tool for HR departments to monitor employee wellbeing. Combines weekly mood check-ins, anonymous feedback, and AI-driven burnout detection models. Integrates with Slack and HR systems to support a healthier workplace culture.
"""

```

# Airflow Tools
Source: https://docs.agno.com/examples/concepts/tools/others/airflow

## Code

```python cookbook/tools/airflow_tools.py
from agno.agent import Agent
from agno.tools.airflow import AirflowTools

agent = Agent(
 tools=[AirflowTools(dags_dir="tmp/dags", save_dag=True, read_dag=True)],
 show_tool_calls=True,
 markdown=True,
)

dag_content = """
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
 'owner': 'airflow',
 'depends_on_past': False,
 'start_date': datetime(2024, 1, 1),
 'email_on_failure': False,
 'email_on_retry': False,
 'retries': 1,
 'retry_delay': timedelta(minutes=5),
}

# Using 'schedule' instead of deprecated 'schedule_interval'
with DAG(
 'example_dag',
 default_args=default_args,
 description='A simple example DAG',
 schedule='@daily', # Changed from schedule_interval
 catchup=False
) as dag:

 def print_hello():
 print("Hello from Airflow!")
 return "Hello task completed"

 task = PythonOperator(
 task_id='hello_task',
 python_callable=print_hello,
 dag=dag,
 )
"""

agent.run(f"Save this DAG file as 'example_dag.py': {dag_content}")
agent.print_response("Read the contents of 'example_dag.py'")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U apache-airflow openai agno
 ```
 </Step>

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/airflow_tools.py
 ```

 ```bash Windows
 python cookbook/tools/airflow_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Apify Tools
Source: https://docs.agno.com/examples/concepts/tools/others/apify

## Code

```python cookbook/tools/apify_tools.py
from agno.agent import Agent
from agno.tools.apify import ApifyTools

agent = Agent(tools=[ApifyTools()], show_tool_calls=True)
agent.print_response("Tell me about https://docs.agno.com/introduction", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export APIFY_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U apify-client openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/apify_tools.py
 ```

 ```bash Windows
 python cookbook/tools/apify_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# AWS Lambda Tools
Source: https://docs.agno.com/examples/concepts/tools/others/aws_lambda

## Code

```python cookbook/tools/aws_lambda_tools.py
from agno.agent import Agent
from agno.tools.aws_lambda import AWSLambdaTools

agent = Agent(
 tools=[AWSLambdaTools(region_name="us-east-1")],
 name="AWS Lambda Agent",
 show_tool_calls=True,
)

agent.print_response("List all Lambda functions in our AWS account", markdown=True)
agent.print_response(
 "Invoke the 'hello-world' Lambda function with an empty payload", markdown=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=xxx
 export AWS_SECRET_ACCESS_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/aws_lambda_tools.py
 ```

 ```bash Windows
 python cookbook/tools/aws_lambda_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Cal.com Tools
Source: https://docs.agno.com/examples/concepts/tools/others/calcom

## Code

```python cookbook/tools/calcom_tools.py
from datetime import datetime

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.calcom import CalComTools

agent = Agent(
 name="Calendar Assistant",
 instructions=[
 f"You're scheduing assistant. Today is {datetime.now()}.",
 "You can help users by:",
 " - Finding available time slots",
 " - Creating new bookings",
 " - Managing existing bookings (view, reschedule, cancel)",
 " - Getting booking details",
 " - IMPORTANT: In case of rescheduling or cancelling booking, call the get_upcoming_bookings function to get the booking uid. check available slots before making a booking for given time",
 "Always confirm important details before making bookings or changes.",
 ],
 model=OpenAIChat(id="gpt-4"),
 tools=[CalComTools(user_timezone="America/New_York")],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("What are my bookings for tomorrow?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export CALCOM_API_KEY=xxx
 export CALCOM_EVENT_TYPE_ID=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U requests pytz openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/calcom_tools.py
 ```

 ```bash Windows
 python cookbook/tools/calcom_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Composio Tools
Source: https://docs.agno.com/examples/concepts/tools/others/composio

## Code

```python cookbook/tools/composio_tools.py
from agno.agent import Agent
from composio_agno import Action, ComposioToolSet

toolset = ComposioToolSet()
composio_tools = toolset.get_tools(
 actions=[Action.GITHUB_STAR_A_REPOSITORY_FOR_THE_AUTHENTICATED_USER]
)

agent = Agent(tools=composio_tools, show_tool_calls=True)
agent.print_response("Can you star agno-agi/agno repo?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export COMPOSIO_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U composio-agno openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/composio_tools.py
 ```

 ```bash Windows
 python cookbook/tools/composio_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Confluence Tools
Source: https://docs.agno.com/examples/concepts/tools/others/confluence

## Code

```python cookbook/tools/confluence_tools.py
from agno.agent import Agent
from agno.tools.confluence import ConfluenceTools

agent = Agent(
 name="Confluence agent",
 tools=[ConfluenceTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("How many spaces are there and what are their names?")
agent.print_response(
 "What is the content present in page 'Large language model in LLM space'"
)
agent.print_response("Can you extract all the page names from 'LLM' space")
agent.print_response("Can you create a new page named 'TESTING' in 'LLM' space")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API credentials">
 ```bash
 export CONFLUENCE_API_TOKEN=xxx
 export CONFLUENCE_SITE_URL=xxx
 export CONFLUENCE_USERNAME=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U atlassian-python-api openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/confluence_tools.py
 ```

 ```bash Windows
 python cookbook/tools/confluence_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# DALL-E Tools
Source: https://docs.agno.com/examples/concepts/tools/others/dalle

## Code

```python cookbook/tools/dalle_tools.py
from pathlib import Path

from agno.agent import Agent
from agno.tools.dalle import DalleTools
from agno.utils.media import download_image

agent = Agent(tools=[DalleTools()], name="DALL-E Image Generator")

agent.print_response(
 "Generate an image of a futuristic city with flying cars and tall skyscrapers",
 markdown=True,
)

custom_dalle = DalleTools(
 model="dall-e-3", size="1792x1024", quality="hd", style="natural"
)

agent_custom = Agent(
 tools=[custom_dalle],
 name="Custom DALL-E Generator",
 show_tool_calls=True,
)

response = agent_custom.run(
 "Create a panoramic nature scene showing a peaceful mountain lake at sunset",
 markdown=True,
)
if response.images:
 download_image(
 url=response.images[0].url,
 save_path=Path(__file__).parent.joinpath("tmp/nature.jpg"),
 )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx # Required for DALL-E image generation
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
 python cookbook/tools/dalle_tools.py
 ```

 ```bash Windows
 python cookbook/tools/dalle_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Daytona Code Execution
Source: https://docs.agno.com/examples/concepts/tools/others/daytona

Learn to use Agno's Daytona integration to run your Agent-generated code in a secure sandbox.

## Code

```python cookbook/tools/daytona_tools.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.daytona import DaytonaTools

daytona_tools = DaytonaTools()

# Setup an Agent focused on coding tasks, with access to the Daytona tools
agent = Agent(
 name="Coding Agent with Daytona tools",
 agent_id="coding-agent",
 model=Claude(id="claude-sonnet-4-20250514"),
 tools=[daytona_tools],
 markdown=True,
 show_tool_calls=True,
 instructions=[
 "You are an expert at writing and validating Python code. You have access to a remote, secure Daytona sandbox.",
 "Your primary purpose is to:",
 "1. Write clear, efficient Python code based on user requests",
 "2. Execute and verify the code in the Daytona sandbox",
 "3. Share the complete code with the user, as this is the main use case",
 "4. Provide thorough explanations of how the code works",
 "You can use the run_python_code tool to run Python code in the Daytona sandbox.",
 "Guidelines:",
 "- ALWAYS share the complete code with the user, properly formatted in code blocks",
 "- Verify code functionality by executing it in the sandbox before sharing",
 "- Iterate and debug code as needed to ensure it works correctly",
 "- Use pandas, matplotlib, and other Python libraries for data analysis when appropriate",
 "- Create proper visualizations when requested and add them as image artifacts to show inline",
 "- Handle file uploads and downloads properly",
 "- Explain your approach and the code's functionality in detail",
 "- Format responses with both code and explanations for maximum clarity",
 "- Handle errors gracefully and explain any issues encountered",
 ],
)

agent.print_response(
 "Write Python code to generate the first 10 Fibonacci numbers and calculate their sum and average"
)
```

# Desi Vocal Tools
Source: https://docs.agno.com/examples/concepts/tools/others/desi_vocal

## Code

```python cookbook/tools/desi_vocal_tools.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.desi_vocal import DesiVocalTools

audio_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DesiVocalTools()],
 description="You are an AI agent that can generate audio using the DesiVocal API.",
 instructions=[
 "When the user asks you to generate audio, use the `text_to_speech` tool to generate the audio.",
 "You'll generate the appropriate prompt to send to the tool to generate audio.",
 "You don't need to find the appropriate voice first, I already specified the voice to user.",
 "Return the audio file name in your response. Don't convert it to markdown.",
 "Generate the text prompt we send in hindi language",
 ],
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
)

audio_agent.print_response(
 "Generate a very small audio of history of french revolution"
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export DESI_VOCAL_API_KEY=xxx
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
 python cookbook/tools/desi_vocal_tools.py
 ```

 ```bash Windows
 python cookbook/tools/desi_vocal_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# E2B Code Execution
Source: https://docs.agno.com/examples/concepts/tools/others/e2b

Learn to use Agno's E2B integration to run your Agent-generated code in a secure sandbox.

## Code

```python cookbook/tools/e2b_tools.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.e2b import E2BTools

e2b_tools = E2BTools(
 timeout=600, # 10 minutes timeout (in seconds)
 filesystem=True,
 internet_access=True,
 sandbox_management=True,
 command_execution=True,
)

agent = Agent(
 name="Code Execution Sandbox",
 agent_id="e2b-sandbox",
 model=OpenAIChat(id="gpt-4o"),
 tools=[e2b_tools],
 markdown=True,
 show_tool_calls=True,
 instructions=[
 "You are an expert at writing and validating Python code using a secure E2B sandbox environment.",
 "Your primary purpose is to:",
 "1. Write clear, efficient Python code based on user requests",
 "2. Execute and verify the code in the E2B sandbox",
 "3. Share the complete code with the user, as this is the main use case",
 "4. Provide thorough explanations of how the code works",
 ],
)

# Example: Generate Fibonacci numbers
agent.print_response(
 "Write Python code to generate the first 10 Fibonacci numbers and calculate their sum and average"
)

# Example: Data visualization
agent.print_response(
 "Write a Python script that creates a sample dataset of sales by region and visualize it with matplotlib"
)

# Example: Run a web server
agent.print_response(
 "Create a simple FastAPI web server that displays 'Hello from E2B Sandbox!' and run it to get a public URL"
)

# Example: Sandbox management
agent.print_response("What's the current status of our sandbox and how much time is left before timeout?")

# Example: File operations
agent.print_response("Create a text file with the current date and time, then read it back")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Create an E2B account">
 Create an account at [E2B](https://e2b.dev/) and get your API key from the dashboard.
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install e2b_code_interpreter
 ```
 </Step>

 <Step title="Set your API Key">
 <CodeGroup>
 ```bash Mac/Linux
 export E2B_API_KEY=your_api_key_here
 ```

 ```bash Windows (Command Prompt)
 set E2B_API_KEY=your_api_key_here
 ```

 ```bash Windows (PowerShell)
 $env:E2B_API_KEY="your_api_key_here"
 ```
 </CodeGroup>
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac/Linux
 python cookbook/tools/e2b_tools.py
 ```

 ```bash Windows
 python cookbook\tools\e2b_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Fal Tools
Source: https://docs.agno.com/examples/concepts/tools/others/fal

## Code

```python cookbook/tools/fal_tools.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.fal import FalTools

fal_agent = Agent(
 name="Fal Video Generator Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[FalTools("fal-ai/hunyuan-video")],
 description="You are an AI agent that can generate videos using the Fal API.",
 instructions=[
 "When the user asks you to create a video, use the `generate_media` tool to create the video.",
 "Return the URL as raw to the user.",
 "Don't convert video URL to markdown or anything else.",
 ],
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
)

fal_agent.print_response("Generate video of balloon in the ocean")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export FAL_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U fal openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/fal_tools.py
 ```

 ```bash Windows
 python cookbook/tools/fal_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Financial Datasets Tools
Source: https://docs.agno.com/examples/concepts/tools/others/financial_datasets

## Code

```python cookbook/tools/financial_datasets_tools.py
from agno.agent import Agent
from agno.tools.financial_datasets import FinancialDatasetsTools

agent = Agent(
 name="Financial Data Agent",
 tools=[
 FinancialDatasetsTools(), # For accessing financial data
 ],
 description="You are a financial data specialist that helps analyze financial information for stocks and cryptocurrencies.",
 instructions=[
 "When given a financial query:",
 "1. Use appropriate Financial Datasets methods based on the query type",
 "2. Format financial data clearly and highlight key metrics",
 "3. For financial statements, compare important metrics with previous periods when relevant",
 "4. Calculate growth rates and trends when appropriate",
 "5. Handle errors gracefully and provide meaningful feedback",
 ],
 markdown=True,
 show_tool_calls=True,
)

# Example 1: Financial Statements
print("\n=== Income Statement Example ===")
agent.print_response(
 "Get the most recent income statement for AAPL and highlight key metrics",
 stream=True,
)

# Example 2: Balance Sheet Analysis
print("\n=== Balance Sheet Analysis Example ===")
agent.print_response(
 "Analyze the balance sheets for MSFT over the last 3 years. Focus on debt-to-equity ratio and cash position.",
 stream=True,
)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API credentials">
 ```bash
 export FINANCIAL_DATASETS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/financial_datasets_tools.py
 ```

 ```bash Windows
 python cookbook/tools/financial_datasets_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Giphy Tools
Source: https://docs.agno.com/examples/concepts/tools/others/giphy

## Code

```python cookbook/tools/giphy_tools.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.giphy import GiphyTools

gif_agent = Agent(
 name="Gif Generator Agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[GiphyTools(limit=5)],
 description="You are an AI agent that can generate gifs using Giphy.",
 instructions=[
 "When the user asks you to create a gif, come up with the appropriate Giphy query and use the `search_gifs` tool to find the appropriate gif.",
 ],
 debug_mode=True,
 show_tool_calls=True,
)

gif_agent.print_response("I want a gif to send to a friend for their birthday.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export GIPHY_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U giphy_client openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/giphy_tools.py
 ```

 ```bash Windows
 python cookbook/tools/giphy_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# GitHub Tools
Source: https://docs.agno.com/examples/concepts/tools/others/github

## Code

```python cookbook/tools/github_tools.py
from agno.agent import Agent
from agno.tools.github import GithubTools

agent = Agent(
 instructions=[
 "Use your tools to answer questions about the repo: agno-agi/agno",
 "Do not create any issues or pull requests unless explicitly asked to do so",
 ],
 tools=[GithubTools()],
 show_tool_calls=True,
)
agent.print_response("List open pull requests", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your GitHub token">
 ```bash
 export GITHUB_TOKEN=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U PyGithub openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/github_tools.py
 ```

 ```bash Windows
 python cookbook/tools/github_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Google Calendar Tools
Source: https://docs.agno.com/examples/concepts/tools/others/google_calendar

## Code

```python cookbook/tools/google_calendar_tools.py
from agno.agent import Agent
from agno.tools.googlecalendar import GoogleCalendarTools

agent = Agent(
 tools=[GoogleCalendarTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("What events do I have today?")
agent.print_response("Schedule a meeting with John tomorrow at 2pm")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set up Google Calendar credentials">
 ```bash
 export GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-auth-oauthlib google-auth-httplib2 google-api-python-client openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/google_calendar_tools.py
 ```

 ```bash Windows
 python cookbook/tools/google_calendar_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Google Maps Tools
Source: https://docs.agno.com/examples/concepts/tools/others/google_maps

## Code

```python cookbook/tools/google_maps_tools.py
from agno.agent import Agent
from agno.tools.google_maps import GoogleMapTools
from agno.tools.crawl4ai import Crawl4aiTools # Optional: for enriching place data

agent = Agent(
 name="Maps API Demo Agent",
 tools=[
 GoogleMapTools(),
 Crawl4aiTools(max_length=5000), # Optional: for scraping business websites
 ],
 description="Location and business information specialist for mapping and location-based queries.",
 markdown=True,
 show_tool_calls=True,
)

# Example 1: Business 
print("\n=== Business Search Example ===")
agent.print_response(
 "Find me highly rated Indian restaurants in Phoenix, AZ with their contact details",
 markdown=True,
 stream=True,
)

# Example 2: Directions
print("\n=== Directions Example ===")
agent.print_response(
 """Get driving directions from 'Phoenix Sky Harbor Airport' to 'Desert Botanical Garden', 
 avoiding highways if possible""",
 markdown=True,
 stream=True,
)

# Example 3: Address Validation and Geocoding
print("\n=== Address Validation and Geocoding Example ===")
agent.print_response(
 """Please validate and geocode this address: 
 '1600 Amphitheatre Parkway, Mountain View, CA'""",
 markdown=True,
 stream=True,
)

# Example 4: Distance Matrix
print("\n=== Distance Matrix Example ===")
agent.print_response(
 """Calculate the travel time and distance between these locations in Phoenix:
 Origins: ['Phoenix Sky Harbor Airport', 'Downtown Phoenix']
 Destinations: ['Desert Botanical Garden', 'Phoenix Zoo']""",
 markdown=True,
 stream=True,
)

# Example 5: Location Analysis
print("\n=== Location Analysis Example ===")
agent.print_response(
 """Analyze this location in Phoenix:
 Address: '2301 N Central Ave, Phoenix, AZ 85004'
 Please provide:
 1. Exact coordinates
 2. Nearby landmarks
 3. Elevation data
 4. Local timezone""",
 markdown=True,
 stream=True,
)

# Example 6: Multi-mode Transit Comparison
print("\n=== Transit Options Example ===")
agent.print_response(
 """Compare different travel modes from 'Phoenix Convention Center' to 'Phoenix Art Museum':
 1. Driving
 2. Walking
 3. Transit (if available)
 Include estimated time and distance for each option.""",
 markdown=True,
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export GOOGLE_MAPS_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```

 Get your API key from the [Google Cloud Console](https://console.cloud.google.com/projectselector2/google/maps-apis/credentials)
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai googlemaps agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/google_maps_tools.py
 ```

 ```bash Windows
 python cookbook/tools/google_maps_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Jira Tools
Source: https://docs.agno.com/examples/concepts/tools/others/jira

## Code

```python cookbook/tools/jira_tools.py
from agno.agent import Agent
from agno.tools.jira import JiraTools

agent = Agent(
 tools=[JiraTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("List all open issues in project 'DEMO'")
agent.print_response("Create a new task in project 'DEMO' with high priority")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your Jira credentials">
 ```bash
 export JIRA_API_TOKEN=xxx
 export JIRA_SERVER_URL=xxx
 export JIRA_EMAIL=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U jira openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/jira_tools.py
 ```

 ```bash Windows
 python cookbook/tools/jira_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Linear Tools
Source: https://docs.agno.com/examples/concepts/tools/others/linear

## Code

```python cookbook/tools/linear_tools.py
from agno.agent import Agent
from agno.tools.linear import LinearTools

agent = Agent(
 tools=[LinearTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Show me all active issues")
agent.print_response("Create a new high priority task for the engineering team")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your Linear API key">
 ```bash
 export LINEAR_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U linear-sdk openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/linear_tools.py
 ```

 ```bash Windows
 python cookbook/tools/linear_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Luma Labs Tools
Source: https://docs.agno.com/examples/concepts/tools/others/lumalabs

## Code

```python cookbook/tools/lumalabs_tools.py
from agno.agent import Agent
from agno.tools.lumalabs import LumaLabsTools

agent = Agent(
 tools=[LumaLabsTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Generate a 3D model of a futuristic city")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LUMALABS_API_KEY=xxx
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
 python cookbook/tools/lumalabs_tools.py
 ```

 ```bash Windows
 python cookbook/tools/lumalabs_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# MLX Transcribe Tools
Source: https://docs.agno.com/examples/concepts/tools/others/mlx_transcribe

## Code

```python cookbook/tools/mlx_transcribe_tools.py
from agno.agent import Agent
from agno.tools.mlx_transcribe import MLXTranscribeTools

agent = Agent(
 tools=[MLXTranscribeTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Transcribe this audio file: path/to/audio.mp3")
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
 pip install -U mlx-transcribe openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/mlx_transcribe_tools.py
 ```

 ```bash Windows
 python cookbook/tools/mlx_transcribe_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Models Labs Tools
Source: https://docs.agno.com/examples/concepts/tools/others/models_labs

## Code

```python cookbook/tools/models_labs_tools.py
from agno.agent import Agent
from agno.tools.models_labs import ModelsLabsTools

agent = Agent(
 tools=[ModelsLabsTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Generate an image of a sunset over mountains")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export MODELS_LABS_API_KEY=xxx
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
 python cookbook/tools/models_labs_tools.py
 ```

 ```bash Windows
 python cookbook/tools/models_labs_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# OpenBB Tools
Source: https://docs.agno.com/examples/concepts/tools/others/openbb

## Code

```python cookbook/tools/openbb_tools.py
from agno.agent import Agent
from agno.tools.openbb import OpenBBTools

agent = Agent(
 tools=[OpenBBTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Get the latest stock price for AAPL")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENBB_PAT=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openbb openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/openbb_tools.py
 ```

 ```bash Windows
 python cookbook/tools/openbb_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Replicate Tools
Source: https://docs.agno.com/examples/concepts/tools/others/replicate

## Code

```python cookbook/tools/replicate_tools.py
from agno.agent import Agent
from agno.tools.replicate import ReplicateTools

agent = Agent(
 tools=[ReplicateTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Generate an image of a cyberpunk city")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API token">
 ```bash
 export REPLICATE_API_TOKEN=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U replicate openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/replicate_tools.py
 ```

 ```bash Windows
 python cookbook/tools/replicate_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Resend Tools
Source: https://docs.agno.com/examples/concepts/tools/others/resend

## Code

```python cookbook/tools/resend_tools.py
from agno.agent import Agent
from agno.tools.resend import ResendTools

agent = Agent(
 tools=[ResendTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Send an email to test@example.com with the subject 'Test Email'")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export RESEND_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U resend openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/resend_tools.py
 ```

 ```bash Windows
 python cookbook/tools/resend_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Todoist Tools
Source: https://docs.agno.com/examples/concepts/tools/others/todoist

## Code

```python cookbook/tools/todoist_tools.py
"""
Example showing how to use the Todoist Tools with Agno

Requirements:
- Sign up/login to Todoist and get a Todoist API Token (get from https://app.todoist.com/app/settings/integrations/developer)
- pip install todoist-api-python

Usage:
- Set the following environment variables:
 export TODOIST_API_TOKEN="your_api_token"

- Or provide them when creating the TodoistTools instance
"""

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.todoist import TodoistTools

todoist_agent = Agent(
 name="Todoist Agent",
 role="Manage your todoist tasks",
 instructions=[
 "When given a task, create a todoist task for it.",
 "When given a list of tasks, create a todoist task for each one.",
 "When given a task to update, update the todoist task.",
 "When given a task to delete, delete the todoist task.",
 "When given a task to get, get the todoist task.",
 ],
 agent_id="todoist-agent",
 model=OpenAIChat(id="gpt-4o"),
 tools=[TodoistTools()],
 markdown=True,
 debug_mode=True,
 show_tool_calls=True,
)

# Example 1: Create a task
print("\n=== Create a task ===")
todoist_agent.print_response("Create a todoist task to buy groceries tomorrow at 10am")

# Example 2: Delete a task
print("\n=== Delete a task ===")
todoist_agent.print_response(
 "Delete the todoist task to buy groceries tomorrow at 10am"
)

# Example 3: Get all tasks
print("\n=== Get all tasks ===")
todoist_agent.print_response("Get all the todoist tasks")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API Token">
 ```bash
 export TODOIST_API_TOKEN=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U todoist-api-python openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/todoist_tools.py
 ```

 ```bash Windows
 python cookbook/tools/todoist_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# YFinance Tools
Source: https://docs.agno.com/examples/concepts/tools/others/yfinance

## Code

```python cookbook/tools/yfinance_tools.py
from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 tools=[YFinanceTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Get the current stock price and recent history for AAPL")
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
 pip install -U yfinance openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/yfinance_tools.py
 ```

 ```bash Windows
 python cookbook/tools/yfinance_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# YouTube Tools
Source: https://docs.agno.com/examples/concepts/tools/others/youtube

## Code

```python cookbook/tools/youtube_tools.py
from agno.agent import Agent
from agno.tools.youtube import YouTubeTools

agent = Agent(
 tools=[YouTubeTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Search for recent videos about artificial intelligence")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export YOUTUBE_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-api-python-client openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/youtube_tools.py
 ```

 ```bash Windows
 python cookbook/tools/youtube_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Zendesk Tools
Source: https://docs.agno.com/examples/concepts/tools/others/zendesk

## Code

```python cookbook/tools/zendesk_tools.py
from agno.agent import Agent
from agno.tools.zendesk import ZendeskTools

agent = Agent(
 tools=[ZendeskTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Show me all open tickets")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set your Zendesk credentials">
 ```bash
 export ZENDESK_EMAIL=xxx
 export ZENDESK_TOKEN=xxx
 export ZENDESK_SUBDOMAIN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U zenpy openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/zendesk_tools.py
 ```

 ```bash Windows
 python cookbook/tools/zendesk_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# ArXiv Tools
Source: https://docs.agno.com/examples/concepts/tools/search/arxiv

## Code

```python cookbook/tools/arxiv_tools.py
from agno.agent import Agent
from agno.tools.arxiv_toolkit import ArxivTools

agent = Agent(tools=[ArxivTools()], show_tool_calls=True)
agent.print_response("Search arxiv for 'language models'", markdown=True)
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
 pip install -U arxiv openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/arxiv_tools.py
 ```

 ```bash Windows
 python cookbook/tools/arxiv_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Baidu Search Tools
Source: https://docs.agno.com/examples/concepts/tools/search/baidu
## Code

```python cookbook/tools/baidusearch_tools.py
from agno.agent import Agent
from agno.tools.baidusearch import BaiduSearchTools

agent = Agent(
 tools=[BaiduSearchTools()],
 description="You are a search agent that helps users find the most relevant information using Baidu.",
 instructions=[
 "Given a topic by the user, respond with the 3 most relevant search results about that topic.",
 "Search for 5 results and select the top 3 unique items.",
 "Search in both English and Chinese.",
 ],
 show_tool_calls=True,
)
agent.print_response("What are the latest advancements in AI?", markdown=True)
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
 python cookbook/tools/baidusearch_tools.py
 ```

 ```bash Windows
 python cookbook/tools/baidusearch_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Brave Search Tools
Source: https://docs.agno.com/examples/concepts/tools/search/brave
## Code

```python cookbook/tools/bravesearch_tools.py
from agno.agent import Agent
from agno.tools.bravesearch import BraveSearchTools

agent = Agent(
 tools=[BraveSearchTools()],
 description="You are a news agent that helps users find the latest news.",
 instructions=[
 "Given a topic by the user, respond with 4 latest news items about that topic."
 ],
 show_tool_calls=True,
)
agent.print_response("AI Agents", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API credentials">
 ```bash
 export BRAVE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U brave-search openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/bravesearch_tools.py
 ```

 ```bash Windows
 python cookbook/tools/bravesearch_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Crawl4ai Tools
Source: https://docs.agno.com/examples/concepts/tools/search/crawl4ai

## Code

```python cookbook/tools/crawl4ai_tools.py
from agno.agent import Agent
from agno.tools.crawl4ai import Crawl4aiTools

agent = Agent(tools=[Crawl4aiTools(max_length=None)], show_tool_calls=True)
agent.print_response("Tell me about https://github.com/agno-agi/agno.")
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
 pip install -U crawl4ai openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/crawl4ai_tools.py
 ```

 ```bash Windows
 python cookbook/tools/crawl4ai_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# DuckDuckGo 
Source: https://docs.agno.com/examples/concepts/tools/search/duckduckgo

## Code

```python cookbook/tools/duckduckgo_tools.py
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(tools=[DuckDuckGoTools()], show_tool_calls=True)
agent.print_response("Whats happening in France?", markdown=True)

# We will search DDG but limit the site to Politifact
agent = Agent(
 tools=[DuckDuckGoTools(modifier="site:politifact.com")], show_tool_calls=True
)
agent.print_response(
 "Is Taylor Swift promoting energy-saving devices with Elon Musk?", markdown=False
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
 pip install -U duckduckgo-search openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/duckduckgo_tools.py
 ```

 ```bash Windows
 python cookbook/tools/duckduckgo_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Exa Tools
Source: https://docs.agno.com/examples/concepts/tools/search/exa

## Code

```python cookbook/tools/exa_tools.py
from agno.agent import Agent
from agno.tools.exa import ExaTools

agent = Agent(
 tools=[ExaTools(include_domains=["cnbc.com", "reuters.com", "bloomberg.com"])],
 show_tool_calls=True,
)
agent.print_response("Search for AAPL news", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export EXA_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U exa-py openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/exa_tools.py
 ```

 ```bash Windows
 python cookbook/tools/exa_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Google Search Tools
Source: https://docs.agno.com/examples/concepts/tools/search/google_
## Code

```python cookbook/tools/googlesearch_tools.py
from agno.agent import Agent
from agno.tools.googlesearch import GoogleSearchTools

agent = Agent(
 tools=[GoogleSearchTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("What are the latest developments in AI?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API credentials">
 ```bash
 export GOOGLE_CSE_ID=xxx
 export GOOGLE_API_KEY=xxx
 export OPENAI_API_KEY=xxx 
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-api-python-client openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/googlesearch_tools.py
 ```

 ```bash Windows
 python cookbook/tools/googlesearch_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Hacker News Tools
Source: https://docs.agno.com/examples/concepts/tools/search/hackernews

## Code

```python cookbook/tools/hackernews_tools.py
from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools

agent = Agent(
 tools=[HackerNewsTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("What are the top stories on Hacker News right now?")
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
 python cookbook/tools/hackernews_tools.py
 ```

 ```bash Windows
 python cookbook/tools/hackernews_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PubMed Tools
Source: https://docs.agno.com/examples/concepts/tools/search/pubmed

## Code

```python cookbook/tools/pubmed_tools.py
from agno.agent import Agent
from agno.tools.pubmed import PubMedTools

agent = Agent(
 tools=[PubMedTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Find recent research papers about COVID-19 vaccines")
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
 pip install -U biopython openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/pubmed_tools.py
 ```

 ```bash Windows
 python cookbook/tools/pubmed_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# SearxNG Tools
Source: https://docs.agno.com/examples/concepts/tools/search/searxng

## Code

```python cookbook/tools/searxng_tools.py
from agno.agent import Agent
from agno.tools.searxng import SearxNGTools

agent = Agent(
 tools=[SearxNGTools(instance_url="https://your-searxng-instance.com")],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Search for recent news about artificial intelligence")
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
 pip install -U searxng-client openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/searxng_tools.py
 ```

 ```bash Windows
 python cookbook/tools/searxng_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# SerpAPI Tools
Source: https://docs.agno.com/examples/concepts/tools/search/serpapi

## Code

```python cookbook/tools/serpapi_tools.py
from agno.agent import Agent
from agno.tools.serpapi import SerpAPITools

agent = Agent(
 tools=[SerpAPITools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("What are the top search results for 'machine learning'?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export SERPAPI_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U google-search-results openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/serpapi_tools.py
 ```

 ```bash Windows
 python cookbook/tools/serpapi_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Tavily Tools
Source: https://docs.agno.com/examples/concepts/tools/search/tavily

## Code

```python cookbook/tools/tavily_tools.py
from agno.agent import Agent
from agno.tools.tavily import TavilyTools

agent = Agent(
 tools=[TavilyTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Search for recent breakthroughs in quantum computing")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export TAVILY_API_KEY=xxx
 export OPENAI_API_KEY=xxx 
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai tavily-python agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/tavily_tools.py
 ```

 ```bash Windows
 python cookbook/tools/tavily_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Wikipedia Tools
Source: https://docs.agno.com/examples/concepts/tools/search/wikipedia

## Code

```python cookbook/tools/wikipedia_tools.py
from agno.agent import Agent
from agno.tools.wikipedia import WikipediaTools

agent = Agent(
 tools=[WikipediaTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Search Wikipedia for information about artificial intelligence")
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
 pip install -U wikipedia openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/wikipedia_tools.py
 ```

 ```bash Windows
 python cookbook/tools/wikipedia_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Discord Tools
Source: https://docs.agno.com/examples/concepts/tools/social/discord

## Code

```python cookbook/tools/discord_tools.py
from agno.agent import Agent
from agno.tools.discord import DiscordTools

discord_tools = DiscordTools(
 bot_token=discord_token,
 enable_messaging=True,
 enable_history=True,
 enable_channel_management=True,
 enable_message_management=True,
)

discord_agent = Agent(
 name="Discord Agent",
 instructions=[
 "You are a Discord bot that can perform various operations.",
 "You can send messages, read message history, manage channels, and delete messages.",
 ],
 tools=[discord_tools],
 show_tool_calls=True,
 markdown=True,
)

channel_id = "YOUR_CHANNEL_ID"
server_id = "YOUR_SERVER_ID"

discord_agent.print_response(
 f"Send a message 'Hello from Agno!' to channel {channel_id}", stream=True
)

discord_agent.print_response(f"Get information about channel {channel_id}", stream=True)

discord_agent.print_response(f"List all channels in server {server_id}", stream=True)

discord_agent.print_response(
 f"Get the last 5 messages from channel {channel_id}", stream=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your Discord token">
 ```bash
 export DISCORD_BOT_TOKEN=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U discord.py openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/discord_tools.py
 ```

 ```bash Windows
 python cookbook/tools/discord_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Email Tools
Source: https://docs.agno.com/examples/concepts/tools/social/email

## Code

```python cookbook/tools/email_tools.py
from agno.agent import Agent
from agno.tools.email import EmailTools

receiver_email = "<receiver_email>"
sender_email = "<sender_email>"
sender_name = "<sender_name>"
sender_passkey = "<sender_passkey>"

agent = Agent(
 tools=[
 EmailTools(
 receiver_email=receiver_email,
 sender_email=sender_email,
 sender_name=sender_name,
 sender_passkey=sender_passkey,
 )
 ]
)
agent.print_response("Send an email to <receiver_email>.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set your email credentials">
 ```bash
 export SENDER_EMAIL=xxx
 export SENDER_PASSKEY=xxx
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
 python cookbook/tools/email_tools.py
 ```

 ```bash Windows
 python cookbook/tools/email_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Slack Tools
Source: https://docs.agno.com/examples/concepts/tools/social/slack

## Code

```python cookbook/tools/slack_tools.py
from agno.agent import Agent
from agno.tools.slack import SlackTools

agent = Agent(
 tools=[SlackTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Send a message to #general channel saying 'Hello from Agno!'")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set your Slack token">
 ```bash
 export SLACK_BOT_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U slack-sdk openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/slack_tools.py
 ```

 ```bash Windows
 python cookbook/tools/slack_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Twilio Tools
Source: https://docs.agno.com/examples/concepts/tools/social/twilio

## Code

```python cookbook/tools/twilio_tools.py
from agno.agent import Agent
from agno.tools.twilio import TwilioTools

agent = Agent(
 tools=[TwilioTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Send an SMS to +1234567890 saying 'Hello from Agno!'")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set your Twilio credentials">
 ```bash
 export TWILIO_ACCOUNT_SID=xxx
 export TWILIO_AUTH_TOKEN=xxx
 export TWILIO_FROM_NUMBER=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U twilio openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/twilio_tools.py
 ```

 ```bash Windows
 python cookbook/tools/twilio_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Webex Tools
Source: https://docs.agno.com/examples/concepts/tools/social/webex

## Code

```python cookbook/tools/webex_tools.py
from agno.agent import Agent
from agno.tools.webex import WebexTools

agent = Agent(
 name="Webex Assistant",
 tools=[WebexTools()],
 description="You are a Webex assistant that can send messages and manage spaces.",
 instructions=[
 "You can help users by:",
 "- Listing available Webex spaces",
 "- Sending messages to spaces",
 "Always confirm the space exists before sending messages.",
 ],
 show_tool_calls=True,
 markdown=True,
)

# List all spaces in Webex
agent.print_response("List all spaces on our Webex", markdown=True)

# Send a message to a Space in Webex
agent.print_response(
 "Send a funny ice-breaking message to the webex Welcome space", markdown=True
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set up Webex Bot">
 1. Go to [Webex Developer Portal](https://developer.webex.com/)
 2. Create a Bot:
 * Navigate to My Webex Apps → Create a Bot
 * Fill in the bot details and click Add Bot
 3. Get your access token:
 * Copy the token shown after bot creation
 * Or regenerate via My Webex Apps → Edit Bot
 </Step>

 <Step title="Set your API keys">
 ```bash
 export WEBEX_ACCESS_TOKEN=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U webexpythonsdk openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/webex_tools.py
 ```

 ```bash Windows
 python cookbook/tools/webex_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# WhatsApp Tools
Source: https://docs.agno.com/examples/concepts/tools/social/whatsapp

## Code

```python cookbook/tools/whatsapp_tools.py
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.whatsapp import WhatsAppTools

agent = Agent(
 name="whatsapp",
 model=Gemini(id="gemini-2.0-flash"),
 tools=[WhatsAppTools()],
)

# Example: Send a template message
# Note: Replace '''hello_world''' with your actual template name
agent.print_response(
 "Send a template message using the '''hello_world''' template in English to +91 1234567890"
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set up WhatsApp Business API">
 1. Go to [Meta for Developers](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started)
 2. Create a Meta App and set up the WhatsApp Business API.
 3. Obtain your Phone Number ID and a permanent System User Access Token.
 </Step>

 <Step title="Set your API keys and identifiers">
 ```bash
 export WHATSAPP_ACCESS_TOKEN=xxx
 export WHATSAPP_PHONE_NUMBER_ID=xxx
 export OPENAI_API_KEY=xxx # Or your preferred LLM API key
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno openai google-generativeai # Add any other necessary WhatsApp SDKs
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/whatsapp_tools.py
 ```

 ```bash Windows
 python cookbook/tools/whatsapp_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# X (Twitter) Tools
Source: https://docs.agno.com/examples/concepts/tools/social/x

## Code

```python cookbook/tools/x_tools.py
from agno.agent import Agent
from agno.tools.x import XTools

agent = Agent(
 tools=[XTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Make a post saying 'Hello World from Agno!'")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Set your X credentials">
 ```bash
 export X_CONSUMER_KEY=xxx
 export X_CONSUMER_SECRET=xxx
 export X_ACCESS_TOKEN=xxx
 export X_ACCESS_TOKEN_SECRET=xxx
 export X_BEARER_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U tweepy openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/x_tools.py
 ```

 ```bash Windows
 python cookbook/tools/x_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Firecrawl Tools
Source: https://docs.agno.com/examples/concepts/tools/web_scrape/firecrawl

Use Firecrawl with Agno to scrape and crawl the web.

## Code

```python cookbook/tools/firecrawl_tools.py
from agno.agent import Agent
from agno.tools.firecrawl import FirecrawlTools

agent = Agent(
 tools=[FirecrawlTools(scrape=False, crawl=True)],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Summarize this https://finance.yahoo.com/")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export FIRECRAWL_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U firecrawl openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/firecrawl_tools.py
 ```

 ```bash Windows
 python cookbook/tools/firecrawl_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Jina Reader Tools
Source: https://docs.agno.com/examples/concepts/tools/web_scrape/jina_reader

## Code

```python cookbook/tools/jina_reader_tools.py
from agno.agent import Agent
from agno.tools.jina_reader import JinaReaderTools

agent = Agent(
 tools=[JinaReaderTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Read and summarize this PDF: https://example.com/sample.pdf")
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
 pip install -U jina-reader openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/jina_reader_tools.py
 ```

 ```bash Windows
 python cookbook/tools/jina_reader_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Newspaper Tools
Source: https://docs.agno.com/examples/concepts/tools/web_scrape/newspaper

## Code

```python cookbook/tools/newspaper_tools.py
from agno.agent import Agent
from agno.tools.newspaper import NewspaperTools

agent = Agent(
 tools=[NewspaperTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Extract the main article content from https://example.com/article")
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
 pip install -U newspaper3k openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/newspaper_tools.py
 ```

 ```bash Windows
 python cookbook/tools/newspaper_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Newspaper4k Tools
Source: https://docs.agno.com/examples/concepts/tools/web_scrape/newspaper4k

## Code

```python cookbook/tools/newspaper4k_tools.py
from agno.agent import Agent
from agno.tools.newspaper4k import Newspaper4kTools

agent = Agent(
 tools=[Newspaper4kTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Analyze and summarize this news article: https://example.com/news")
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
 pip install -U newspaper4k openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/newspaper4k_tools.py
 ```

 ```bash Windows
 python cookbook/tools/newspaper4k_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Spider Tools
Source: https://docs.agno.com/examples/concepts/tools/web_scrape/spider

## Code

```python cookbook/tools/spider_tools.py
from agno.agent import Agent
from agno.tools.spider import SpiderTools

agent = Agent(
 tools=[SpiderTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Crawl https://example.com and extract all links")
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
 pip install -U scrapy openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/spider_tools.py
 ```

 ```bash Windows
 python cookbook/tools/spider_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Website Tools
Source: https://docs.agno.com/examples/concepts/tools/web_scrape/website

## Code

```python cookbook/tools/website_tools.py
from agno.agent import Agent
from agno.tools.website import WebsiteTools

agent = Agent(
 tools=[WebsiteTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Extract the main content from https://example.com")
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
 pip install -U beautifulsoup4 requests openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/tools/website_tools.py
 ```

 ```bash Windows
 python cookbook/tools/website_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# User Confirmation Required
Source: https://docs.agno.com/examples/concepts/user-control-flows/01-confirmation-required

This example demonstrates how to implement human-in-the-loop functionality by requiring user confirmation before executing tool calls.

## Code

```python cookbook/agent_concepts/user_control_flows/confirmation_required.py
import json

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint
from rich.console import Console
from rich.prompt import Prompt

console = Console()

@tool(requires_confirmation=True)
def get_top_hackernews_stories(num_stories: int) -> str:
 """Fetch top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to retrieve

 Returns:
 str: JSON string containing story details
 """
 # Fetch top story IDs
 response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
 story_ids = response.json()

 # Yield story details
 all_stories = []
 for story_id in story_ids[:num_stories]:
 story_response = httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
 )
 story = story_response.json()
 if "text" in story:
 story.pop("text", None)
 all_stories.append(story)
 return json.dumps(all_stories)

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[get_top_hackernews_stories],
 markdown=True,
)

agent.run("Fetch the top 2 hackernews stories.")
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_confirmation:
 # Ask for confirmation
 console.print(
 f"Tool name [bold blue]{tool.tool_name}({tool.tool_args})[/] requires confirmation."
 )
 message = (
 Prompt.ask("Do you want to continue?", choices=["y", "n"], default="y")
 .strip()
 .lower()
 )

 if message == "n":
 tool.confirmed = False
 else:
 tool.confirmed = True

run_response = agent.continue_run()
pprint.pprint_run_response(run_response)
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
 pip install -U agno httpx rich openai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/user_control_flows/confirmation_required.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/confirmation_required.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `@tool(requires_confirmation=True)` to mark tools that need user confirmation
* Demonstrates how to continue agent execution after user input

## Use Cases

* Confirming sensitive operations before execution

# Async User Confirmation
Source: https://docs.agno.com/examples/concepts/user-control-flows/02-confirmation-required-async

This example demonstrates how to implement asynchronous user confirmation flows, allowing for non-blocking execution while waiting for user input.

## Code

```python cookbook/agent_concepts/user_control_flows/confirmation_required_async.py
import asyncio
import json

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint
from rich.console import Console
from rich.prompt import Prompt

console = Console()

@tool(requires_confirmation=True)
async def get_top_hackernews_stories(num_stories: int) -> str:
 """Fetch top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to retrieve

 Returns:
 str: JSON string containing story details
 """
 # Fetch top story IDs
 response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
 story_ids = response.json()

 # Yield story details
 all_stories = []
 for story_id in story_ids[:num_stories]:
 story_response = httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
 )
 story = story_response.json()
 if "text" in story:
 story.pop("text", None)
 all_stories.append(story)
 return json.dumps(all_stories)

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[get_top_hackernews_stories],
 markdown=True,
)

run_response = asyncio.run(agent.arun("Fetch the top 2 hackernews stories"))
if run_response.is_paused:
 for tool in run_response.tools_requiring_confirmation:
 # Ask for confirmation
 console.print(
 f"Tool name [bold blue]{tool.tool_name}({tool.tool_args})[/] requires confirmation."
 )
 message = (
 Prompt.ask("Do you want to continue?", choices=["y", "n"], default="y")
 .strip()
 .lower()
 )

 if message == "n":
 tool.confirmed = False
 else:
 tool.confirmed = True

run_response = asyncio.run(agent.acontinue_run(run_response=run_response))
pprint.pprint_run_response(run_response)
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
 pip install -U agno httpx rich openai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/user_control_flows/confirmation_required_async.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/confirmation_required_async.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `agent.arun()` for asynchronous agent execution
* Implements `agent.acontinue_run()` for async continuation
* Maintains the same confirmation flow as synchronous version
* Demonstrates how to handle async execution with user input

## Use Cases

* Non-blocking user confirmation flows
* High-performance applications requiring async execution
* Web applications with user interaction
* Long-running operations with user input

# Streaming User Confirmation
Source: https://docs.agno.com/examples/concepts/user-control-flows/03-confirmation-required-stream

This example demonstrates how to implement streaming user confirmation flows, allowing for real-time interaction and response streaming.

## Code

```python cookbook/agent_concepts/user_control_flows/confirmation_required_stream.py
import json

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint
from rich.console import Console
from rich.prompt import Prompt

console = Console()

@tool(requires_confirmation=True)
def get_top_hackernews_stories(num_stories: int) -> str:
 """Fetch top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to retrieve

 Returns:
 str: JSON string containing story details
 """
 # Fetch top story IDs
 response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
 story_ids = response.json()

 # Yield story details
 all_stories = []
 for story_id in story_ids[:num_stories]:
 story_response = httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
 )
 story = story_response.json()
 if "text" in story:
 story.pop("text", None)
 all_stories.append(story)
 return json.dumps(all_stories)

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[get_top_hackernews_stories],
 markdown=True,
)

for run_response in agent.run("Fetch the top 2 hackernews stories", stream=True):
 if run_response.is_paused:
 for tool in run_response.tools_requiring_confirmation:
 # Ask for confirmation
 console.print(
 f"Tool name [bold blue]{tool.tool_name}({tool.tool_args})[/] requires confirmation."
 )
 message = (
 Prompt.ask("Do you want to continue?", choices=["y", "n"], default="y")
 .strip()
 .lower()
 )

 if message == "n":
 tool.confirmed = False
 else:
 tool.confirmed = True
 run_response = agent.continue_run(run_response=run_response, stream=True)
 pprint.pprint_run_response(run_response)
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
 pip install -U agno httpx rich openai
 ```
 </Step>

 <Step title="Run Example">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/user_control_flows/confirmation_required_stream.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/confirmation_required_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `agent.run(stream=True)` for streaming responses
* Implements streaming continuation with `agent.continue_run(stream=True)`
* Maintains real-time interaction with user confirmation
* Demonstrates how to handle streaming responses with user input

## Use Cases

* Real-time user interaction
* Streaming applications requiring user input
* Interactive chat interfaces
* Progressive response generation

# User Input Required
Source: https://docs.agno.com/examples/concepts/user-control-flows/04-user-input-required

This example demonstrates how to implement user input collection during agent execution, allowing users to provide specific information for tool parameters.

## Code

```python cookbook/agent_concepts/user_control_flows/user_input_required.py
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.tools.function import UserInputField
from agno.utils import pprint

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
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[send_email],
 markdown=True,
)

agent.run("Send an email with the subject 'Hello' and the body 'Hello, world!'")
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name}")
 print(f"Description: {field.description}")
 print(f"Type: {field.field_type}")

 # Get user input
 if field.value is None:
 user_value = input(f"Please enter a value for {field.name}: ")
 # Update the field value
 field.value = user_value
 else:
 print(f"Value: {field.value}")

 run_response = agent.continue_run()
 pprint.pprint_run_response(run_response)
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
 python cookbook/agent_concepts/user_control_flows/user_input_required.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/user_input_required.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `@tool(requires_user_input=True)` to mark tools that need user input
* Can specify which fields require user input using `user_input_fields`
* Implements a dynamic form-like interface for collecting user input
* Handles both user-provided and agent-provided values

## Use Cases

* Collecting required parameters for operations

# Async User Input
Source: https://docs.agno.com/examples/concepts/user-control-flows/05-user-input-required-async

This example demonstrates how to implement asynchronous user input collection, allowing for non-blocking execution while gathering user information.

## Code

```python cookbook/agent_concepts/user_control_flows/user_input_required_async.py
import asyncio
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.tools.function import UserInputField
from agno.utils import pprint

@tool(requires_user_input=True, user_input_fields=["to_address"])
async def send_email(subject: str, body: str, to_address: str) -> str:
 """
 Send an email.

 Args:
 subject (str): The subject of the email.
 body (str): The body of the email.
 to_address (str): The address to send the email to.
 """
 return f"Sent email to {to_address} with subject {subject} and body {body}"

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[send_email],
 markdown=True,
)

asyncio.run(
 agent.arun("Send an email with the subject 'Hello' and the body 'Hello, world!'")
)
if agent.is_paused:
 for tool in agent.run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name}")
 print(f"Description: {field.description}")
 print(f"Type: {field.field_type}")

 # Get user input
 if field.value is None:
 user_value = input(f"Please enter a value for {field.name}: ")
 # Update the field value
 field.value = user_value
 else:
 print(f"Value: {field.value}")

 run_response = asyncio.run(agent.acontinue_run())
 pprint.pprint_run_response(run_response)
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
 python cookbook/agent_concepts/user_control_flows/user_input_required_async.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/user_input_required_async.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `agent.arun()` for asynchronous agent execution
* Implements `agent.acontinue_run()` for async continuation
* Maintains the same user input flow as synchronous version
* Demonstrates how to handle async execution with user input collection

## Use Cases

* Non-blocking user input collection
* High-performance applications requiring async execution
* Web applications with form-like interactions
* Long-running operations with user input

# Streaming User Input
Source: https://docs.agno.com/examples/concepts/user-control-flows/06-user-input-required-stream

This example demonstrates how to implement streaming user input collection, allowing for real-time interaction and response streaming while gathering user information.

## Code

```python cookbook/agent_concepts/user_control_flows/user_input_required_stream.py
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.tools.function import UserInputField
from agno.utils import pprint

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
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[send_email],
 markdown=True,
)

for run_response in agent.run(
 "Send an email with the subject 'Hello' and the body 'Hello, world!'", stream=True
):
 if run_response.is_paused:
 for tool in run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name}")
 print(f"Description: {field.description}")
 print(f"Type: {field.field_type}")

 # Get user input
 if field.value is None:
 user_value = input(f"Please enter a value for {field.name}: ")
 # Update the field value
 field.value = user_value
 else:
 print(f"Value: {field.value}")

 run_response = agent.continue_run(stream=True)
 pprint.pprint_run_response(run_response)
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
 python cookbook/agent_concepts/user_control_flows/user_input_required_stream.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/user_input_required_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `agent.run(stream=True)` for streaming responses
* Implements streaming continuation with `agent.continue_run(stream=True)`
* Maintains real-time interaction with user input collection
* Demonstrates how to handle streaming responses with user input

## Use Cases

* Real-time user interaction
* Streaming applications requiring user input
* Interactive form-like interfaces
* Progressive response generation with user input

# Dynamic User Input (Agentic)
Source: https://docs.agno.com/examples/concepts/user-control-flows/07-agentic-user-input

This example demonstrates how to implement dynamic user input collection using the `UserControlFlowTools`, allowing the agent to request information as needed during execution.

## Code

```python cookbook/agent_concepts/user_control_flows/agentic_user_input.py
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.function import UserInputField
from agno.tools.toolkit import Toolkit
from agno.tools.user_control_flow import UserControlFlowTools
from agno.utils import pprint

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
 date_from (str): The start date (in YYYY-MM-DD format).
 date_to (str): The end date (in YYYY-MM-DD format).
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

run_response = agent.run("Send an email with the body 'What is the weather in Tokyo?'")
# We use a while loop to continue the running until the agent is satisfied with the user input
while run_response.is_paused:
 for tool in run_response.tools_requiring_user_input:
 input_schema: List[UserInputField] = tool.user_input_schema

 for field in input_schema:
 # Display field information to the user
 print(f"\nField: {field.name}")
 print(f"Description: {field.description}")
 print(f"Type: {field.field_type}")

 # Get user input
 if field.value is None:
 user_value = input(f"Please enter a value for {field.name}: ")
 else:
 print(f"Value: {field.value}")
 user_value = field.value

 # Update the field value
 field.value = user_value

 run_response = agent.continue_run(run_response=run_response)
 if not run_response.is_paused:
 pprint.pprint_run_response(run_response)
 break
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
 python cookbook/agent_concepts/user_control_flows/agentic_user_input.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/agentic_user_input.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `UserControlFlowTools` for dynamic user input collection
* Implements a toolkit with multiple tools that may require user input
* Handles multiple rounds of user input collection
* Demonstrates how to continue agent execution after each input round

## Use Cases

* Dynamic form-like interactions

# External Tool Execution
Source: https://docs.agno.com/examples/concepts/user-control-flows/08-external-tool-execution

This example demonstrates how to execute tool calls outside of the agent's control, allowing for custom execution logic and security measures.

## Code

```python cookbook/agent_concepts/user_control_flows/external_tool_execution.py
import subprocess

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint

@tool(external_execution=True)
def execute_shell_command(command: str) -> str:
 """Execute a shell command.

 Args:
 command (str): The shell command to execute

 Returns:
 str: The output of the shell command
 """
 if command.startswith("ls"):
 return subprocess.check_output(command, shell=True).decode("utf-8")
 else:
 raise Exception(f"Unsupported command: {command}")

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
 # We execute the tool ourselves. You can also execute something completely external here.
 result = execute_shell_command.entrypoint(**tool.tool_args)
 # We have to set the result on the tool execution object so that the agent can continue
 tool.result = result

 run_response = agent.continue_run()
 pprint.pprint_run_response(run_response)
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
 python cookbook/agent_concepts/user_control_flows/external_tool_execution.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/external_tool_execution.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `@tool(external_execution=True)` to mark tools that need external execution
* Demonstrates how to handle tool execution results

## Use Cases

* Executing sensitive operations outside agent control
* Executing long-running operations outside agent control

# Async External Tool Execution
Source: https://docs.agno.com/examples/concepts/user-control-flows/09-external-tool-execution-async

This example demonstrates how to implement asynchronous external tool execution, allowing for non-blocking execution of tools outside of the agent's control.

## Code

```python cookbook/agent_concepts/user_control_flows/external_tool_execution_async.py
import asyncio
import subprocess

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint

@tool(external_execution=True)
def execute_shell_command(command: str) -> str:
 """Execute a shell command.

 Args:
 command (str): The shell command to execute

 Returns:
 str: The output of the shell command
 """
 if command.startswith("ls"):
 return subprocess.check_output(command, shell=True).decode("utf-8")
 else:
 raise Exception(f"Unsupported command: {command}")

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[execute_shell_command],
 markdown=True,
)

run_response = asyncio.run(agent.arun("What files do I have in my current directory?"))
if run_response.is_paused:
 for tool in run_response.tools_awaiting_external_execution:
 if tool.tool_name == execute_shell_command.name:
 print(f"Executing {tool.tool_name} with args {tool.tool_args} externally")
 # We execute the tool ourselves. You can also execute something completely external here.
 result = execute_shell_command.entrypoint(**tool.tool_args)
 # We have to set the result on the tool execution object so that the agent can continue
 tool.result = result

 run_response = asyncio.run(agent.acontinue_run(run_response=run_response))
 pprint.pprint_run_response(run_response)
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
 python cookbook/agent_concepts/user_control_flows/external_tool_execution_async.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/external_tool_execution_async.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `agent.arun()` for asynchronous agent execution
* Implements `agent.acontinue_run()` for async continuation
* Maintains the same external tool execution flow as synchronous version
* Demonstrates how to handle async execution with external tools

## Use Cases

* Non-blocking external tool execution
* High-performance applications requiring async execution
* Web applications with external service calls
* Long-running operations with external tools

# Streaming External Tool Execution
Source: https://docs.agno.com/examples/concepts/user-control-flows/10-external-tool-execution-stream

This example demonstrates how to implement streaming external tool execution, allowing for real-time interaction and response streaming while executing tools outside of the agent's control.

## Code

```python cookbook/agent_concepts/user_control_flows/external_tool_execution_stream.py
import subprocess

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool
from agno.utils import pprint

@tool(external_execution=True)
def execute_shell_command(command: str) -> str:
 """Execute a shell command.

 Args:
 command (str): The shell command to execute

 Returns:
 str: The output of the shell command
 """
 if command.startswith("ls"):
 return subprocess.check_output(command, shell=True).decode("utf-8")
 else:
 raise Exception(f"Unsupported command: {command}")

agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[execute_shell_command],
 markdown=True,
)

for run_response in agent.run(
 "What files do I have in my current directory?", stream=True
):
 if run_response.is_paused:
 for tool in run_response.tools_awaiting_external_execution:
 if tool.tool_name == execute_shell_command.name:
 print(f"Executing {tool.tool_name} with args {tool.tool_args} externally")
 # We execute the tool ourselves. You can also execute something completely external here.
 result = execute_shell_command.entrypoint(**tool.tool_args)
 # We have to set the result on the tool execution object so that the agent can continue
 tool.result = result

 run_response = agent.continue_run(run_response=run_response, stream=True)
 pprint.pprint_run_response(run_response)
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
 python cookbook/agent_concepts/user_control_flows/external_tool_execution_stream.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/user_control_flows/external_tool_execution_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

## Key Features

* Uses `agent.run(stream=True)` for streaming responses
* Implements streaming continuation with `agent.continue_run(stream=True)`
* Maintains real-time interaction with external tool execution
* Demonstrates how to handle streaming responses with external tools

## Use Cases

* Real-time external tool execution
* Streaming applications with external service calls
* Interactive interfaces with external tool execution
* Progressive response generation with external tools

# Azure Cosmos DB MongoDB vCore Integration
Source: https://docs.agno.com/examples/concepts/vectordb/azure_cosmos_mongodb

## Code

```python cookbook/agent_concepts/knowledge/vector_dbs/mongo_db/cosmos_mongodb_vcore.py
import urllib.parse
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.mongodb import MongoDb

# Azure Cosmos DB MongoDB connection string
"""
Example connection strings:
"mongodb+srv://<username>:<encoded_password>@cluster0.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
"""
mdb_connection_string = f"mongodb+srv://<username>:<encoded_password>@cluster0.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=MongoDb(
 collection_name="recipes",
 db_url=mdb_connection_string,
 search_index_name="recipes",
 cosmos_compatibility=True,
 ),
)

# Comment out after first run
knowledge_base.load(recreate=True)

# Create and use the agent
agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U pymongo pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/knowledge/vector_dbs/mongo_db/cosmos_mongodb_vcore.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/knowledge/vector_dbs/mongo_db/cosmos_mongodb_vcore.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Cassandra Integration
Source: https://docs.agno.com/examples/concepts/vectordb/cassandra

## Code

```python cookbook/agent_concepts/vector_dbs/cassandra_db.py
from agno.agent import Agent
from agno.embedder.mistral import MistralEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.mistral import MistralChat
from agno.vectordb.cassandra import Cassandra

try:
 from cassandra.cluster import Cluster
except (ImportError, ModuleNotFoundError):
 raise ImportError(
 "Could not import cassandra-driver python package.Please install it with pip install cassandra-driver."
 )

cluster = Cluster()

session = cluster.connect()
session.execute(
 """
 CREATE KEYSPACE IF NOT EXISTS testkeyspace
 WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 }
 """
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=Cassandra(
 table_name="recipes",
 keyspace="testkeyspace",
 session=session,
 embedder=MistralEmbedder(),
 ),
)

knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=MistralChat(),
 knowledge=knowledge_base,
 show_tool_calls=True,
)

agent.print_response(
 "What are the health benefits of Khao Niew Dam Piek Maphrao Awn?",
 markdown=True,
 show_full_reasoning=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U cassandra-driver pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/cassandra_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/cassandra_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# ChromaDB Integration
Source: https://docs.agno.com/examples/concepts/vectordb/chromadb

## Code

```python cookbook/agent_concepts/vector_dbs/chroma_db.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.chroma import ChromaDb

# Initialize ChromaDB
vector_db = ChromaDb(collection="recipes", path="tmp/chromadb", persistent_client=True)

# Create knowledge base
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

knowledge_base.load(recreate=False) # Comment out after first run

# Create and use the agent
agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("Show me how to make Tom Kha Gai", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U chromadb pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/chroma_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/chroma_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Clickhouse Integration
Source: https://docs.agno.com/examples/concepts/vectordb/clickhouse

## Code

```python cookbook/agent_concepts/vector_dbs/clickhouse.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.clickhouse import Clickhouse

agent = Agent(
 storage=SqliteStorage(table_name="recipe_agent"),
 knowledge=PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=Clickhouse(
 table_name="recipe_documents",
 host="localhost",
 port=8123,
 username="ai",
 password="ai",
 ),
 ),
 show_tool_calls=True,
 search_knowledge=True,
 read_chat_history=True,
)
agent.knowledge.load(recreate=False) # type: ignore

agent.print_response("How do I make pad thai?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Start Clickhouse">
 ```bash
 docker run -d \
 -e CLICKHOUSE_DB=ai \
 -e CLICKHOUSE_USER=ai \
 -e CLICKHOUSE_PASSWORD=ai \
 -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 \
 -v clickhouse_data:/var/lib/clickhouse/ \
 -v clickhouse_log:/var/log/clickhouse-server/ \
 -p 8123:8123 \
 -p 9000:9000 \
 --ulimit nofile=262144:262144 \
 --name clickhouse-server \
 clickhouse/clickhouse-server
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U clickhouse-connect pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/clickhouse.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/clickhouse.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Couchbase Integration
Source: https://docs.agno.com/examples/concepts/vectordb/couchbase

## Code

```python cookbook/agent_concepts/vector_dbs/couchbase.py
import os
import time
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.couchbase import Couchbase
from couchbase.options import ClusterOptions, KnownConfigProfiles
from couchbase.auth import PasswordAuthenticator

# Couchbase connection settings
username = os.getenv("COUCHBASE_USER", "Administrator")
password = os.getenv("COUCHBASE_PASSWORD", "password")
connection_string = os.getenv("COUCHBASE_CONNECTION_STRING", "couchbase://localhost")

# Create cluster options with authentication
auth = PasswordAuthenticator(username, password)
cluster_options = ClusterOptions(auth)
cluster_options.apply_profile(KnownConfigProfiles.WanDevelopment)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=CouchbaseSearch(
 bucket_name="recipe_bucket",
 scope_name="recipe_scope",
 collection_name="recipes",
 couchbase_connection_string=connection_string,
 cluster_options=cluster_options,
 search_index="vector_search_fts_index",
 embedder=OpenAIEmbedder(
 id="text-embedding-3-large", 
 dimensions=3072, 
 api_key=os.getenv("OPENAI_API_KEY")
 ),
 wait_until_index_ready=60,
 overwrite=True
 ),
)

knowledge_base.load(recreate=True)

# Wait for the vector index to sync with KV
time.sleep(20)

agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Start Couchbase">
 ```bash
 docker run -d --name couchbase-server \
 -p 8091-8096:8091-8096 \
 -p 11210:11210 \
 -e COUCHBASE_ADMINISTRATOR_USERNAME=Administrator \
 -e COUCHBASE_ADMINISTRATOR_PASSWORD=password \
 couchbase:latest
 ```

 Then access [http://localhost:8091](http://localhost:8091) and create:

 * Bucket: `recipe_bucket`
 * Scope: `recipe_scope`
 * Collection: `recipes`
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U couchbase openai agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export COUCHBASE_USER="Administrator"
 export COUCHBASE_PASSWORD="password"
 export COUCHBASE_CONNECTION_STRING="couchbase://localhost"
 export OPENAI_API_KEY="your-openai-api-key"
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/couchbase.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/couchbase.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# LanceDB Integration
Source: https://docs.agno.com/examples/concepts/vectordb/lancedb

## Code

```python cookbook/agent_concepts/vector_dbs/lance_db.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb

vector_db = LanceDb(
 table_name="recipes",
 uri="/tmp/lancedb", # You can change this path to store data elsewhere
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("How to make Tom Kha Gai", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U lancedb pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/lance_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/lance_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Milvus Integration
Source: https://docs.agno.com/examples/concepts/vectordb/milvus

## Code

```python cookbook/agent_concepts/vector_dbs/milvus.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.milvus import Milvus

COLLECTION_NAME = "thai-recipes"

vector_db = Milvus(collection=COLLECTION_NAME, url="http://localhost:6333")

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("List down the ingredients to make Massaman Gai", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U pymilvus pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/milvus.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/milvus.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# MongoDB Integration
Source: https://docs.agno.com/examples/concepts/vectordb/mongodb

## Code

```python cookbook/agent_concepts/vector_dbs/mongodb.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.mongodb import MongoDb

mdb_connection_string = "mongodb://ai:ai@localhost:27017/ai?authSource=admin"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=MongoDb(
 collection_name="recipes",
 db_url=mdb_connection_string,
 wait_until_index_ready=60,
 wait_after_insert=300,
 ),
)
knowledge_base.load(recreate=True)

agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U pymongo pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/mongodb.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/mongodb.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PgVector Integration
Source: https://docs.agno.com/examples/concepts/vectordb/pgvector

## Code

```python cookbook/agent_concepts/vector_dbs/pg_vector.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

vector_db = PgVector(table_name="recipes", db_url=db_url)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Start PgVector">
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

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy pgvector psycopg pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/pg_vector.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/pg_vector.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Pinecone Integration
Source: https://docs.agno.com/examples/concepts/vectordb/pinecone

## Code

```python cookbook/agent_concepts/vector_dbs/pinecone_db.py
from os import getenv

from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.pineconedb import PineconeDb

api_key = getenv("PINECONE_API_KEY")
index_name = "thai-recipe-index"

vector_db = PineconeDb(
 name=index_name,
 dimension=1536,
 metric="cosine",
 spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
 api_key=api_key,
)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

knowledge_base.load(recreate=False, upsert=True)

agent = Agent(
 knowledge=knowledge_base,
 show_tool_calls=True,
 search_knowledge=True,
 read_chat_history=True,
)

agent.print_response("How do I make pad thai?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export PINECONE_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U pinecone-client pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/pinecone_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/pinecone_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Qdrant Integration
Source: https://docs.agno.com/examples/concepts/vectordb/qdrant

## Code

```python cookbook/agent_concepts/vector_dbs/qdrant_db.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.qdrant import Qdrant

COLLECTION_NAME = "thai-recipes"

vector_db = Qdrant(collection=COLLECTION_NAME, url="http://localhost:6333")

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)

knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(knowledge=knowledge_base, show_tool_calls=True)
agent.print_response("List down the ingredients to make Massaman Gai", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Start Qdrant">
 ```bash
 docker run -p 6333:6333 -p 6334:6334 \
 -v $(pwd)/qdrant_storage:/qdrant/storage:z \
 qdrant/qdrant
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U qdrant-client pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/qdrant_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/qdrant_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# SingleStore Integration
Source: https://docs.agno.com/examples/concepts/vectordb/singlestore

## Code

```python cookbook/agent_concepts/vector_dbs/singlestore.py
from os import getenv

from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.singlestore import SingleStore
from sqlalchemy.engine import create_engine

USERNAME = getenv("SINGLESTORE_USERNAME")
PASSWORD = getenv("SINGLESTORE_PASSWORD")
HOST = getenv("SINGLESTORE_HOST")
PORT = getenv("SINGLESTORE_PORT")
DATABASE = getenv("SINGLESTORE_DATABASE")
SSL_CERT = getenv("SINGLESTORE_SSL_CERT", None)

db_url = (
 f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}?charset=utf8mb4"
)
if SSL_CERT:
 db_url += f"&ssl_ca={SSL_CERT}&ssl_verify_cert=true"

db_engine = create_engine(db_url)

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=SingleStore(
 collection="recipes",
 db_engine=db_engine,
 schema=DATABASE,
 ),
)

knowledge_base.load(recreate=False)

agent = Agent(
 knowledge=knowledge_base,
 show_tool_calls=True,
 search_knowledge=True,
 read_chat_history=True,
)

agent.print_response("How do I make pad thai?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set environment variables">
 ```bash
 export SINGLESTORE_HOST="localhost"
 export SINGLESTORE_PORT="3306"
 export SINGLESTORE_USERNAME="root"
 export SINGLESTORE_PASSWORD="admin"
 export SINGLESTORE_DATABASE="AGNO"
 export SINGLESTORE_SSL_CA=".certs/singlestore_bundle.pem"
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy pymysql pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/singlestore.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/singlestore.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Weaviate Integration
Source: https://docs.agno.com/examples/concepts/vectordb/weaviate

## Code

```python cookbook/agent_concepts/vector_dbs/weaviate_db.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.search import SearchType
from agno.vectordb.weaviate import Distance, VectorIndex, Weaviate

vector_db = Weaviate(
 collection="recipes",
 search_type=SearchType.hybrid,
 vector_index=VectorIndex.HNSW,
 distance=Distance.COSINE,
 local=True, # Set to False if using Weaviate Cloud and True if using local instance
)
# Create knowledge base
knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=vector_db,
)
knowledge_base.load(recreate=False) # Comment out after first run

# Create and use the agent
agent = Agent(
 knowledge=knowledge_base,
 search_knowledge=True,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install -U weaviate-client pypdf openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/agent_concepts/vector_dbs/weaviate_db.py
 ```

 ```bash Windows
 python cookbook/agent_concepts/vector_dbs/weaviate_db.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Accuracy with Given Answer
Source: https://docs.agno.com/examples/evals/accuracy/accuracy_with_given_answer

Learn how to evaluate the accuracy of an Agno Agent's response with a given answer.

For this example an agent won't be executed, but the given result will be evaluated against the expected output for correctness.

## Code

```python
from typing import Optional

from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat

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

# Accuracy with Teams
Source: https://docs.agno.com/examples/evals/accuracy/accuracy_with_teams

Learn how to evaluate the accuracy of an Agno Team.

## Code

```python
from typing import Optional

from agno.agent import Agent
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat
from agno.team.team import Team

# Setup a team with two members
english_agent = Agent(
 name="English Agent",
 role="You only answer in English",
 model=OpenAIChat(id="gpt-4o"),
)
spanish_agent = Agent(
 name="Spanish Agent",
 role="You can only answer in Spanish",
 model=OpenAIChat(id="gpt-4o"),
)

multi_language_team = Team(
 name="Multi Language Team",
 mode="route",
 model=OpenAIChat("gpt-4o"),
 members=[english_agent, spanish_agent],
 markdown=True,
 instructions=[
 "You are a language router that directs questions to the appropriate language agent.",
 "If the user asks in a language whose agent is not a team member, respond in English with:",
 "'I can only answer in the following languages: English and Spanish.",
 "Always check the language of the user's input before routing to an agent.",
 ],
)

# Evaluate the accuracy of the Team's responses
evaluation = AccuracyEval(
 model=OpenAIChat(id="o4-mini"),
 team=multi_language_team,
 input="Comment allez-vous?",
 expected_output="I can only answer in the following languages: English and Spanish.",
 num_iterations=1,
)

result: Optional[AccuracyResult] = evaluation.run(print_results=True)
assert result is not None and result.avg_score >= 8
```

# Accuracy with Tools
Source: https://docs.agno.com/examples/evals/accuracy/accuracy_with_tools

Learn how to evaluate the accuracy of an Agent that is using tools.

This example shows an evaluation that runs the provided agent with the provided input and then evaluates the answer that the agent gives.

## Code

```python
from typing import Optional

from agno.agent import Agent
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools

evaluation = AccuracyEval(
 model=OpenAIChat(id="o4-mini"),
 agent=Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[CalculatorTools(factorial=True)],
 ),
 input="What is 10!?",
 expected_output="3628800",
)

result: Optional[AccuracyResult] = evaluation.run(print_results=True)
assert result is not None and result.avg_score >= 8
```

# Simple Accuracy
Source: https://docs.agno.com/examples/evals/accuracy/basic

Learn to check how complete, correct and accurate an Agno Agent's response is.

This example shows a more complex evaluation that compares the full output of the agent for correctness.

## Code

```python
from typing import Optional

from agno.agent import Agent
from agno.eval.accuracy import AccuracyEval, AccuracyResult
from agno.models.openai import OpenAIChat
from agno.tools.calculator import CalculatorTools

evaluation = AccuracyEval(
 model=OpenAIChat(id="o4-mini"),
 agent=Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[CalculatorTools(enable_all=True)],
 ),
 input="What is 10*5 then to the power of 2? do it step by step",
 expected_output="2500",
 additional_guidelines="Agent output should include the steps and the final answer.",
)

result: Optional[AccuracyResult] = evaluation.run(print_results=True)
assert result is not None and result.avg_score >= 8
```

# Performance on Agent Instantiation
Source: https://docs.agno.com/examples/evals/performance/performance_agent_instantiation

Evaluation to analyze the runtime and memory usage of an Agent.

## Code

```python
"""Run `pip install openai agno memory_profiler` to install dependencies."""

from agno.agent import Agent
from agno.eval.performance import PerformanceEval
from agno.models.openai import OpenAIChat

def simple_response():
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 system_message="Be concise, reply with one sentence.",
 )
 response = agent.run("What is the capital of France?")
 return response

simple_response_perf = PerformanceEval(
 func=simple_response, num_iterations=1, warmup_runs=0
)

if __name__ == "__main__":
 simple_response_perf.run(print_results=True, print_summary=True)
```

# Performance on Agent Instantiation with Tool
Source: https://docs.agno.com/examples/evals/performance/performance_instantiation_with_tool

Example showing how to analyze the runtime and memory usage of an Agent that is using tools.

## Code

```python
"""Run `pip install agno openai memory_profiler` to install dependencies."""

from typing import Literal

from agno.agent import Agent
from agno.eval.performance import PerformanceEval
from agno.models.openai import OpenAIChat

def get_weather(city: Literal["nyc", "sf"]):
 """Use this to get weather information."""
 if city == "nyc":
 return "It might be cloudy in nyc"
 elif city == "sf":
 return "It's always sunny in sf"
 else:
 raise AssertionError("Unknown city")

tools = [get_weather]

def instantiate_agent():
 return Agent(model=OpenAIChat(id="gpt-4o"), tools=tools)

instantiation_perf = PerformanceEval(func=instantiate_agent, num_iterations=1000)

if __name__ == "__main__":
 instantiation_perf.run(print_results=True, print_summary=True)
```

# Performance on Agent Response
Source: https://docs.agno.com/examples/evals/performance/performance_simple_response

Example showing how to analyze the runtime and memory usage of an Agent's run, given its response.

## Code

```python

"""Run `pip install openai agno memory_profiler` to install dependencies."""

from agno.agent import Agent
from agno.eval.performance import PerformanceEval
from agno.models.openai import OpenAIChat

def simple_response():
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 system_message="Be concise, reply with one sentence.",
 )
 response = agent.run("What is the capital of France?")
 return response

simple_response_perf = PerformanceEval(
 func=simple_response, num_iterations=1, warmup_runs=0
)

if __name__ == "__main__":
 simple_response_perf.run(print_results=True, print_summary=True)
```

# Performance with Teams
Source: https://docs.agno.com/examples/evals/performance/performance_team_instantiation

Learn how to analyze the runtime and memory usage of an Agno Team.

## Code

```python
"""Run `pip install agno openai` to install dependencies."""

from agno.agent import Agent
from agno.eval.performance import PerformanceEval
from agno.models.openai import OpenAIChat
from agno.team.team import Team

team_member = Agent(model=OpenAIChat(id="gpt-4o"))

def instantiate_team():
 return Team(members=[team_member])

instantiation_perf = PerformanceEval(func=instantiate_team, num_iterations=1000)

if __name__ == "__main__":
 instantiation_perf.run(print_results=True, print_summary=True)
```

# Performance on Agent with Storage
Source: https://docs.agno.com/examples/evals/performance/performance_with_storage

Example showing how to analyze the runtime and memory usage of an Agent that is using storage.

## Code

```python
"""Run `pip install openai agno` to install dependencies."""

from agno.agent import Agent
from agno.eval.performance import PerformanceEval
from agno.models.openai import OpenAIChat

def simple_response():
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 system_message="Be concise, reply with one sentence.",
 add_history_to_messages=True,
 )
 response_1 = agent.run("What is the capital of France?")
 print(response_1.content)
 response_2 = agent.run("How many people live there?")
 print(response_2.content)
 return response_2.content

simple_response_perf = PerformanceEval(
 func=simple_response, num_iterations=1, warmup_runs=0
)

if __name__ == "__main__":
 simple_response_perf.run(print_results=True, print_summary=True)
```

# Reliability with Single Tool
Source: https://docs.agno.com/examples/evals/reliability/basic

Evaluation to assert an Agent is making the expected tool calls.

## Code

```python
from typing import Optional

from agno.agent import Agent
from agno.eval.reliability import ReliabilityEval, ReliabilityResult
from agno.models.openai import OpenAIChat
from agno.run.response import RunResponse
from agno.tools.calculator import CalculatorTools

def multiply_and_exponentiate():
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[CalculatorTools(add=True, multiply=True, exponentiate=True)],
 )
 response: RunResponse = agent.run(
 "What is 10*5 then to the power of 2? do it step by step"
 )
 evaluation = ReliabilityEval(
 agent_response=response,
 expected_tool_calls=["multiply", "exponentiate"],
 )
 result: Optional[ReliabilityResult] = evaluation.run(print_results=True)
 result.assert_passed()

if __name__ == "__main__":
 multiply_and_exponentiate()
```

# Reliability with Multiple Tools
Source: https://docs.agno.com/examples/evals/reliability/reliability_with_multiple_tools

Learn how to assert an Agno Agent is making multiple expected tool calls.

## Code

```python
from typing import Optional

from agno.agent import Agent
from agno.eval.reliability import ReliabilityEval, ReliabilityResult
from agno.models.openai import OpenAIChat
from agno.run.response import RunResponse
from agno.tools.calculator import CalculatorTools

def multiply_and_exponentiate():
 agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[CalculatorTools(add=True, multiply=True, exponentiate=True)],
 )
 response: RunResponse = agent.run(
 "What is 10*5 then to the power of 2? do it step by step"
 )
 evaluation = ReliabilityEval(
 agent_response=response,
 expected_tool_calls=["multiply", "exponentiate"],
 )
 result: Optional[ReliabilityResult] = evaluation.run(print_results=True)
 result.assert_passed()

if __name__ == "__main__":
 multiply_and_exponentiate()
```

# Reliability with Teams
Source: https://docs.agno.com/examples/evals/reliability/reliability_with_teams

Learn how to assert an Agno Team is making the expected tool calls.

## Code

```python
from typing import Optional

from agno.agent import Agent
from agno.eval.reliability import ReliabilityEval, ReliabilityResult
from agno.models.openai import OpenAIChat
from agno.run.team import TeamRunResponse
from agno.team.team import Team
from agno.tools.yfinance import YFinanceTools

team_member = Agent(
 name="Stock Searcher",
 model=OpenAIChat("gpt-4o"),
 role="Searches the web for information on a stock.",
 tools=[YFinanceTools(stock_price=True)],
)

team = Team(
 name="Stock Research Team",
 model=OpenAIChat("gpt-4o"),
 members=[team_member],
 markdown=True,
 show_members_responses=True,
)

expected_tool_calls = [
 "transfer_task_to_member", # Tool call used to transfer a task to a Team member
 "get_current_stock_price", # Tool call used to get the current stock price of a stock
]

def evaluate_team_reliability():
 response: TeamRunResponse = team.run("What is the current stock price of NVDA?")
 evaluation = ReliabilityEval(
 team_response=response,
 expected_tool_calls=expected_tool_calls,
 )
 result: Optional[ReliabilityResult] = evaluation.run(print_results=True)
 result.assert_passed()

if __name__ == "__main__":
 evaluate_team_reliability()
```

# Agent Context
Source: https://docs.agno.com/examples/getting-started/agent-context

This example shows how to inject external dependencies into an agent. The context is evaluated when the agent is run, acting like dependency injection for Agents.

Example prompts to try:

* "Summarize the top stories on HackerNews"
* "What are the trending tech discussions right now?"
* "Analyze the current top stories and identify trends"
* "What's the most upvoted story today?"

## Code

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
 # add_context will automatically add the context to the user message
 # add_context=True,
 # Alternatively, you can manually add the context to the instructions
 instructions=dedent("""\
 You are an insightful tech trend observer! 📰

 Here are the top stories on HackerNews:
 {top_hackernews_stories}\
 """),
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
 pip install openai httpx agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_context.py
 ```
 </Step>
</Steps>

# Agent Session
Source: https://docs.agno.com/examples/getting-started/agent-session

This example shows how to create an agent with persistent memory stored in a SQLite database. We set the session\_id on the agent when resuming the conversation, this way the previous chat history is preserved.

Key features:

* Stores conversation history in a SQLite database
* Continues conversations across multiple sessions
* References previous context in responses

## Code

```python agent_session.py
import json
from typing import Optional

import typer
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print

console = Console()

def create_agent(user: str = "user"):
 session_id: Optional[str] = None

 # Ask if user wants to start new session or continue existing one
 new = typer.confirm("Do you want to start a new session?")

 # Get existing session if user doesn't want a new one
 agent_storage = SqliteStorage(
 table_name="agent_sessions", db_file="tmp/agents.db"
 )

 if not new:
 existing_sessions = agent_storage.get_all_session_ids(user)
 if len(existing_sessions) > 0:
 session_id = existing_sessions[0]

 agent = Agent(
 user_id=user,
 # Set the session_id on the agent to resume the conversation
 session_id=session_id,
 model=OpenAIChat(id="gpt-4o"),
 storage=agent_storage,
 # Add chat history to messages
 add_history_to_messages=True,
 num_history_responses=3,
 markdown=True,
 )

 if session_id is None:
 session_id = agent.session_id
 if session_id is not None:
 print(f"Started Session: {session_id}\n")
 else:
 print("Started Session\n")
 else:
 print(f"Continuing Session: {session_id}\n")

 return agent

def print_messages(agent):
 """Print the current chat history in a formatted panel"""
 console.print(
 Panel(
 JSON(
 json.dumps(
 [
 m.model_dump(include={"role", "content"})
 for m in agent.memory.messages
 ]
 ),
 indent=4,
 ),
 title=f"Chat History for session_id: {agent.session_id}",
 expand=True,
 )
 )

def main(user: str = "user"):
 agent = create_agent(user)

 print("Chat with an OpenAI agent!")
 exit_on = ["exit", "quit", "bye"]
 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in exit_on:
 break

 agent.print_response(message=message, stream=True, markdown=True)
 print_messages(agent)

if __name__ == "__main__":
 typer.run(main)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai sqlalchemy agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_session.py
 ```
 </Step>
</Steps>

# Agent State
Source: https://docs.agno.com/examples/getting-started/agent-state

This example shows how to create an agent that maintains state across interactions. It demonstrates a simple counter mechanism, but this pattern can be extended to more complex state management like maintaining conversation context, user preferences, or tracking multi-step processes.

Example prompts to try:

* "Increment the counter 3 times and tell me the final count"
* "What's our current count? Add 2 more to it"
* "Let's increment the counter 5 times, but tell me each step"
* "Add 4 to our count and remind me where we started"
* "Increase the counter twice and summarize our journey"

## Code

```python agent_state.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Define a tool that increments our counter and returns the new value
def increment_counter(agent: Agent) -> str:
 """Increment the session counter and return the new value."""
 agent.session_state["count"] += 1
 return f"The count is now {agent.session_state['count']}"

# Create a State Manager Agent that maintains state
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 # Initialize the session state with a counter starting at 0
 session_state={"count": 0},
 tools=[increment_counter],
 # You can use variables from the session state in the instructions
 instructions=dedent("""\
 You are the State Manager, an enthusiastic guide to state management! 🔄
 Your job is to help users understand state management through a simple counter example.

 Follow these guidelines for every interaction:
 1. Always acknowledge the current state (count) when relevant
 2. Use the increment_counter tool to modify the state
 3. Explain state changes in a clear and engaging way

 Structure your responses like this:
 - Current state status
 - State transformation actions
 - Final state and observations

 Starting state (count) is: {count}\
 """),
 show_tool_calls=True,
 markdown=True,
)

# Example usage
agent.print_response(
 "Let's increment the counter 3 times and observe the state changes!",
 stream=True,
)

# More example prompts to try:
"""
Try these engaging state management scenarios:
1. "Update our state 4 times and track the changes"
2. "Modify the counter twice and explain the state transitions"
3. "Increment 3 times and show how state persists"
4. "Let's perform 5 state updates with observations"
5. "Add 3 to our count and explain the state management concept"
"""

print(f"Final session state: {agent.session_state}")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_state.py
 ```
 </Step>
</Steps>

# Agent Team
Source: https://docs.agno.com/examples/getting-started/agent-team

This example shows how to create a powerful team of AI agents working together to provide comprehensive financial analysis and news reporting. The team consists of:

1. Web Agent: Searches and analyzes latest news
2. Finance Agent: Analyzes financial data and market trends
3. Lead Editor: Coordinates and combines insights from both agents

Example prompts to try:

* "What's the latest news and financial performance of Apple (AAPL)?"
* "Analyze the impact of AI developments on NVIDIA's stock (NVDA)"
* "How are EV manufacturers performing? Focus on Tesla (TSLA) and Rivian (RIVN)"
* "What's the market outlook for semiconductor companies like AMD and Intel?"
* "Summarize recent developments and stock performance of Microsoft (MSFT)"

## Code

```python agent_team.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

web_agent = Agent(
 name="Web Agent",
 role="Search the web for information",
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 instructions=dedent("""\
 You are an experienced web researcher and news analyst! 🔍

 Follow these steps when searching for information:
 1. Start with the most recent and relevant sources
 2. Cross-reference information from multiple sources
 3. Prioritize reputable news outlets and official sources
 4. Always cite your sources with links
 5. Focus on market-moving news and significant developments

 Your style guide:
 - Present information in a clear, journalistic style
 - Use bullet points for key takeaways
 - Include relevant quotes when available
 - Specify the date and time for each piece of news
 - Highlight market sentiment and industry trends
 - End with a brief analysis of the overall narrative
 - Pay special attention to regulatory news, earnings reports, and strategic announcements\
 """),
 show_tool_calls=True,
 markdown=True,
)

finance_agent = Agent(
 name="Finance Agent",
 role="Get financial data",
 model=OpenAIChat(id="gpt-4o"),
 tools=[
 YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)
 ],
 instructions=dedent("""\
 You are a skilled financial analyst with expertise in market data! 📊

 Follow these steps when analyzing financial data:
 1. Start with the latest stock price, trading volume, and daily range
 2. Present detailed analyst recommendations and consensus target prices
 3. Include key metrics: P/E ratio, market cap, 52-week range
 4. Analyze trading patterns and volume trends
 5. Compare performance against relevant sector indices

 Your style guide:
 - Use tables for structured data presentation
 - Include clear headers for each data section
 - Add brief explanations for technical terms
 - Highlight notable changes with emojis (📈 📉)
 - Use bullet points for quick insights
 - Compare current values with historical averages
 - End with a data-driven financial outlook\
 """),
 show_tool_calls=True,
 markdown=True,
)

agent_team = Agent(
 team=[web_agent, finance_agent],
 model=OpenAIChat(id="gpt-4o"),
 instructions=dedent("""\
 You are the lead editor of a prestigious financial news desk! 📰

 Your role:
 1. Coordinate between the web researcher and financial analyst
 2. Combine their findings into a compelling narrative
 3. Ensure all information is properly sourced and verified
 4. Present a balanced view of both news and data
 5. Highlight key risks and opportunities

 Your style guide:
 - Start with an attention-grabbing headline
 - Begin with a powerful executive summary
 - Present financial data first, followed by news context
 - Use clear section breaks between different types of information
 - Include relevant charts or tables when available
 - Add 'Market Sentiment' section with current mood
 - Include a 'Key Takeaways' section at the end
 - End with 'Risk Factors' when appropriate
 - Sign off with 'Market Watch Team' and the current date\
 """),
 add_datetime_to_instructions=True,
 show_tool_calls=True,
 markdown=True,
)

# Example usage with diverse queries
agent_team.print_response(
 "Summarize analyst recommendations and share the latest news for NVDA", stream=True
)
agent_team.print_response(
 "What's the market outlook and financial performance of AI semiconductor companies?",
 stream=True,
)
agent_team.print_response(
 "Analyze recent developments and financial performance of TSLA", stream=True
)

# More example prompts to try:
"""
Advanced queries to explore:
1. "Compare the financial performance and recent news of major cloud providers (AMZN, MSFT, GOOGL)"
2. "What's the impact of recent Fed decisions on banking stocks? Focus on JPM and BAC"
3. "Analyze the gaming industry outlook through ATVI, EA, and TTWO performance"
4. "How are social media companies performing? Compare META and SNAP"
5. "What's the latest on AI chip manufacturers and their market position?"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai duckduckgo-search yfinance agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_team.py
 ```
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/getting-started/agent-with-knowledge

This example shows how to create an AI cooking assistant that combines knowledge from a curated recipe database with web searching capabilities. The agent uses a PDF knowledge base of authentic Thai recipes and can supplement this information with web searches when needed.

Example prompts to try:

* "How do I make authentic Pad Thai?"
* "What's the difference between red and green curry?"
* "Can you explain what galangal is and possible substitutes?"
* "Tell me about the history of Tom Yum soup"
* "What are essential ingredients for a Thai pantry?"
* "How do I make Thai basil chicken (Pad Kra Pao)?"

## Code

```python agent_with_knowledge.py
from textwrap import dedent

from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType

# Create a Recipe Expert Agent with knowledge of Thai recipes
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 instructions=dedent("""\
 You are a passionate and knowledgeable Thai cuisine expert! 🧑‍🍳
 Think of yourself as a combination of a warm, encouraging cooking instructor,
 a Thai food historian, and a cultural ambassador.

 Follow these steps when answering questions:
 1. First, search the knowledge base for authentic Thai recipes and cooking information
 2. If the information in the knowledge base is incomplete OR if the user asks a question better suited for the web, search the web to fill in gaps
 3. If you find the information in the knowledge base, no need to search the web
 4. Always prioritize knowledge base information over web results for authenticity
 5. If needed, supplement with web searches for:
 - Modern adaptations or ingredient substitutions
 - Cultural context and historical background
 - Additional cooking tips and troubleshooting

 Communication style:
 1. Start each response with a relevant cooking emoji
 2. Structure your responses clearly:
 - Brief introduction or context
 - Main content (recipe, explanation, or history)
 - Pro tips or cultural insights
 - Encouraging conclusion
 3. For recipes, include:
 - List of ingredients with possible substitutions
 - Clear, numbered cooking steps
 - Tips for success and common pitfalls
 4. Use friendly, encouraging language

 Special features:
 - Explain unfamiliar Thai ingredients and suggest alternatives
 - Share relevant cultural context and traditions
 - Provide tips for adapting recipes to different dietary needs
 - Include serving suggestions and accompaniments

 End each response with an uplifting sign-off like:
 - 'Happy cooking! ขอให้อร่อย (Enjoy your meal)!'
 - 'May your Thai cooking adventure bring joy!'
 - 'Enjoy your homemade Thai feast!'

 Remember:
 - Always verify recipe authenticity with the knowledge base
 - Clearly indicate when information comes from web sources
 - Be encouraging and supportive of home cooks at all skill levels\
 """),
 knowledge=PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=LanceDb(
 uri="tmp/lancedb",
 table_name="recipe_knowledge",
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
 ),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
 add_references=True,
)

# Comment out after the knowledge base is loaded
if agent.knowledge is not None:
 agent.knowledge.load()

agent.print_response(
 "How do I make chicken and galangal in coconut milk soup", stream=True
)
agent.print_response("What is the history of Thai curry?", stream=True)
agent.print_response("What ingredients do I need for Pad Thai?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai lancedb tantivy pypdf duckduckgo-search agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_with_knowledge.py
 ```
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/getting-started/agent-with-storage

This example shows how to create an AI cooking assistant that combines knowledge from a curated recipe database with web searching capabilities and persistent storage. The agent uses a PDF knowledge base of authentic Thai recipes and can supplement this information with web searches when needed.

Example prompts to try:

* "How do I make authentic Pad Thai?"
* "What's the difference between red and green curry?"
* "Can you explain what galangal is and possible substitutes?"
* "Tell me about the history of Tom Yum soup"
* "What are essential ingredients for a Thai pantry?"
* "How do I make Thai basil chicken (Pad Kra Pao)?"

## Code

```python agent_with_storage.py
from textwrap import dedent
from typing import List, Optional

import typer
from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.vectordb.lancedb import LanceDb, SearchType
from rich import print

agent_knowledge = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=LanceDb(
 uri="tmp/lancedb",
 table_name="recipe_knowledge",
 search_type=SearchType.hybrid,
 embedder=OpenAIEmbedder(id="text-embedding-3-small"),
 ),
)

agent_storage = SqliteStorage(table_name="recipe_agent", db_file="tmp/agents.db")

def recipe_agent(user: str = "user"):
 session_id: Optional[str] = None

 # Ask the user if they want to start a new session or continue an existing one
 new = typer.confirm("Do you want to start a new session?")

 if not new:
 existing_sessions: List[str] = agent_storage.get_all_session_ids(user)
 if len(existing_sessions) > 0:
 session_id = existing_sessions[0]

 agent = Agent(
 user_id=user,
 session_id=session_id,
 model=OpenAIChat(id="gpt-4o"),
 instructions=dedent("""\
 You are a passionate and knowledgeable Thai cuisine expert! 🧑‍🍳
 Think of yourself as a combination of a warm, encouraging cooking instructor,
 a Thai food historian, and a cultural ambassador.

 Follow these steps when answering questions:
 1. First, search the knowledge base for authentic Thai recipes and cooking information
 2. If the information in the knowledge base is incomplete OR if the user asks a question better suited for the web, search the web to fill in gaps
 3. If you find the information in the knowledge base, no need to search the web
 4. Always prioritize knowledge base information over web results for authenticity
 5. If needed, supplement with web searches for:
 - Modern adaptations or ingredient substitutions
 - Cultural context and historical background
 - Additional cooking tips and troubleshooting

 Communication style:
 1. Start each response with a relevant cooking emoji
 2. Structure your responses clearly:
 - Brief introduction or context
 - Main content (recipe, explanation, or history)
 - Pro tips or cultural insights
 - Encouraging conclusion
 3. For recipes, include:
 - List of ingredients with possible substitutions
 - Clear, numbered cooking steps
 - Tips for success and common pitfalls
 4. Use friendly, encouraging language

 Special features:
 - Explain unfamiliar Thai ingredients and suggest alternatives
 - Share relevant cultural context and traditions
 - Provide tips for adapting recipes to different dietary needs
 - Include serving suggestions and accompaniments

 End each response with an uplifting sign-off like:
 - 'Happy cooking! ขอให้อร่อย (Enjoy your meal)!'
 - 'May your Thai cooking adventure bring joy!'
 - 'Enjoy your homemade Thai feast!'

 Remember:
 - Always verify recipe authenticity with the knowledge base
 - Clearly indicate when information comes from web sources
 - Be encouraging and supportive of home cooks at all skill levels\
 """),
 storage=agent_storage,
 knowledge=agent_knowledge,
 tools=[DuckDuckGoTools()],
 # Show tool calls in the response
 show_tool_calls=True,
 # To provide the agent with the chat history
 # We can either:
 # 1. Provide the agent with a tool to read the chat history
 # 2. Automatically add the chat history to the messages sent to the model
 #
 # 1. Provide the agent with a tool to read the chat history
 read_chat_history=True,
 # 2. Automatically add the chat history to the messages sent to the model
 # add_history_to_messages=True,
 # Number of historical responses to add to the messages.
 # num_history_responses=3,
 markdown=True,
 )

 print("You are about to chat with an agent!")
 if session_id is None:
 session_id = agent.session_id
 if session_id is not None:
 print(f"Started Session: {session_id}\n")
 else:
 print("Started Session\n")
 else:
 print(f"Continuing Session: {session_id}\n")

 # Runs the agent as a command line application
 agent.cli_app(markdown=True)

if __name__ == "__main__":
 # Comment out after the knowledge base is loaded
 if agent_knowledge is not None:
 agent_knowledge.load()

 typer.run(recipe_agent)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai lancedb tantivy pypdf duckduckgo-search sqlalchemy agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_with_storage.py
 ```
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/getting-started/agent-with-tools

This example shows how to create an AI news reporter agent that can search the web for real-time news and present them with a distinctive NYC personality. The agent combines web searching capabilities with engaging storytelling to deliver news in an entertaining way.

Example prompts to try:

* "What's the latest headline from Wall Street?"
* "Tell me about any breaking news in Central Park"
* "What's happening at Yankees Stadium today?"
* "Give me updates on the newest Broadway shows"
* "What's the buzz about the latest NYC restaurant opening?"

## Code

```python agent_with_tools.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

# Create a News Reporter Agent with a fun personality
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 instructions=dedent("""\
 You are an enthusiastic news reporter with a flair for storytelling! 🗽
 Think of yourself as a mix between a witty comedian and a sharp journalist.

 Follow these guidelines for every report:
 1. Start with an attention-grabbing headline using relevant emoji
 2. Use the search tool to find current, accurate information
 3. Present news with authentic NYC enthusiasm and local flavor
 4. Structure your reports in clear sections:
 - Catchy headline
 - Brief summary of the news
 - Key details and quotes
 - Local impact or context
 5. Keep responses concise but informative (2-3 paragraphs max)
 6. Include NYC-style commentary and local references
 7. End with a signature sign-off phrase

 Sign-off examples:
 - 'Back to you in the studio, folks!'
 - 'Reporting live from the city that never sleeps!'
 - 'This is [Your Name], live from the heart of Manhattan!'

 Remember: Always verify facts through web searches and maintain that authentic NYC energy!\
 """),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

# Example usage
agent.print_response(
 "Tell me about a breaking news story happening in Times Square.", stream=True
)

# More example prompts to try:
"""
Try these engaging news queries:
1. "What's the latest development in NYC's tech scene?"
2. "Tell me about any upcoming events at Madison Square Garden"
3. "What's the weather impact on NYC today?"
4. "Any updates on the NYC subway system?"
5. "What's the hottest food trend in Manhattan right now?"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python agent_with_tools.py
 ```
 </Step>
</Steps>

# Audio Agent
Source: https://docs.agno.com/examples/getting-started/audio-agent

This example shows how to create an AI agent that can process audio input and generate audio responses. You can use this agent for various voice-based interactions, from analyzing speech content to generating natural-sounding responses.

Example audio interactions to try:

* Upload a recording of a conversation for analysis
* Have the agent respond to questions with voice output
* Process different languages and accents
* Analyze tone and emotion in speech

## Code

```python audio_agent.py
from textwrap import dedent

import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

# Create an AI Voice Interaction Agent
agent = Agent(
 model=OpenAIChat(
 id="gpt-4o-audio-preview",
 modalities=["text", "audio"],
 audio={"voice": "alloy", "format": "wav"},
 ),
 description=dedent("""\
 You are an expert in audio processing and voice interaction, capable of understanding
 and analyzing spoken content while providing natural, engaging voice responses.
 You excel at comprehending context, emotion, and nuance in speech.\
 """),
 instructions=dedent("""\
 As a voice interaction specialist, follow these guidelines:
 1. Listen carefully to audio input to understand both content and context
 2. Provide clear, concise responses that address the main points
 3. When generating voice responses, maintain a natural, conversational tone
 4. Consider the speaker's tone and emotion in your analysis
 5. If the audio is unclear, ask for clarification

 Focus on creating engaging and helpful voice interactions!\
 """),
)

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()

# Process the audio and get a response
agent.run(
 "What's in this recording? Please analyze the content and tone.",
 audio=[Audio(content=response.content, format="wav")],
)

# Save the audio response if available
if agent.run_response.response_audio is not None:
 write_audio_to_file(
 audio=agent.run_response.response_audio.content, filename="tmp/response.wav"
 )

# More example interactions to try:
"""
Try these voice interaction scenarios:
1. "Can you summarize the main points discussed in this recording?"
2. "What emotions or tone do you detect in the speaker's voice?"
3. "Please provide a detailed analysis of the speech patterns and clarity"
4. "Can you identify any background noises or audio quality issues?"
5. "What is the overall context and purpose of this recording?"

Note: You can use your own audio files by converting them to base64 format.
Example for using your own audio file:

with open('your_audio.wav', 'rb') as audio_file:
 audio_data = audio_file.read()
 agent.run("Analyze this audio", audio=[Audio(content=audio_data, format="wav")])
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai requests agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python audio_agent.py
 ```
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/getting-started/basic-agent

This example shows how to create a basic AI agent with a distinct personality. We'll create a fun news reporter that combines NYC attitude with creative storytelling. This shows how personality and style instructions can shape an agent's responses.

Example prompts to try:

* "What's the latest scoop from Central Park?"
* "Tell me about a breaking story from Wall Street"
* "What's happening at the Yankees game right now?"
* "Give me the buzz about a new Broadway show"

## Code

```python basic_agent.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# Create our News Reporter with a fun personality
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 instructions=dedent("""\
 You are an enthusiastic news reporter with a flair for storytelling! 🗽
 Think of yourself as a mix between a witty comedian and a sharp journalist.

 Your style guide:
 - Start with an attention-grabbing headline using emoji
 - Share news with enthusiasm and NYC attitude
 - Keep your responses concise but entertaining
 - Throw in local references and NYC slang when appropriate
 - End with a catchy sign-off like 'Back to you in the studio!' or 'Reporting live from the Big Apple!'

 Remember to verify all facts while keeping that NYC energy high!\
 """),
 markdown=True,
)

# Example usage
agent.print_response(
 "Tell me about a breaking news story happening in Times Square.", stream=True
)

# More example prompts to try:
"""
Try these fun scenarios:
1. "What's the latest food trend taking over Brooklyn?"
2. "Tell me about a peculiar incident on the subway today"
3. "What's the scoop on the newest rooftop garden in Manhattan?"
4. "Report on an unusual traffic jam caused by escaped zoo animals"
5. "Cover a flash mob wedding proposal at Grand Central"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python basic_agent.py
 ```
 </Step>
</Steps>

# Custom Tools
Source: https://docs.agno.com/examples/getting-started/custom-tools

This example shows how to create and use your own custom tool with Agno.
You can replace the Hacker News functionality with any API or service you want!

Some ideas for your own tools:

* Weather data fetcher
* Stock price analyzer
* Personal calendar integration
* Custom database queries
* Local file operations

## Code

```python custom_tools.py
import json
from textwrap import dedent

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAIChat

def get_top_hackernews_stories(num_stories: int = 10) -> str:
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
 if "text" in story:
 story.pop("text", None)
 stories.append(story)
 return json.dumps(stories)

# Create a Tech News Reporter Agent with a Silicon Valley personality
agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 instructions=dedent("""\
 You are a tech-savvy Hacker News reporter with a passion for all things technology! 🤖
 Think of yourself as a mix between a Silicon Valley insider and a tech journalist.

 Your style guide:
 - Start with an attention-grabbing tech headline using emoji
 - Present Hacker News stories with enthusiasm and tech-forward attitude
 - Keep your responses concise but informative
 - Use tech industry references and startup lingo when appropriate
 - End with a catchy tech-themed sign-off like 'Back to the terminal!' or 'Pushing to production!'

 Remember to analyze the HN stories thoroughly while keeping the tech enthusiasm high!\
 """),
 tools=[get_top_hackernews_stories],
 show_tool_calls=True,
 markdown=True,
)

# Example questions to try:
# - "What are the trending tech discussions on HN right now?"
# - "Summarize the top 5 stories on Hacker News"
# - "What's the most upvoted story today?"
agent.print_response("Summarize the top 5 stories on hackernews?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai httpx agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python custom_tools.py
 ```
 </Step>
</Steps>

# Human in the Loop
Source: https://docs.agno.com/examples/getting-started/human-in-the-loop

This example shows how to implement human validation in your agent workflows. It demonstrates:

* Pre-execution validation
* Post-execution review
* Interactive feedback loops
* Quality control checkpoints

Example scenarios:

* Content moderation
* Critical decision approval
* Output quality validation
* Safety checks
* Expert review processes

## Code

```python human_in_the_loop.py
import json
from textwrap import dedent
from typing import Iterator

import httpx
from agno.agent import Agent
from agno.exceptions import StopAgentRun
from agno.tools import FunctionCall, tool
from rich.console import Console
from rich.pretty import pprint
from rich.prompt import Prompt

# This is the console instance used by the print_response method
# We can use this to stop and restart the live display and ask for user confirmation
console = Console()

def pre_hook(fc: FunctionCall):
 # Get the live display instance from the console
 live = console._live

 # Stop the live display temporarily so we can ask for user confirmation
 live.stop() # type: ignore

 # Ask for confirmation
 console.print(f"\nAbout to run [bold blue]{fc.function.name}[/]")
 message = (
 Prompt.ask("Do you want to continue?", choices=["y", "n"], default="y")
 .strip()
 .lower()
 )

 # Restart the live display
 live.start() # type: ignore

 # If the user does not want to continue, raise a StopExecution exception
 if message != "y":
 raise StopAgentRun(
 "Tool call cancelled by user",
 agent_message="Stopping execution as permission was not granted.",
 )

@tool(pre_hook=pre_hook)
def get_top_hackernews_stories(num_stories: int) -> Iterator[str]:
 """Fetch top stories from Hacker News after user confirmation.

 Args:
 num_stories (int): Number of stories to retrieve

 Returns:
 str: JSON string containing story details
 """
 # Fetch top story IDs
 response = httpx.get("https://hacker-news.firebaseio.com/v0/topstories.json")
 story_ids = response.json()

 # Yield story details
 for story_id in story_ids[:num_stories]:
 story_response = httpx.get(
 f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
 )
 story = story_response.json()
 if "text" in story:
 story.pop("text", None)
 yield json.dumps(story)

# Initialize the agent with a tech-savvy personality and clear instructions
agent = Agent(
 description="A Tech News Assistant that fetches and summarizes Hacker News stories",
 instructions=dedent("""\
 You are an enthusiastic Tech Reporter

 Your responsibilities:
 - Present Hacker News stories in an engaging and informative way
 - Provide clear summaries of the information you gather

 Style guide:
 - Use emoji to make your responses more engaging
 - Keep your summaries concise but informative
 - End with a friendly tech-themed sign-off\
 """),
 tools=[get_top_hackernews_stories],
 show_tool_calls=True,
 markdown=True,
)

# Example questions to try:
# - "What are the top 3 HN stories right now?"
# - "Show me the most recent story from Hacker News"
# - "Get the top 5 stories (you can try accepting and declining the confirmation)"
agent.print_response(
 "What are the top 2 hackernews stories?", stream=True, console=console
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python human_in_the_loop.py
 ```
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/getting-started/image-agent

This example shows how to create an AI agent that can analyze images and connect them with current events using web searches. Perfect for:

1. News reporting and journalism
2. Travel and tourism content
3. Social media analysis
4. Educational presentations
5. Event coverage

Example images to try:

* Famous landmarks (Eiffel Tower, Taj Mahal, etc.)
* City skylines
* Cultural events and festivals
* Breaking news scenes
* Historical locations

## Code

```python image_agent.py
from textwrap import dedent

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are a world-class visual journalist and cultural correspondent with a gift
 for bringing images to life through storytelling! 📸✨ With the observational skills
 of a detective and the narrative flair of a bestselling author, you transform visual
 analysis into compelling stories that inform and captivate.\
 """),
 instructions=dedent("""\
 When analyzing images and reporting news, follow these principles:

 1. Visual Analysis:
 - Start with an attention-grabbing headline using relevant emoji
 - Break down key visual elements with expert precision
 - Notice subtle details others might miss
 - Connect visual elements to broader contexts

 2. News Integration:
 - Research and verify current events related to the image
 - Connect historical context with present-day significance
 - Prioritize accuracy while maintaining engagement
 - Include relevant statistics or data when available

 3. Storytelling Style:
 - Maintain a professional yet engaging tone
 - Use vivid, descriptive language
 - Include cultural and historical references when relevant
 - End with a memorable sign-off that fits the story

 4. Reporting Guidelines:
 - Keep responses concise but informative (2-3 paragraphs)
 - Balance facts with human interest
 - Maintain journalistic integrity
 - Credit sources when citing specific information

 Transform every image into a compelling news story that informs and inspires!\
 """),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

# Example usage with a famous landmark
agent.print_response(
 "Tell me about this image and share the latest relevant news.",
 images=[
 Image(
 url="https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg"
 )
 ],
 stream=True,
)

# More examples to try:
"""
Sample prompts to explore:
1. "What's the historical significance of this location?"
2. "How has this place changed over time?"
3. "What cultural events happen here?"
4. "What's the architectural style and influence?"
5. "What recent developments affect this area?"

Sample image URLs to analyze:
1. Eiffel Tower: "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg"
2. Taj Mahal: "https://upload.wikimedia.org/wikipedia/commons/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg"
3. Golden Gate Bridge: "https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg"
"""

# To get the response in a variable:
# from rich.pretty import pprint
# response = agent.run(
# "Analyze this landmark's architecture and recent news.",
# images=[Image(url="YOUR_IMAGE_URL")],
# )
# pprint(response.content)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python image_agent.py
 ```
 </Step>
</Steps>

# Image Generation
Source: https://docs.agno.com/examples/getting-started/image-generation

This example shows how to create an AI agent that generates images using DALL-E.
You can use this agent to create various types of images, from realistic photos to artistic
illustrations and creative concepts.

Example prompts to try:

* "Create a surreal painting of a floating city in the clouds at sunset"
* "Generate a photorealistic image of a cozy coffee shop interior"
* "Design a cute cartoon mascot for a tech startup"
* "Create an artistic portrait of a cyberpunk samurai"

## Code

```python image_generation.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.dalle import DalleTools

# Create an Creative AI Artist Agent
image_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DalleTools()],
 description=dedent("""\
 You are an experienced AI artist with expertise in various artistic styles,
 from photorealism to abstract art. You have a deep understanding of composition,
 color theory, and visual storytelling.\
 """),
 instructions=dedent("""\
 As an AI artist, follow these guidelines:
 1. Analyze the user's request carefully to understand the desired style and mood
 2. Before generating, enhance the prompt with artistic details like lighting, perspective, and atmosphere
 3. Use the `create_image` tool with detailed, well-crafted prompts
 4. Provide a brief explanation of the artistic choices made
 5. If the request is unclear, ask for clarification about style preferences

 Always aim to create visually striking and meaningful images that capture the user's vision!\
 """),
 markdown=True,
 show_tool_calls=True,
)

# Example usage
image_agent.print_response(
 "Create a magical library with floating books and glowing crystals", stream=True
)

# Retrieve and display generated images
images = image_agent.get_images()
if images and isinstance(images, list):
 for image_response in images:
 image_url = image_response.url
 print(f"Generated image URL: {image_url}")

# More example prompts to try:
"""
Try these creative prompts:
1. "Generate a steampunk-style robot playing a violin"
2. "Design a peaceful zen garden during cherry blossom season"
3. "Create an underwater city with bioluminescent buildings"
4. "Generate a cozy cabin in a snowy forest at night"
5. "Create a futuristic cityscape with flying cars and skyscrapers"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python image_generation.py
 ```
 </Step>
</Steps>

# Introduction
Source: https://docs.agno.com/examples/getting-started/introduction

This guide walks through the basics of building Agents with Agno.

The examples build on each other, introducing new concepts and capabilities progressively. Each example contains detailed comments, example prompts, and required dependencies.

## Setup

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install openai duckduckgo-search yfinance lancedb tantivy pypdf requests exa-py newspaper4k lxml_html_clean sqlalchemy agno
```

Export your OpenAI API key:

```bash
export OPENAI_API_KEY=your_api_key
```

## Examples

<CardGroup cols={3}>
 <Card title="Basic Agent" icon="robot" iconType="duotone" href="./basic-agent">
 Build a news reporter with a vibrant personality. This Agent only shows basic LLM inference.
 </Card>

 <Card title="Agent with Tools" icon="toolbox" iconType="duotone" href="./agent-with-tools">
 Add web search capabilities using DuckDuckGo for real-time information gathering.
 </Card>

 <Card title="Agent with Knowledge" icon="brain" iconType="duotone" href="./agent-with-knowledge">
 Add a vector database to your agent to store and search knowledge.
 </Card>

 <Card title="Agent with Storage" icon="database" iconType="duotone" href="./agent-with-storage">
 Add persistence to your agents with session management and history capabilities.
 </Card>

 <Card title="Agent Team" icon="users" iconType="duotone" href="./agent-team">
 Create an agent team specializing in market research and financial analysis.
 </Card>

 <Card title="Structured Output" icon="code" iconType="duotone" href="./structured-output">
 Generate a structured output using a Pydantic model.
 </Card>

 <Card title="Custom Tools" icon="wrench" iconType="duotone" href="./custom-tools">
 Create and integrate custom tools with your agent.
 </Card>

 <Card title="Research Agent" icon="magnifying-glass" iconType="duotone" href="./research-agent">
 Build an AI research agent using Exa with controlled output steering.
 </Card>

 <Card title="Research Workflow" icon="diagram-project" iconType="duotone" href="./research-workflow">
 Create a research workflow combining web searches and content scraping.
 </Card>

 <Card title="Image Agent" icon="image" iconType="duotone" href="./image-agent">
 Create an agent that can understand images.
 </Card>

 <Card title="Image Generation" icon="paintbrush" iconType="duotone" href="./image-generation">
 Create an Agent that can generate images using DALL-E.
 </Card>

 <Card title="Video Generation" icon="video" iconType="duotone" href="./video-generation">
 Create an Agent that can generate videos using ModelsLabs.
 </Card>

 <Card title="Audio Agent" icon="microphone" iconType="duotone" href="./audio-agent">
 Create an Agent that can process audio input and generate responses.
 </Card>

 <Card title="Agent with State" icon="database" iconType="duotone" href="./agent-state">
 Create an Agent with session state management.
 </Card>

 <Card title="Agent Context" icon="sitemap" iconType="duotone" href="./agent-context">
 Evaluate dependencies at agent.run and inject them into the instructions.
 </Card>

 <Card title="Agent Session" icon="clock-rotate-left" iconType="duotone" href="./agent-session">
 Create an Agent with persistent session memory across conversations.
 </Card>

 <Card title="User Memories" icon="memory" iconType="duotone" href="./user-memories">
 Create an Agent that stores user memories and summaries.
 </Card>

 <Card title="Function Retries" icon="rotate" iconType="duotone" href="./retry-functions">
 Handle function retries for failed or unsatisfactory outputs.
 </Card>

 <Card title="Human in the Loop" icon="user-check" iconType="duotone" href="./human-in-the-loop">
 Add user confirmation and safety checks for interactive agent control.
 </Card>
</CardGroup>

Each example includes runnable code and detailed explanations. We recommend following them in order, as concepts build upon previous examples.

# Research Agent
Source: https://docs.agno.com/examples/getting-started/research-agent

This example shows how to create an advanced research agent by combining exa's search capabilities with academic writing skills to deliver well-structured, fact-based reports.

Key features demonstrated:

* Using Exa.ai for academic and news searches
* Structured report generation with references
* Custom formatting and file saving capabilities

Example prompts to try:

* "What are the latest developments in quantum computing?"
* "Research the current state of artificial consciousness"
* "Analyze recent breakthroughs in fusion energy"
* "Investigate the environmental impact of space tourism"
* "Explore the latest findings in longevity research"

## Code

```python research_agent.py
from datetime import datetime
from pathlib import Path
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

cwd = Path(__file__).parent.resolve()
tmp = cwd.joinpath("tmp")
if not tmp.exists():
 tmp.mkdir(exist_ok=True, parents=True)

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
 save_response_to_file=str(tmp.joinpath("{message}.md")),
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

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai exa-py agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python research_agent.py
 ```
 </Step>
</Steps>

# Research Workflow
Source: https://docs.agno.com/examples/getting-started/research-workflow

This example shows how to build a sophisticated research workflow that combines:
🔍 Web search capabilities for finding relevant sources
📚 Content extraction and processing
✍️ Academic-style report generation
💾 Smart caching for improved performance

We've used the following tools as they're available for free:

* DuckDuckGoTools: Searches the web for relevant articles
* Newspaper4kTools: Scrapes and processes article content

Example research topics to try:

* "What are the latest developments in quantum computing?"
* "Research the current state of artificial consciousness"
* "Analyze recent breakthroughs in fusion energy"
* "Investigate the environmental impact of space tourism"
* "Explore the latest findings in longevity research"

## Code

```python research_workflow.py
import json
from textwrap import dedent
from typing import Dict, Iterator, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.workflow.sqlite import SqliteWorkflowStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import RunEvent, RunResponse, Workflow
from pydantic import BaseModel, Field

class Article(BaseModel):
 title: str = Field(..., description="Title of the article.")
 url: str = Field(..., description="Link to the article.")
 summary: Optional[str] = Field(
 ..., description="Summary of the article if available."
 )

class SearchResults(BaseModel):
 articles: list[Article]

class ScrapedArticle(BaseModel):
 title: str = Field(..., description="Title of the article.")
 url: str = Field(..., description="Link to the article.")
 summary: Optional[str] = Field(
 ..., description="Summary of the article if available."
 )
 content: Optional[str] = Field(
 ...,
 description="Content of the in markdown format if available. Return None if the content is not available or does not make sense.",
 )

class ResearchReportGenerator(Workflow):
 description: str = dedent("""\
 Generate comprehensive research reports that combine academic rigor
 with engaging storytelling. This workflow orchestrates multiple AI agents to search, analyze,
 and synthesize information from diverse sources into well-structured reports.
 """)

 web_searcher: Agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[DuckDuckGoTools()],
 description=dedent("""\
 You are ResearchBot-X, an expert at discovering and evaluating academic and scientific sources.\
 """),
 instructions=dedent("""\
 You're a meticulous research assistant with expertise in source evaluation! 🔍
 Search for 10-15 sources and identify the 5-7 most authoritative and relevant ones.
 Prioritize:
 - Peer-reviewed articles and academic publications
 - Recent developments from reputable institutions
 - Authoritative news sources and expert commentary
 - Diverse perspectives from recognized experts
 Avoid opinion pieces and non-authoritative sources.\
 """),
 response_model=SearchResults,
 )

 article_scraper: Agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[Newspaper4kTools()],
 description=dedent("""\
 You are ContentBot-X, an expert at extracting and structuring academic content.\
 """),
 instructions=dedent("""\
 You're a precise content curator with attention to academic detail! 📚
 When processing content:
 - Extract content from the article
 - Preserve academic citations and references
 - Maintain technical accuracy in terminology
 - Structure content logically with clear sections
 - Extract key findings and methodology details
 - Handle paywalled content gracefully
 Format everything in clean markdown for optimal readability.\
 """),
 response_model=ScrapedArticle,
 )

 writer: Agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are Professor X-2000, a distinguished AI research scientist combining academic rigor with engaging narrative style.\
 """),
 instructions=dedent("""\
 Channel the expertise of a world-class academic researcher!
 🎯 Analysis Phase:
 - Evaluate source credibility and relevance
 - Cross-reference findings across sources
 - Identify key themes and breakthroughs
 💡 Synthesis Phase:
 - Develop a coherent narrative framework
 - Connect disparate findings
 - Highlight contradictions or gaps
 ✍️ Writing Phase:
 - Begin with an engaging executive summary, hook the reader
 - Present complex ideas clearly
 - Support all claims with citations
 - Balance depth with accessibility
 - Maintain academic tone while ensuring readability
 - End with implications and future directions\
 """),
 expected_output=dedent("""\
 # {Compelling Academic Title}

 ## Executive Summary
 {Concise overview of key findings and significance}

 ## Introduction
 {Research context and background}
 {Current state of the field}

 ## Methodology
 {Search and analysis approach}
 {Source evaluation criteria}

 ## Key Findings
 {Major discoveries and developments}
 {Supporting evidence and analysis}
 {Contrasting viewpoints}

 ## Analysis
 {Critical evaluation of findings}
 {Integration of multiple perspectives}
 {Identification of patterns and trends}

 ## Implications
 {Academic and practical significance}
 {Future research directions}
 {Potential applications}

 ## Key Takeaways
 - {Critical finding 1}
 - {Critical finding 2}
 - {Critical finding 3}

 ## References
 {Properly formatted academic citations}

 ---
 Report generated by Professor X-2000
 Advanced Research Division
 Date: {current_date}\
 """),
 markdown=True,
 )

 def run(
 self,
 topic: str,
 use_search_cache: bool = True,
 use_scrape_cache: bool = True,
 use_cached_report: bool = True,
 ) -> Iterator[RunResponse]:
 """
 Generate a comprehensive news report on a given topic.

 This function orchestrates a workflow to search for articles, scrape their content,
 and generate a final report. It utilizes caching mechanisms to optimize performance.

 Args:
 topic (str): The topic for which to generate the news report.
 use_search_cache (bool, optional): Whether to use cached search results. Defaults to True.
 use_scrape_cache (bool, optional): Whether to use cached scraped articles. Defaults to True.
 use_cached_report (bool, optional): Whether to return a previously generated report on the same topic. Defaults to False.

 Returns:
 Iterator[RunResponse]: An stream of objects containing the generated report or status information.

 Steps:
 1. Check for a cached report if use_cached_report is True.
 2. Search the web for articles on the topic:
 - Use cached search results if available and use_search_cache is True.
 - Otherwise, perform a new web search.
 3. Scrape the content of each article:
 - Use cached scraped articles if available and use_scrape_cache is True.
 - Scrape new articles that aren't in the cache.
 4. Generate the final report using the scraped article contents.

 The function utilizes the `session_state` to store and retrieve cached data.
 """
 logger.info(f"Generating a report on: {topic}")

 # Use the cached report if use_cached_report is True
 if use_cached_report:
 cached_report = self.get_cached_report(topic)
 if cached_report:
 yield RunResponse(
 content=cached_report, event=RunEvent.workflow_completed
 )
 return

 # Search the web for articles on the topic
 search_results: Optional[SearchResults] = self.get_search_results(
 topic, use_search_cache
 )
 # If no search_results are found for the topic, end the workflow
 if search_results is None or len(search_results.articles) == 0:
 yield RunResponse(
 event=RunEvent.workflow_completed,
 content=f"Sorry, could not find any articles on the topic: {topic}",
 )
 return

 # Scrape the search results
 scraped_articles: Dict[str, ScrapedArticle] = self.scrape_articles(
 search_results, use_scrape_cache
 )

 # Write a research report
 yield from self.write_research_report(topic, scraped_articles)

 def get_cached_report(self, topic: str) -> Optional[str]:
 logger.info("Checking if cached report exists")
 return self.session_state.get("reports", {}).get(topic)

 def add_report_to_cache(self, topic: str, report: str):
 logger.info(f"Saving report for topic: {topic}")
 self.session_state.setdefault("reports", {})
 self.session_state["reports"][topic] = report
 # Save the report to the storage
 self.write_to_storage()

 def get_cached_search_results(self, topic: str) -> Optional[SearchResults]:
 logger.info("Checking if cached search results exist")
 return self.session_state.get("search_results", {}).get(topic)

 def add_search_results_to_cache(self, topic: str, search_results: SearchResults):
 logger.info(f"Saving search results for topic: {topic}")
 self.session_state.setdefault("search_results", {})
 self.session_state["search_results"][topic] = search_results.model_dump()
 # Save the search results to the storage
 self.write_to_storage()

 def get_cached_scraped_articles(
 self, topic: str
 ) -> Optional[Dict[str, ScrapedArticle]]:
 logger.info("Checking if cached scraped articles exist")
 return self.session_state.get("scraped_articles", {}).get(topic)

 def add_scraped_articles_to_cache(
 self, topic: str, scraped_articles: Dict[str, ScrapedArticle]
 ):
 logger.info(f"Saving scraped articles for topic: {topic}")
 self.session_state.setdefault("scraped_articles", {})
 self.session_state["scraped_articles"][topic] = scraped_articles
 # Save the scraped articles to the storage
 self.write_to_storage()

 def get_search_results(
 self, topic: str, use_search_cache: bool, num_attempts: int = 3
 ) -> Optional[SearchResults]:
 # Get cached search_results from the session state if use_search_cache is True
 if use_search_cache:
 try:
 search_results_from_cache = self.get_cached_search_results(topic)
 if search_results_from_cache is not None:
 search_results = SearchResults.model_validate(
 search_results_from_cache
 )
 logger.info(
 f"Found {len(search_results.articles)} articles in cache."
 )
 return search_results
 except Exception as e:
 logger.warning(f"Could not read search results from cache: {e}")

 # If there are no cached search_results, use the web_searcher to find the latest articles
 for attempt in range(num_attempts):
 try:
 searcher_response: RunResponse = self.web_searcher.run(topic)
 if (
 searcher_response is not None
 and searcher_response.content is not None
 and isinstance(searcher_response.content, SearchResults)
 ):
 article_count = len(searcher_response.content.articles)
 logger.info(
 f"Found {article_count} articles on attempt {attempt + 1}"
 )
 # Cache the search results
 self.add_search_results_to_cache(topic, searcher_response.content)
 return searcher_response.content
 else:
 logger.warning(
 f"Attempt {attempt + 1}/{num_attempts} failed: Invalid response type"
 )
 except Exception as e:
 logger.warning(f"Attempt {attempt + 1}/{num_attempts} failed: {str(e)}")

 logger.error(f"Failed to get search results after {num_attempts} attempts")
 return None

 def scrape_articles(
 self, search_results: SearchResults, use_scrape_cache: bool
 ) -> Dict[str, ScrapedArticle]:
 scraped_articles: Dict[str, ScrapedArticle] = {}

 # Get cached scraped_articles from the session state if use_scrape_cache is True
 if use_scrape_cache:
 try:
 scraped_articles_from_cache = self.get_cached_scraped_articles(topic)
 if scraped_articles_from_cache is not None:
 scraped_articles = scraped_articles_from_cache
 logger.info(
 f"Found {len(scraped_articles)} scraped articles in cache."
 )
 return scraped_articles
 except Exception as e:
 logger.warning(f"Could not read scraped articles from cache: {e}")

 # Scrape the articles that are not in the cache
 for article in search_results.articles:
 if article.url in scraped_articles:
 logger.info(f"Found scraped article in cache: {article.url}")
 continue

 article_scraper_response: RunResponse = self.article_scraper.run(
 article.url
 )
 if (
 article_scraper_response is not None
 and article_scraper_response.content is not None
 and isinstance(article_scraper_response.content, ScrapedArticle)
 ):
 scraped_articles[article_scraper_response.content.url] = (
 article_scraper_response.content
 )
 logger.info(f"Scraped article: {article_scraper_response.content.url}")

 # Save the scraped articles in the session state
 self.add_scraped_articles_to_cache(topic, scraped_articles)
 return scraped_articles

 def write_research_report(
 self, topic: str, scraped_articles: Dict[str, ScrapedArticle]
 ) -> Iterator[RunResponse]:
 logger.info("Writing research report")
 # Prepare the input for the writer
 writer_input = {
 "topic": topic,
 "articles": [v.model_dump() for v in scraped_articles.values()],
 }
 # Run the writer and yield the response
 yield from self.writer.run(json.dumps(writer_input, indent=4), stream=True)
 # Save the research report in the cache
 self.add_report_to_cache(topic, self.writer.run_response.content)

# Run the workflow if the script is executed directly
if __name__ == "__main__":
 from rich.prompt import Prompt

 # Example research topics
 example_topics = [
 "quantum computing breakthroughs 2024",
 "artificial consciousness research",
 "fusion energy developments",
 "space tourism environmental impact",
 "longevity research advances",
 ]

 topics_str = "\n".join(
 f"{i + 1}. {topic}" for i, topic in enumerate(example_topics)
 )

 print(f"\n📚 Example Research Topics:\n{topics_str}\n")

 # Get topic from user
 topic = Prompt.ask(
 "[bold]Enter a research topic[/bold]\n✨",
 default="quantum computing breakthroughs 2024",
 )

 # Convert the topic to a URL-safe string for use in session_id
 url_safe_topic = topic.lower().replace(" ", "-")

 # Initialize the news report generator workflow
 generate_research_report = ResearchReportGenerator(
 session_id=f"generate-report-on-{url_safe_topic}",
 storage=SqliteWorkflowStorage(
 table_name="generate_research_report_workflow",
 db_file="tmp/workflows.db",
 ),
 )

 # Execute the workflow with caching enabled
 report_stream: Iterator[RunResponse] = generate_research_report.run(
 topic=topic,
 use_search_cache=True,
 use_scrape_cache=True,
 use_cached_report=True,
 )

 # Print the response
 pprint_run_response(report_stream, markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 openai duckduckgo-search newspaper4k lxml_html_clean sqlalchemy agno
 ```
 </Step>

 <Step title="Run the workflow">
 ```bash
 python research_workflow.py
 ```
 </Step>
</Steps>

# Retry Functions
Source: https://docs.agno.com/examples/getting-started/retry-functions

This example shows how to retry a function call if it fails or you do not like the output. This is useful for:

* Handling temporary failures
* Improving output quality through retries
* Implementing human-in-the-loop validation

## Code

```python retry_functions.py
from typing import Iterator

from agno.agent import Agent
from agno.exceptions import RetryAgentRun
from agno.tools import FunctionCall, tool

num_calls = 0

def pre_hook(fc: FunctionCall):
 global num_calls

 print(f"Pre-hook: {fc.function.name}")
 print(f"Arguments: {fc.arguments}")
 num_calls += 1
 if num_calls < 2:
 raise RetryAgentRun(
 "This wasn't interesting enough, please retry with a different argument"
 )

@tool(pre_hook=pre_hook)
def print_something(something: str) -> Iterator[str]:
 print(something)
 yield f"I have printed {something}"

agent = Agent(tools=[print_something], markdown=True)
agent.print_response("Print something interesting", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python retry_functions.py
 ```
 </Step>
</Steps>

# Structured Output
Source: https://docs.agno.com/examples/getting-started/structured-output

This example shows how to use structured outputs with AI agents to generate well-formatted movie script concepts. It shows two approaches:

1. JSON Mode: Traditional JSON response parsing
2. Structured Output: Enhanced structured data handling

Example prompts to try:

* "Tokyo" - Get a high-tech thriller set in futuristic Japan
* "Ancient Rome" - Experience an epic historical drama
* "Manhattan" - Explore a modern romantic comedy
* "Amazon Rainforest" - Adventure in an exotic location
* "Mars Colony" - Science fiction in a space settlement

## Code

```python structured_output.py
from textwrap import dedent
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIChat
from pydantic import BaseModel, Field

class MovieScript(BaseModel):
 setting: str = Field(
 ...,
 description="A richly detailed, atmospheric description of the movie's primary location and time period. Include sensory details and mood.",
 )
 ending: str = Field(
 ...,
 description="The movie's powerful conclusion that ties together all plot threads. Should deliver emotional impact and satisfaction.",
 )
 genre: str = Field(
 ...,
 description="The film's primary and secondary genres (e.g., 'Sci-fi Thriller', 'Romantic Comedy'). Should align with setting and tone.",
 )
 name: str = Field(
 ...,
 description="An attention-grabbing, memorable title that captures the essence of the story and appeals to target audience.",
 )
 characters: List[str] = Field(
 ...,
 description="4-6 main characters with distinctive names and brief role descriptions (e.g., 'Sarah Chen - brilliant quantum physicist with a dark secret').",
 )
 storyline: str = Field(
 ...,
 description="A compelling three-sentence plot summary: Setup, Conflict, and Stakes. Hook readers with intrigue and emotion.",
 )

# Agent that uses JSON mode
json_mode_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are an acclaimed Hollywood screenwriter known for creating unforgettable blockbusters! 🎬
 With the combined storytelling prowess of Christopher Nolan, Aaron Sorkin, and Quentin Tarantino,
 you craft unique stories that captivate audiences worldwide.

 Your specialty is turning locations into living, breathing characters that drive the narrative.\
 """),
 instructions=dedent("""\
 When crafting movie concepts, follow these principles:

 1. Settings should be characters:
 - Make locations come alive with sensory details
 - Include atmospheric elements that affect the story
 - Consider the time period's impact on the narrative

 2. Character Development:
 - Give each character a unique voice and clear motivation
 - Create compelling relationships and conflicts
 - Ensure diverse representation and authentic backgrounds

 3. Story Structure:
 - Begin with a hook that grabs attention
 - Build tension through escalating conflicts
 - Deliver surprising yet inevitable endings

 4. Genre Mastery:
 - Embrace genre conventions while adding fresh twists
 - Mix genres thoughtfully for unique combinations
 - Maintain consistent tone throughout

 Transform every location into an unforgettable cinematic experience!\
 """),
 response_model=MovieScript,
)

# Agent that uses structured outputs
structured_output_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are an acclaimed Hollywood screenwriter known for creating unforgettable blockbusters! 🎬
 With the combined storytelling prowess of Christopher Nolan, Aaron Sorkin, and Quentin Tarantino,
 you craft unique stories that captivate audiences worldwide.

 Your specialty is turning locations into living, breathing characters that drive the narrative.\
 """),
 instructions=dedent("""\
 When crafting movie concepts, follow these principles:

 1. Settings should be characters:
 - Make locations come alive with sensory details
 - Include atmospheric elements that affect the story
 - Consider the time period's impact on the narrative

 2. Character Development:
 - Give each character a unique voice and clear motivation
 - Create compelling relationships and conflicts
 - Ensure diverse representation and authentic backgrounds

 3. Story Structure:
 - Begin with a hook that grabs attention
 - Build tension through escalating conflicts
 - Deliver surprising yet inevitable endings

 4. Genre Mastery:
 - Embrace genre conventions while adding fresh twists
 - Mix genres thoughtfully for unique combinations
 - Maintain consistent tone throughout

 Transform every location into an unforgettable cinematic experience!\
 """),
 response_model=MovieScript,
)

# Example usage with different locations
json_mode_agent.print_response("Tokyo", stream=True)
structured_output_agent.print_response("Ancient Rome", stream=True)

# More examples to try:
"""
Creative location prompts to explore:
1. "Underwater Research Station" - For a claustrophobic sci-fi thriller
2. "Victorian London" - For a gothic mystery
3. "Dubai 2050" - For a futuristic heist movie
4. "Antarctic Research Base" - For a survival horror story
5. "Caribbean Island" - For a tropical adventure romance
"""

# To get the response in a variable:
# from rich.pretty import pprint

# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)
# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python structured_output.py
 ```
 </Step>
</Steps>

# User Memories
Source: https://docs.agno.com/examples/getting-started/user-memories

This example shows how to create an agent with persistent memory that stores:

1. Personalized user memories - facts and preferences learned about specific users
2. Session summaries - key points and context from conversations
3. Chat history - stored in SQLite for persistence

Key features:

* Stores user-specific memories in SQLite database
* Maintains session summaries for context
* Continues conversations across sessions with memory
* References previous context and user information in responses

Examples:
User: "My name is John and I live in NYC"
Agent: *Creates memory about John's location*

User: "What do you remember about me?"
Agent: *Recalls previous memories about John*

## Code

```python user_memories.py
import json
from textwrap import dedent
from typing import Optional

import typer
from agno.agent import Agent
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from rich.prompt import Prompt

def create_agent(user: str = "user"):
 session_id: Optional[str] = None

 # Ask if user wants to start new session or continue existing one
 new = typer.confirm("Do you want to start a new session?")

 # Initialize storage for both agent sessions and memories
 agent_storage = SqliteStorage(table_name="agent_memories", db_file="tmp/agents.db")

 if not new:
 existing_sessions = agent_storage.get_all_session_ids(user)
 if len(existing_sessions) > 0:
 session_id = existing_sessions[0]

 agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 user_id=user,
 session_id=session_id,
 # Configure memory system with SQLite storage
 memory=Memory(
 db=SqliteMemoryDb(
 table_name="agent_memory",
 db_file="tmp/agent_memory.db",
 ),
 ),
 enable_user_memories=True,
 enable_session_summaries=True,
 storage=agent_storage,
 add_history_to_messages=True,
 num_history_responses=3,
 # Enhanced system prompt for better personality and memory usage
 description=dedent("""\
 You are a helpful and friendly AI assistant with excellent memory.
 - Remember important details about users and reference them naturally
 - Maintain a warm, positive tone while being precise and helpful
 - When appropriate, refer back to previous conversations and memories
 - Always be truthful about what you remember or don't remember"""),
 )

 if session_id is None:
 session_id = agent.session_id
 if session_id is not None:
 print(f"Started Session: {session_id}\n")
 else:
 print("Started Session\n")
 else:
 print(f"Continuing Session: {session_id}\n")

 return agent

def print_agent_memory(agent):
 """Print the current state of agent's memory systems"""
 console = Console()

 messages = []
 session_id = agent.session_id
 session_run = agent.memory.runs[session_id][-1]
 for m in session_run.messages:
 message_dict = m.to_dict()
 messages.append(message_dict)

 # Print chat history
 console.print(
 Panel(
 JSON(
 json.dumps(
 messages,
 ),
 indent=4,
 ),
 title=f"Chat History for session_id: {session_run.session_id}",
 expand=True,
 )
 )

 # Print user memories
 for user_id in list(agent.memory.memories.keys()):
 console.print(
 Panel(
 JSON(
 json.dumps(
 [
 user_memory.to_dict()
 for user_memory in agent.memory.get_user_memories(user_id=user_id)
 ],
 indent=4,
 ),
 ),
 title=f"Memories for user_id: {user_id}",
 expand=True,
 )
 )

 # Print session summary
 for user_id in list(agent.memory.summaries.keys()):
 console.print(
 Panel(
 JSON(
 json.dumps(
 [
 summary.to_dict()
 for summary in agent.memory.get_session_summaries(user_id=user_id)
 ],
 indent=4,
 ),
 ),
 title=f"Summary for session_id: {agent.session_id}",
 expand=True,
 )
 )

def main(user: str = "user"):
 """Interactive chat loop with memory display"""
 agent = create_agent(user)

 print("Try these example inputs:")
 print("- 'My name is [name] and I live in [city]'")
 print("- 'I love [hobby/interest]'")
 print("- 'What do you remember about me?'")
 print("- 'What have we discussed so far?'\n")

 exit_on = ["exit", "quit", "bye"]
 while True:
 message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
 if message in exit_on:
 break

 agent.print_response(message=message, stream=True, markdown=True)
 print_agent_memory(agent)

if __name__ == "__main__":
 typer.run(main)

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai sqlalchemy agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python user_memories.py
 ```
 </Step>
</Steps>

# Video Generation
Source: https://docs.agno.com/examples/getting-started/video-generation

This example shows how to create an AI agent that generates videos using ModelsLabs.
You can use this agent to create various types of short videos, from animated scenes
to creative visual stories.

Example prompts to try:

* "Create a serene video of waves crashing on a beach at sunset"
* "Generate a magical video of butterflies flying in a enchanted forest"
* "Create a timelapse of a blooming flower in a garden"
* "Generate a video of northern lights dancing in the night sky"

## Code

```python video_generation.py
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.models_labs import ModelsLabTools

# Create a Creative AI Video Director Agent
video_agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[ModelsLabTools()],
 description=dedent("""\
 You are an experienced AI video director with expertise in various video styles,
 from nature scenes to artistic animations. You have a deep understanding of motion,
 timing, and visual storytelling through video content.\
 """),
 instructions=dedent("""\
 As an AI video director, follow these guidelines:
 1. Analyze the user's request carefully to understand the desired style and mood
 2. Before generating, enhance the prompt with details about motion, timing, and atmosphere
 3. Use the `generate_media` tool with detailed, well-crafted prompts
 4. Provide a brief explanation of the creative choices made
 5. If the request is unclear, ask for clarification about style preferences

 The video will be displayed in the UI automatically below your response.
 Always aim to create captivating and meaningful videos that bring the user's vision to life!\
 """),
 markdown=True,
 show_tool_calls=True,
)

# Example usage
video_agent.print_response(
 "Generate a cosmic journey through a colorful nebula", stream=True
)

# Retrieve and display generated videos
videos = video_agent.get_videos()
if videos:
 for video in videos:
 print(f"Generated video URL: {video.url}")

# More example prompts to try:
"""
Try these creative prompts:
1. "Create a video of autumn leaves falling in a peaceful forest"
2. "Generate a video of a cat playing with a ball"
3. "Create a video of a peaceful koi pond with rippling water"
4. "Generate a video of a cozy fireplace with dancing flames"
5. "Create a video of a mystical portal opening in a magical realm"
"""
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export MODELS_LAB_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python video_generation.py
 ```
 </Step>
</Steps>

# Examples Gallery
Source: https://docs.agno.com/examples/introduction

Explore Agno's example gallery showcasing everything from single-agent tasks to sophisticated multi-agent workflows.

Welcome to Agno's example gallery! Here you'll discover examples showcasing everything from **single-agent tasks** to sophisticated **multi-agent workflows**. You can either:

* Run the examples individually
* Clone the entire [Agno cookbook](https://github.com/agno-agi/agno/tree/main/cookbook)

Have an interesting example to share? Please consider [contributing](https://github.com/agno-agi/agno-docs) to our growing collection.

## Getting Started

If you're just getting started, follow the [Getting Started](/examples/getting-started) guide for a step-by-step tutorial. The examples build on each other, introducing new concepts and capabilities progressively.

## Use Cases

Build real-world applications with Agno.

<CardGroup cols={3}>
 <Card title="Simple Agents" icon="user-astronaut" iconType="duotone" href="/examples/agents">
 Simple agents for web scraping, data processing, financial analysis, etc.
 </Card>

 <Card title="Advanced Workflows" icon="diagram-project" iconType="duotone" href="/examples/workflows">
 Advanced workflows for creating blog posts, investment reports, etc.
 </Card>

 <Card title="Full stack Applications" icon="brain-circuit" iconType="duotone" href="/examples/applications">
 Full stack applications like the LLM OS that come with a UI, database etc.
 </Card>
</CardGroup>

## Agent Concepts

Explore Agent concepts with detailed examples.

<CardGroup cols={3}>
 <Card title="Multimodal" icon="image" iconType="duotone" href="/examples/concepts/multimodal">
 Learn how to use multimodal Agents
 </Card>

 <Card title="RAG" icon="book-bookmark" iconType="duotone" href="/examples/concepts/rag">
 Learn how to use Agentic RAG
 </Card>

 <Card title="Knowledge" icon="brain-circuit" iconType="duotone" href="/examples/concepts/knowledge">
 Add domain-specific knowledge to your Agents
 </Card>

 <Card title="Async" icon="bolt" iconType="duotone" href="/examples/concepts/async">
 Run Agents asynchronously
 </Card>

 <Card title="Hybrid search" icon="magnifying-glass-plus" iconType="duotone" href="/examples/concepts/hybrid-search">
 Combine semantic and keyword 
 </Card>

 <Card title="Memory" icon="database" iconType="duotone" href="/examples/concepts/memory">
 Let Agents remember past conversations
 </Card>

 <Card title="Tools" icon="screwdriver-wrench" iconType="duotone" href="/examples/concepts/tools">
 Extend your Agents with 100s or tools
 </Card>

 <Card title="Storage" icon="hard-drive" iconType="duotone" href="/examples/concepts/storage">
 Store Agents sessions in a database
 </Card>

 <Card title="Vector Databases" icon="database" iconType="duotone" href="/examples/concepts/vectordb">
 Store Knowledge in Vector Databases
 </Card>

 <Card title="Embedders" icon="database" iconType="duotone" href="/examples/concepts/embedders">
 Convert text to embeddings to store in VectorDbs
 </Card>
</CardGroup>

## Models

Explore different models with Agno.

<CardGroup cols={3}>
 <Card title="OpenAI" icon="network-wired" iconType="duotone" href="/examples/models/openai">
 Examples using OpenAI GPT models
 </Card>

 <Card title="Ollama" icon="laptop-code" iconType="duotone" href="/examples/models/ollama">
 Examples using Ollama models locally
 </Card>

 <Card title="Anthropic" icon="network-wired" iconType="duotone" href="/examples/models/anthropic">
 Examples using Anthropic models like Claude
 </Card>

 <Card title="Cohere" icon="brain-circuit" iconType="duotone" href="/examples/models/cohere">
 Examples using Cohere command models
 </Card>

 <Card title="DeepSeek" icon="circle-nodes" iconType="duotone" href="/examples/models/deepseek">
 Examples using DeepSeek models
 </Card>

 <Card title="Gemini" icon="google" iconType="duotone" href="/examples/models/gemini">
 Examples using Google Gemini models
 </Card>

 <Card title="Groq" icon="bolt" iconType="duotone" href="/examples/models/groq">
 Examples using Groq's fast inference
 </Card>

 <Card title="Mistral" icon="wind" iconType="duotone" href="/examples/models/mistral">
 Examples using Mistral models
 </Card>

 <Card title="Azure" icon="microsoft" iconType="duotone" href="/examples/models/azure">
 Examples using Azure OpenAI
 </Card>

 <Card title="Fireworks" icon="sparkles" iconType="duotone" href="/examples/models/fireworks">
 Examples using Fireworks models
 </Card>

 <Card title="AWS" icon="aws" iconType="duotone" href="/examples/models/aws">
 Examples using Amazon Bedrock
 </Card>

 <Card title="Hugging Face" icon="face-awesome" iconType="duotone" href="/examples/models/huggingface">
 Examples using Hugging Face models
 </Card>

 <Card title="NVIDIA" icon="microchip" iconType="duotone" href="/examples/models/nvidia">
 Examples using NVIDIA models
 </Card>

 <Card title="Together" icon="people-group" iconType="duotone" href="/examples/models/together">
 Examples using Together AI models
 </Card>

 <Card title="xAI" icon="brain-circuit" iconType="duotone" href="/examples/models/xai">
 Examples using xAI models
 </Card>
</CardGroup>

# Basic Agent
Source: https://docs.agno.com/examples/models/anthropic/basic

## Code

```python cookbook/models/anthropic/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.anthropic import Claude

agent = Agent(model=Claude(id="claude-3-5-sonnet-20241022"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
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
 python cookbook/models/anthropic/basic.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/anthropic/basic_stream

## Code

```python cookbook/models/anthropic/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.anthropic import Claude

agent = Agent(model=Claude(id="claude-3-5-sonnet-20241022"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/anthropic/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Code Execution Tool
Source: https://docs.agno.com/examples/models/anthropic/code_execution

Learn how to use Anthropic's code execution tool with Agno.

With Anthropic's [code execution tool](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool), your model can execute Python code in a secure, sandboxed environment.
This is useful for your model to perform tasks as analyzing data, creating visualizations, or performing complex calculations.

## Working example

```python
from agno.agent import Agent
from agno.models.anthropic import Claude

agent = Agent(
 model=Claude(
 id="claude-sonnet-4-20250514",
 default_headers={
 "anthropic-beta": "code-execution-2025-05-22"
 }
 ),
 tools=[
 {
 "type": "code_execution_20250522",
 "name": "code_execution",
 }
 ],
 markdown=True,
)

agent.print_response("Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]", stream=True)
```

# File Upload
Source: https://docs.agno.com/examples/models/anthropic/file_upload

Learn how to use Anthropic's Files API with Agno.

With Anthropic's [Files API](https://docs.anthropic.com/en/docs/build-with-claude/files), you can upload files and later reference them in other API calls.
This is handy when a file is referenced multiple times in the same flow.

## Usage

<Steps>
 <Step title="Upload a file">
 Initialize the Anthropic client and use `client.beta.files.upload`:

 ```python
 from anthropic import Anthropic

 file_path = Path("path/to/your/file.pdf")

 client = Anthropic()
 uploaded_file = client.beta.files.upload(file=file_path)
 ```
 </Step>

 <Step title="Initialize the Claude model">
 When initializing the `Claude` model, pass the necessary beta header:

 ```python
 from agno.agent import Agent
 from agno.models.anthropic import Claude

 agent = Agent(
 model=Claude(
 id="claude-opus-4-20250514",
 default_headers={"anthropic-beta": "files-api-2025-04-14"},
 )
 )
 ```
 </Step>

 <Step title="Reference the file">
 You can now reference the uploaded file when interacting with your Agno agent:

 ```python
 agent.print_response(
 "Summarize the contents of the attached file.",
 files=[File(external=uploaded_file)],
 )
 ```
 </Step>
</Steps>

Notice there are some storage limits attached to this feature. You can read more about that on Anthropic's [docs](https://docs.anthropic.com/en/docs/build-with-claude/files#file-storage-and-limits).

## Working example

```python cookbook/models/anthropic/pdf_input_file_upload.py
from pathlib import Path

from agno.agent import Agent
from agno.media import File
from agno.models.anthropic import Claude
from agno.utils.media import download_file
from anthropic import Anthropic

pdf_path = Path(__file__).parent.joinpath("ThaiRecipes.pdf")

# Download the file using the download_file function
download_file(
 "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf", str(pdf_path)
)

# Initialize Anthropic client
client = Anthropic()

# Upload the file to Anthropic
uploaded_file = client.beta.files.upload(
 file=Path(pdf_path),
)

if uploaded_file is not None:
 agent = Agent(
 model=Claude(
 id="claude-opus-4-20250514",
 default_headers={"anthropic-beta": "files-api-2025-04-14"},
 ),
 markdown=True,
 )

 agent.print_response(
 "Summarize the contents of the attached file.",
 files=[File(external=uploaded_file)],
 )
```

# Image Input Bytes Content
Source: https://docs.agno.com/examples/models/anthropic/image_input_bytes

## Code

```python cookbook/models/anthropic/image_input_bytes.py
from pathlib import Path
from agno.agent import Agent
from agno.media import Image
from agno.models.anthropic.claude import Claude
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.utils.media import download_image

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

image_path = Path(__file__).parent.joinpath("sample.jpg")

download_image(
 url="https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg",
 output_path=str(image_path),
)

# Read the image file content as bytes
image_bytes = image_path.read_bytes()

agent.print_response(
 "Tell me about this image and give me the latest news about it.",
 images=[
 Image(content=image_bytes),
 ],
 stream=True,
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
 pip install -U anthropic agno duckduckgo-
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/anthropic/image_input_bytes.py 
 ```

 ```bash Windows
 python cookbook/models/anthropic/image_input_bytes.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Input URL
Source: https://docs.agno.com/examples/models/anthropic/image_input_url

## Code

```python cookbook/models/anthropic/image_input_url.py
from agno.agent import Agent
from agno.media import Image
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

agent.print_response(
 "Tell me about this image and search the web for more information.",
 images=[
 Image(
 url="https://upload.wikimedia.org/wikipedia/commons/a/a7/Camponotus_flavomarginatus_ant.jpg"
 ),
 ],
 stream=True,
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
 pip install -U anthropic agno duckduckgo-
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/anthropic/image_input_url.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/image_input_url.py 
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/anthropic/knowledge

## Code

```python cookbook/models/anthropic/knowledge.py
from agno.agent import Agent
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.anthropic import Claude
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=AzureOpenAIEmbedder(),
 ),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 knowledge=knowledge_base,
 show_tool_calls=True,
 debug_mode=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API keys">
 ```bash
 export ANTHROPIC_API_KEY=xxx
 export OPENAI_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic sqlalchemy pgvector pypdf openai agno
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
 python cookbook/models/anthropic/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PDF Input Bytes Agent
Source: https://docs.agno.com/examples/models/anthropic/pdf_input_bytes

## Code

```python cookbook/models/anthropic/pdf_input_bytes.py
from pathlib import Path
from agno.agent import Agent
from agno.media import File
from agno.models.anthropic import Claude
from agno.utils.media import download_file

pdf_path = Path(__file__).parent.joinpath("ThaiRecipes.pdf")

# Download the file using the download_file function
download_file(
 "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf", str(pdf_path)
)

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 markdown=True,
)

agent.print_response(
 "Summarize the contents of the attached file.",
 files=[
 File(
 content=pdf_path.read_bytes(),
 ),
 ],
)

print("Citations:")
print(agent.run_response.citations)
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
 python cookbook/models/anthropic/pdf_input_bytes.py 
 ```

 ```bash Windows
 python cookbook/models/anthropic/pdf_input_bytes.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PDF Input Local Agent
Source: https://docs.agno.com/examples/models/anthropic/pdf_input_local

## Code

```python cookbook/models/anthropic/pdf_input_local.py
from pathlib import Path
from agno.agent import Agent
from agno.media import File
from agno.models.anthropic import Claude
from agno.utils.media import download_file

pdf_path = Path(__file__).parent.joinpath("ThaiRecipes.pdf")

# Download the file using the download_file function
download_file(
 "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf", str(pdf_path)
)

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 markdown=True,
)

agent.print_response(
 "Summarize the contents of the attached file.",
 files=[
 File(
 filepath=pdf_path,
 ),
 ],
)

print("Citations:")
print(agent.run_response.citations)
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
 python cookbook/models/anthropic/pdf_input_local.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/pdf_input_local.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# PDF Input URL Agent
Source: https://docs.agno.com/examples/models/anthropic/pdf_input_url

## Code

```python cookbook/models/anthropic/pdf_input_url.py
from agno.agent import Agent
from agno.media import File
from agno.models.anthropic import Claude

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 markdown=True,
)

agent.print_response(
 "Summarize the contents of the attached file.",
 files=[
 File(url="https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"),
 ],
 stream=True,
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
 python cookbook/models/anthropic/pdf_input_url.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/pdf_input_url.py 
 ```
 </CodeGroup>
 </Step>
</Steps>

# Prompt Caching
Source: https://docs.agno.com/examples/models/anthropic/prompt_caching

Learn how to use prompt caching with Anthropic models and Agno.

Prompt caching can help reducing processing time and costs. Consider it if you are using the same prompt multiple times in any flow.

You can read more about prompt caching with Anthropic models [here](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching).

## Usage

To use prompt caching in your Agno setup, pass the `cache_system_prompt` argument when initializing the `Claude` model:

```python
from agno.agent import Agent
from agno.models.anthropic import Claude

agent = Agent(
 model=Claude(
 id="claude-3-5-sonnet-20241022",
 cache_system_prompt=True,
 ),
)
```

Notice that for prompt caching to work, the prompt needs to be of a certain length. You can read more about this on Anthropic's [docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching#cache-limitations).

## Extended cache

You can also use Anthropic's extended cache beta feature. This updates the cache duration from 5 minutes to 1 hour. To activate it, pass the `extended_cache_time` argument and the following beta header:

```python
from agno.agent import Agent
from agno.models.anthropic import Claude

agent = Agent(
 model=Claude(
 id="claude-3-5-sonnet-20241022",
 default_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"},
 cache_system_prompt=True,
 extended_cache_time=True,
 ),
)
```

## Working example

```python cookbook/models/anthropic/prompt_caching_extended.py
from pathlib import Path

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.utils.media import download_file

# Load an example large system message from S3. A large prompt like this would benefit from caching.
txt_path = Path(__file__).parent.joinpath("system_promt.txt")
download_file(
 "https://agno-public.s3.amazonaws.com/prompts/system_promt.txt",
 str(txt_path),
)
system_message = txt_path.read_text()

agent = Agent(
 model=Claude(
 id="claude-sonnet-4-20250514",
 default_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"}, # Set the beta header to use the extended cache time
 system_prompt=system_message,
 cache_system_prompt=True, # Activate prompt caching for Anthropic to cache the system prompt
 extended_cache_time=True, # Extend the cache time from the default to 1 hour
 ),
 system_message=system_message,
 markdown=True,
)

# First run - this will create the cache
response = agent.run(
 "Explain the difference between REST and GraphQL APIs with examples"
)
print(f"First run cache write tokens = {response.metrics['cache_write_tokens']}") # type: ignore

# Second run - this will use the cached system prompt
response = agent.run(
 "What are the key principles of clean code and how do I apply them in Python?"
)
print(f"Second run cache read tokens = {response.metrics['cached_tokens']}") # type: ignore
```

# Agent with Storage
Source: https://docs.agno.com/examples/models/anthropic/storage

## Code

```python cookbook/models/anthropic/storage.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
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
 pip install -U anthropic sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/anthropic/storage.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/anthropic/structured_output

## Code

```python cookbook/models/anthropic/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.anthropic import Claude
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

movie_agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20240620"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
run: RunResponse = movie_agent.run("New York")
pprint(run.content)
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
 python cookbook/models/anthropic/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/anthropic/tool_use

## Code

```python cookbook/models/anthropic/tool_use.py
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20240620"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U anthropic duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/anthropic/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/anthropic/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/aws/bedrock/basic

## Code

```python cookbook/models/aws/bedrock/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.aws import AwsBedrock

agent = Agent(
 model=AwsBedrock(id="mistral.mistral-large-2402-v1:0"), markdown=True
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/bedrock/basic.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/aws/bedrock/basic_stream

## Code

```python cookbook/models/aws/bedrock/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.aws import AwsBedrock

agent = Agent(
 model=AwsBedrock(id="mistral.mistral-large-2402-v1:0"), markdown=True
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/bedrock/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Image Input
Source: https://docs.agno.com/examples/models/aws/bedrock/image_agent

AWS Bedrock supports image input with models like `amazon.nova-pro-v1:0`. You can use this to analyze images and get information about them.

## Code

```python cookbook/models/aws/bedrock/image_agent.py
from pathlib import Path
from agno.agent import Agent
from agno.media import Image
from agno.models.aws import AwsBedrock
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=AwsBedrock(id="amazon.nova-pro-v1:0"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

image_path = Path(__file__).parent.joinpath("sample.jpg")

# Read the image file content as bytes
with open(image_path, "rb") as img_file:
 image_bytes = img_file.read()

agent.print_response(
 "Tell me about this image and give me the latest news about it.",
 images=[
 Image(content=image_bytes, format="jpeg"),
 ],
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 duckduckgo-search agno
 ```
 </Step>

 <Step title="Add an Image">
 Place an image file named `sample.jpg` in the same directory as your script.
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/bedrock/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/aws/bedrock/knowledge

## Code

```python cookbook/models/aws/bedrock/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.aws import AwsBedrock
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=AwsBedrock(id="mistral.mistral-large-2402-v1:0"), markdown=True
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 sqlalchemy pgvector pypdf openai psycopg agno
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
 python cookbook/models/aws/bedrock/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/aws/bedrock/storage

## Code

```python cookbook/models/aws/bedrock/storage.py
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=AwsBedrock(id="mistral.mistral-large-2402-v1:0"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 duckduckgo-search sqlalchemy psycopg agno
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
 python cookbook/models/aws/bedrock/storage.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/aws/bedrock/structured_output

## Code

```python cookbook/models/aws/bedrock/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.aws import AwsBedrock
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

movie_agent = Agent(
 model=AwsBedrock(id="mistral.mistral-large-2402-v1:0"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# movie_agent: RunResponse = movie_agent.run("New York")
# pprint(movie_agent.content)

movie_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/bedrock/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/aws/bedrock/tool_use

## Code

```python cookbook/models/aws/bedrock/tool_use.py
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=AwsBedrock(id="mistral.mistral-large-2402-v1:0"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U boto3 duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/bedrock/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/aws/bedrock/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/aws/claude/basic

## Code

```python cookbook/models/aws/claude/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.aws import Claude

agent = Agent(
 model=Claude(id="anthropic.claude-3-5-sonnet-20240620-v1:0"), markdown=True
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic[bedrock] agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/claude/basic.py
 ```

 ```bash Windows
 python cookbook/models/aws/claude/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/aws/claude/basic_stream

## Code

```python cookbook/models/aws/claude/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.aws import Claude

agent = Agent(
 model=Claude(id="anthropic.claude-3-5-sonnet-20240620-v1:0"), markdown=True
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic[bedrock] agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/claude/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/aws/claude/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/aws/claude/knowledge

## Code

```python cookbook/models/aws/claude/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.aws import Claude
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=Claude(id="claude-3-5-sonnet-20241022"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic[bedrock] sqlalchemy pgvector pypdf openai psycopg agno
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
 python cookbook/models/aws/claude/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/aws/claude/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/aws/claude/storage

## Code

```python cookbook/models/aws/claude/storage.py
from agno.agent import Agent
from agno.models.aws import Claude
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Claude(id="anthropic.claude-3-5-sonnet-20240620-v1:0"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic[bedrock] duckduckgo-search sqlalchemy psycopg agno
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
 python cookbook/models/aws/claude/storage.py
 ```

 ```bash Windows
 python cookbook/models/aws/claude/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/aws/claude/structured_output

## Code

```python cookbook/models/aws/claude/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.aws import Claude
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

movie_agent = Agent(
 model=Claude(id="anthropic.claude-3-5-sonnet-20240620-v1:0"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# movie_agent: RunResponse = movie_agent.run("New York")
# pprint(movie_agent.content)

movie_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic[bedrock] agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/claude/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/aws/claude/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/aws/claude/tool_use

## Code

```python cookbook/models/aws/claude/tool_use.py
from agno.agent import Agent
from agno.models.aws import Claude
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Claude(id="anthropic.claude-3-5-sonnet-20240620-v1:0"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your AWS Credentials">
 ```bash
 export AWS_ACCESS_KEY_ID=***
 export AWS_SECRET_ACCESS_KEY=***
 export AWS_REGION=***
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U anthropic[bedrock] duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/aws/claude/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/aws/claude/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/azure/ai_foundry/basic

## Code

```python cookbook/models/azure/ai_foundry/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.azure import AzureAIFoundry

agent = Agent(model=AzureAIFoundry(id="Phi-4"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story")
```

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
 python cookbook/models/azure/ai_foundry/basic.py
 ```

 ```bash Windows
 python cookbook/models/azure/ai_foundry/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Streaming
Source: https://docs.agno.com/examples/models/azure/ai_foundry/basic_stream

## Code

```python cookbook/models/azure/ai_foundry/basic_stream.py
from typing import Iterator # noqa

from agno.agent import Agent, RunResponse # noqa
from agno.models.azure import AzureAIFoundry

agent = Agent(model=AzureAIFoundry(id="Phi-4"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

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
 python cookbook/models/azure/ai_foundry/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/azure/ai_foundry/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge Base
Source: https://docs.agno.com/examples/models/azure/ai_foundry/knowledge

## Code

```python cookbook/models/azure/ai_foundry/knowledge.py
from agno.agent import Agent
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.azure import AzureAIFoundry
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=AzureOpenAIEmbedder(id="text-embedding-3-small"),
 ),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 model=AzureAIFoundry(id="Cohere-command-r-08-2024"),
 knowledge=knowledge_base,
 show_tool_calls=True,
 debug_mode=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

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
 pip install -U azure-ai-inference agno duckduckgo-search sqlalchemy pgvector pypdf
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
 python cookbook/models/azure/ai_foundry/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/azure/ai_foundry/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/azure/ai_foundry/storage

## Code

```python cookbook/models/azure/ai_foundry/storage.py
from agno.agent import Agent
from agno.models.azure import AzureAIFoundry
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=AzureAIFoundry(id="Cohere-command-r-08-2024"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

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
 pip install -U azure-ai-inference sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/azure/ai_foundry/storage.py
 ```

 ```bash Windows
 python cookbook/models/azure/ai_foundry/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/azure/ai_foundry/structured_output

## Code

```python cookbook/models/azure/ai_foundry/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.azure import AzureAIFoundry
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

agent = Agent(
 model=AzureAIFoundry(id="Phi-4"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
 # debug_mode=True,
)

# Get the response in a variable
# run: RunResponse = agent.run("New York")
# pprint(run.content)

agent.print_response("New York")
```

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
 python cookbook/models/azure/ai_foundry/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/azure/ai_foundry/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/azure/ai_foundry/tool_use

## Code

```python cookbook/models/azure/ai_foundry/tool_use.py
from agno.agent import Agent
from agno.models.azure import AzureAIFoundry
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=AzureAIFoundry(id="Cohere-command-r-08-2024"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?", stream=True)
```

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
 pip install -U azure-ai-inference agno duckduckgo-
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/azure/ai_foundry/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/azure/ai_foundry/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/azure/openai/basic

## Code

```python cookbook/models/azure/openai/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.azure import AzureOpenAI

agent = Agent(model=AzureOpenAI(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story")
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
 python cookbook/models/azure/openai/basic.py
 ```

 ```bash Windows
 python cookbook/models/azure/openai/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Streaming
Source: https://docs.agno.com/examples/models/azure/openai/basic_stream

## Code

```python cookbook/models/azure/openai/basic_stream.py
from typing import Iterator # noqa

from agno.agent import Agent, RunResponse # noqa
from agno.models.azure import AzureOpenAI

agent = Agent(model=AzureOpenAI(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/azure/openai/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/azure/openai/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge Base
Source: https://docs.agno.com/examples/models/azure/openai/knowledge

## Code

```python cookbook/models/azure/openai/knowledge.py
from agno.agent import Agent
from agno.embedder.azure_openai import AzureOpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.azure import AzureOpenAI
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=AzureOpenAIEmbedder(),
 ),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 model=AzureOpenAI(id="gpt-4o"),
 knowledge=knowledge_base,
 show_tool_calls=True,
 debug_mode=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
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
 pip install -U openai agno duckduckgo-search sqlalchemy pgvector pypdf
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
 python cookbook/models/azure/openai/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/azure/openai/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/azure/openai/storage

## Code

```python cookbook/models/azure/openai/storage.py
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=AzureOpenAI(id="gpt-4o"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
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
 pip install -U openai sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/azure/openai/storage.py
 ```

 ```bash Windows
 python cookbook/models/azure/openai/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/azure/openai/structured_output

## Code

```python cookbook/models/azure/openai/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.azure import AzureOpenAI
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

agent = Agent(
 model=AzureOpenAI(id="gpt-4o"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
 # debug_mode=True,
)

# Get the response in a variable
# run: RunResponse = agent.run("New York")
# pprint(run.content)

agent.print_response("New York")
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
 python cookbook/models/azure/openai/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/azure/openai/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/azure/openai/tool_use

## Code

```python cookbook/models/azure/openai/tool_use.py
from agno.agent import Agent
from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=AzureOpenAI(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U openai agno duckduckgo-
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/azure/openai/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/azure/openai/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/cerebras/basic

## Code

```python cookbook/models/cerebras/basic.py
from agno.agent import Agent
from agno.models.cerebras import Cerebras

agent = Agent(
 model=Cerebras(
 id="llama-4-scout-17b-16e-instruct",
 ),
 markdown=True,
)

agent.print_response("write a two sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cerebras-cloud-sdk agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cerebras/basic.py
 ```

 ```bash Windows
 python cookbook/models/cerebras/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/cerebras/basic_stream

## Code

```python cookbook/models/cerebras/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
import asyncio
from agno.models.cerebras import Cerebras

agent = Agent(
 model=Cerebras(
 id="llama-4-scout-17b-16e-instruct",
 ),
 markdown=True,
)

agent.print_response("write a two sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cerebras-cloud-sdk agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cerebras/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/cerebras/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge Base
Source: https://docs.agno.com/examples/models/cerebras/knowledge

## Code

```python cookbook/models/cerebras/basic_knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.cerebras import Cerebras
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=Cerebras(id="llama-4-scout-17b-16e-instruct"),
 knowledge=knowledge_base,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno cerebras-cloud-sdk
 ```
 </Step>

 <Step title="Start your Postgres server">
 Ensure your Postgres server is running and accessible at the connection string used in `db_url`.
 </Step>

 <Step title="Run Agent (first time)">
 The first run will load and index the PDF. This may take a while.

 <CodeGroup>
 ```bash Mac
 python cookbook/models/cerebras/basic_knowledge.py
 ```

 ```bash Windows
 python cookbook/models/cerebras/basic_knowledge.py
 ```
 </CodeGroup>
 </Step>

 <Step title="Subsequent Runs">
 After the first run, comment out or remove `knowledge_base.load(recreate=True)` to avoid reloading the PDF each time.
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/cerebras/storage

## Code

```python cookbook/models/cerebras/basic_storage.py
from agno.agent import Agent
from agno.models.cerebras import Cerebras
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Cerebras(id="llama-4-scout-17b-16e-instruct"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)

agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U duckduckgo-search cerebras-cloud-sdk agno
 ```
 </Step>

 <Step title="Start your Postgres server">
 Ensure your Postgres server is running and accessible at the connection string used in `db_url`.
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cerebras/basic_storage.py
 ```

 ```bash Windows
 python cookbook/models/cerebras/basic_storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/cerebras/structured_output

## Code

```python cookbook/models/cerebras/basic_json_schema.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.cerebras import Cerebras
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

# Agent that uses a JSON schema output
json_schema_output_agent = Agent(
 model=Cerebras(id="llama-4-scout-17b-16e-instruct"),
 description="You are a helpful assistant. Summarize the movie script based on the location in a JSON object.",
 response_model=MovieScript,
)

json_schema_output_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cerebras-cloud-sdk agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cerebras/basic_json_schema.py
 ```

 ```bash Windows
 python cookbook/models/cerebras/basic_json_schema.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/cerebras/tool_use

## Code

```python cookbook/models/cerebras/basic_tools.py
from agno.agent import Agent
from agno.models.cerebras import Cerebras
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Cerebras(
 id="llama-4-scout-17b-16e-instruct",
 ),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

agent.print_response("Whats happening in France?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cerebras-cloud-sdk agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cerebras/basic_tools.py
 ```

 ```bash Windows
 python cookbook/models/cerebras/basic_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/cerebras_openai/basic

## Code

```python cookbook/models/cerebras_openai/basic.py
from agno.agent import Agent
from agno.models.cerebras import CerebrasOpenAI

agent = Agent(
 model=CerebrasOpenAI(
 id="llama-4-scout-17b-16e-instruct",
 ),
 markdown=True,
)

# Print the response in the terminal
agent.print_response("write a two sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
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
 python cookbook/models/cerebras_openai/basic.py
 ```

 ```bash Windows
 python cookbook/models/cerebras_openai/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/cerebras_openai/basic_stream

## Code

```python cookbook/models/cerebras_openai/basic_stream.py
from agno.agent import Agent
from agno.models.cerebras import CerebrasOpenAI

agent = Agent(
 model=CerebrasOpenAI(
 id="llama-4-scout-17b-16e-instruct",
 ),
 markdown=True,
)

# Print the response in the terminal (streaming)
agent.print_response("write a two sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
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
 python cookbook/models/cerebras_openai/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/cerebras_openai/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/cerebras_openai/tool_use

## Code

```python cookbook/models/cerebras_openai/basic_tools.py
from agno.agent import Agent
from agno.models.cerebras import CerebrasOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=CerebrasOpenAI(id="llama-4-scout-17b-16e-instruct"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

# Print the response in the terminal
agent.print_response("Whats happening in France?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CEREBRAS_API_KEY=xxx
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
 python cookbook/models/cerebras_openai/basic_tools.py
 ```

 ```bash Windows
 python cookbook/models/cerebras_openai/basic_tools.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/cohere/basic

## Code

```python cookbook/models/cohere/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.cohere import Cohere

agent = Agent(model=Cohere(id="command-r-08-2024"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cohere/basic.py
 ```

 ```bash Windows
 python cookbook/models/cohere/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/cohere/basic_stream

## Code

```python cookbook/models/cohere/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.cohere import Cohere

agent = Agent(model=Cohere(id="command-r-08-2024"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cohere/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/cohere/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/cohere/image_agent

## Code

```python cookbook/models/cohere/image_agent.py
from agno.agent import Agent
from agno.media import Image
from agno.models.cohere import Cohere

agent = Agent(
 model=Cohere(id="c4ai-aya-vision-8b"),
 markdown=True,
)

agent.print_response(
 "Tell me about this image.",
 images=[
 Image(
 url="https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg"
 )
 ],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cohere/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/cohere/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/cohere/knowledge

## Code

```python cookbook/models/cohere/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.cohere import Cohere
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 model=Cohere(id="command-r-08-2024"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere sqlalchemy pgvector pypdf agno
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
 python cookbook/models/cohere/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/cohere/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/cohere/storage

## Code

```python cookbook/models/cohere/storage.py
from agno.agent import Agent
from agno.models.cohere import Cohere
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Cohere(id="command-r-08-2024"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/cohere/storage.py
 ```

 ```bash Windows
 python cookbook/models/cohere/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/cohere/structured_output

## Code

```python cookbook/models/cohere/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.cohere import Cohere
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

json_mode_agent = Agent(
 model=Cohere(id="command-r-08-2024"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
 # debug_mode=True,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)

json_mode_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cohere/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/cohere/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/cohere/tool_use

## Code

```python cookbook/models/cohere/tool_use.py
from agno.agent import Agent
from agno.models.cohere import Cohere
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Cohere(id="command-r-08-2024"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export CO_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U cohere duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/cohere/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/cohere/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/deepinfra/basic

## Code

```python cookbook/models/deepinfra/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.deepinfra import DeepInfra

agent = Agent(
 model=DeepInfra(id="meta-llama/Llama-2-70b-chat-hf"),
 markdown=True,
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export DEEPINFRA_API_KEY=xxx
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
 python cookbook/models/deepinfra/basic.py
 ```

 ```bash Windows
 python cookbook/models/deepinfra/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/deepinfra/basic_stream

## Code

```python cookbook/models/deepinfra/basic_stream.py
from typing import Iterator # noqa

from agno.agent import Agent, RunResponse # noqa
from agno.models.deepinfra import DeepInfra

agent = Agent(
 model=DeepInfra(id="meta-llama/Llama-2-70b-chat-hf"),
 markdown=True,
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export DEEPINFRA_API_KEY=xxx
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
 python cookbook/models/deepinfra/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/deepinfra/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/deepinfra/structured_output

## Code

```python cookbook/models/deepinfra/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.deepinfra import DeepInfra
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

json_mode_agent = Agent(
 model=DeepInfra(id="meta-llama/Llama-2-70b-chat-hf"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)

json_mode_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export DEEPINFRA_API_KEY=xxx
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
 python cookbook/models/deepinfra/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/deepinfra/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/deepinfra/tool_use

## Code

```python cookbook/models/deepinfra/tool_use.py
from agno.agent import Agent
from agno.models.deepinfra import DeepInfra
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=DeepInfra(id="meta-llama/Llama-2-70b-chat-hf"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export DEEPINFRA_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/deepinfra/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/deepinfra/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/deepseek/basic

## Code

```python cookbook/models/deepseek/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.deepseek import DeepSeek

agent = Agent(model=DeepSeek(id="deepseek-chat"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
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
 python cookbook/models/deepseek/basic.py
 ```

 ```bash Windows
 python cookbook/models/deepseek/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/deepseek/basic_stream

## Code

```python cookbook/models/deepseek/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.deepseek import DeepSeek

agent = Agent(model=DeepSeek(id="deepseek-chat"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/deepseek/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/deepseek/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/deepseek/structured_output

## Code

```python cookbook/models/deepseek/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.deepseek import DeepSeek
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

json_mode_agent = Agent(
 model=DeepSeek(id="deepseek-chat"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)

json_mode_agent.print_response("New York")
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
 python cookbook/models/deepseek/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/deepseek/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/deepseek/tool_use

## Code

```python cookbook/models/deepseek/tool_use.py
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=DeepSeek(id="deepseek-chat"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?")
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
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/deepseek/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/deepseek/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/fireworks/basic

## Code

```python cookbook/models/fireworks/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.fireworks import Fireworks

agent = Agent(
 model=Fireworks(id="accounts/fireworks/models/llama-v3p1-405b-instruct"),
 markdown=True,
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
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
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/fireworks/basic.py
 ```

 ```bash Windows
 python cookbook/models/fireworks/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/fireworks/basic_stream

## Code

```python cookbook/models/fireworks/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.fireworks import Fireworks

agent = Agent(
 model=Fireworks(id="accounts/fireworks/models/llama-v3p1-405b-instruct"),
 markdown=True,
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/fireworks/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/fireworks/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/fireworks/structured_output

## Code

```python cookbook/models/fireworks/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.fireworks import Fireworks
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
agent = Agent(
 model=Fireworks(id="accounts/fireworks/models/llama-v3p1-405b-instruct"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# response: RunResponse = agent.run("New York")
# pprint(json_mode_response.content)

agent.print_response("New York")
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
 pip install -U openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/fireworks/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/fireworks/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/fireworks/tool_use

## Code

```python cookbook/models/fireworks/tool_use.py
from agno.agent import Agent
from agno.models.fireworks import Fireworks
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Fireworks(id="accounts/fireworks/models/llama-v3p1-405b-instruct"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/fireworks/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/fireworks/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Input (Bytes Content)
Source: https://docs.agno.com/examples/models/gemini/audio_input_bytes_content

## Code

```python cookbook/models/google/gemini/audio_input_bytes_content.py
import requests
from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"

# Download the audio file from the URL as bytes
response = requests.get(url)
audio_content = response.content

agent.print_response(
 "Tell me about this audio",
 audio=[Audio(content=audio_content)],
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
 pip install -U google-genai requests agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/google/gemini/audio_input_bytes_content.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/audio_input_bytes_content.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Input (Upload the file)
Source: https://docs.agno.com/examples/models/gemini/audio_input_file_upload

## Code

```python cookbook/models/google/gemini/audio_input_file_upload.py
from pathlib import Path

from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini

model = Gemini(id="gemini-2.0-flash-exp")
agent = Agent(
 model=model,
 markdown=True,
)

# Please download a sample audio file to test this Agent and upload using:
audio_path = Path(__file__).parent.joinpath("sample.mp3")
audio_file = None

remote_file_name = f"files/{audio_path.stem.lower()}"
try:
 audio_file = model.get_client().files.get(name=remote_file_name)
except Exception as e:
 print(f"Error getting file {audio_path.stem}: {e}")
 pass

if not audio_file:
 try:
 audio_file = model.get_client().files.upload(
 file=audio_path,
 config=dict(name=audio_path.stem, display_name=audio_path.stem),
 )
 print(f"Uploaded audio: {audio_file}")
 except Exception as e:
 print(f"Error uploading audio: {e}")

agent.print_response(
 "Tell me about this audio",
 audio=[Audio(content=audio_file)],
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
 pip install -U google-genai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/google/gemini/audio_input_file_upload.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/audio_input_file_upload.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Input (Local file)
Source: https://docs.agno.com/examples/models/gemini/audio_input_local_file_upload

## Code

```python cookbook/models/google/gemini/audio_input_local_file_upload.py
from pathlib import Path
from agno.agent import Agent
from agno.media import Audio
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

# Please download a sample audio file to test this Agent and upload using:
audio_path = Path(__file__).parent.joinpath("sample.mp3")

agent.print_response(
 "Tell me about this audio",
 audio=[Audio(filepath=audio_path)],
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
 pip install -U google-genai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/google/gemini/audio_input_local_file_upload.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/audio_input_local_file_upload.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/gemini/basic

## Code

```python cookbook/models/google/gemini/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.google import Gemini

agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
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
 python cookbook/models/google/gemini/basic.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/gemini/basic_stream

## Code

```python cookbook/models/google/gemini/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.google import Gemini

agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/google/gemini/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Flash Thinking Agent
Source: https://docs.agno.com/examples/models/gemini/flash_thinking

## Code

```python cookbook/models/google/gemini/flash_thinking_agent.py
from agno.agent import Agent
from agno.models.google import Gemini

task = (
 "Three missionaries and three cannibals need to cross a river. "
 "They have a boat that can carry up to two people at a time. "
 "If, at any time, the cannibals outnumber the missionaries on either side of the river, the cannibals will eat the missionaries. "
 "How can all six people get across the river safely? Provide a step-by-step solution and show the solutions as an ascii diagram"
)

agent = Agent(model=Gemini(id="gemini-2.0-flash-thinking-exp-1219"), markdown=True)
agent.print_response(task, stream=True)
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
 python cookbook/models/google/gemini/flash_thinking_agent.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/flash_thinking_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/gemini/image_input

## Code

```python cookbook/models/google/gemini/image_input.py
from agno.agent import Agent
from agno.media import Image
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

agent.print_response(
 "Tell me about this image and give me the latest news about it.",
 images=[
 Image(
 url="https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg"
 ),
 ],
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
 pip install -U google-genai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/google/gemini/image_input.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/image_input.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/gemini/knowledge

## Code

```python cookbook/models/google/gemini/knowledge.py
from agno.agent import Agent
from agno.embedder.google import GeminiEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.google import Gemini
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=GeminiEmbedder(),
 ),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
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
 pip install -U google-genai sqlalchemy pgvector pypdf agno
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
 python cookbook/models/google/gemini/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with PDF Input (Local file)
Source: https://docs.agno.com/examples/models/gemini/pdf_input_local

## Code

```python cookbook/models/google/gemini/pdf_input_local.py
from pathlib import Path
from agno.agent import Agent
from agno.media import File
from agno.models.google import Gemini
from agno.utils.media import download_file

pdf_path = Path(__file__).parent.joinpath("ThaiRecipes.pdf")

# Download the file using the download_file function
download_file(
 "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf", str(pdf_path)
)

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
 add_history_to_messages=True,
)

agent.print_response(
 "Summarize the contents of the attached file.",
 files=[File(filepath=pdf_path)],
)
agent.print_response("Suggest me a recipe from the attached file.")
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
 python cookbook/models/google/gemini/pdf_input_local.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/pdf_input_local.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with PDF Input (URL)
Source: https://docs.agno.com/examples/models/gemini/pdf_input_url

## Code

```python cookbook/models/google/gemini/pdf_input_url.py
from agno.agent import Agent
from agno.media import File
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

agent.print_response(
 "Summarize the contents of the attached file.",
 files=[File(url="https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf")],
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
 python cookbook/models/google/gemini/pdf_input_url.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/pdf_input_url.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/gemini/storage

## Code

```python cookbook/models/google/gemini/storage.py
from agno.agent import Agent
from agno.models.google import Gemini
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
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
 pip install -U google-genai sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/google/gemini/storage.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/gemini/structured_output

## Code

```python cookbook/models/google/gemini/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.google import Gemini
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

movie_agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

movie_agent.print_response("New York")
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
 python cookbook/models/google/gemini/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/gemini/tool_use

## Code

```python cookbook/models/google/gemini/tool_use.py
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U google-genai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/google/gemini/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Video Input (Bytes Content)
Source: https://docs.agno.com/examples/models/gemini/video_input_bytes_content

## Code

```python cookbook/models/google/gemini/video_input_bytes_content.py
import requests
from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

url = "https://videos.pexels.com/video-files/5752729/5752729-uhd_2560_1440_30fps.mp4"

# Download the video file from the URL as bytes
response = requests.get(url)
video_content = response.content

agent.print_response(
 "Tell me about this video",
 videos=[Video(content=video_content)],
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
 python cookbook/models/google/gemini/video_input_bytes_content.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/video_input_bytes_content.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Video Input (File Upload)
Source: https://docs.agno.com/examples/models/gemini/video_input_file_upload

## Code

```python cookbook/models/google/gemini/video_input_file_upload.py
import time
from pathlib import Path

from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini
from agno.utils.log import logger

model = Gemini(id="gemini-2.0-flash-exp")
agent = Agent(
 model=model,
 markdown=True,
)

# Please download a sample video file to test this Agent
# Run: `wget https://storage.googleapis.com/generativeai-downloads/images/GreatRedSpot.mp4` to download a sample video
video_path = Path(__file__).parent.joinpath("samplevideo.mp4")
video_file = None
remote_file_name = f"files/{video_path.stem.lower().replace('_', '')}"
try:
 video_file = model.get_client().files.get(name=remote_file_name)
except Exception as e:
 logger.info(f"Error getting file {video_path.stem}: {e}")
 pass

# Upload the video file if it doesn't exist
if not video_file:
 try:
 logger.info(f"Uploading video: {video_path}")
 video_file = model.get_client().files.upload(
 file=video_path,
 config=dict(name=video_path.stem, display_name=video_path.stem),
 )

 # Check whether the file is ready to be used.
 while video_file.state.name == "PROCESSING":
 time.sleep(2)
 video_file = model.get_client().files.get(name=video_file.name)

 logger.info(f"Uploaded video: {video_file}")
 except Exception as e:
 logger.error(f"Error uploading video: {e}")

if __name__ == "__main__":
 agent.print_response(
 "Tell me about this video",
 videos=[Video(content=video_file)],
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
 pip install -U google-genai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/google/gemini/video_input_file_upload.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/video_input_file_upload.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Video Input (Local File Upload)
Source: https://docs.agno.com/examples/models/gemini/video_input_local_file_upload

## Code

```python cookbook/models/google/gemini/video_input_local_file_upload.py
from pathlib import Path

from agno.agent import Agent
from agno.media import Video
from agno.models.google import Gemini

agent = Agent(
 model=Gemini(id="gemini-2.0-flash-exp"),
 markdown=True,
)

# Get sample videos from https://www.pexels.com/search/videos/sample/
video_path = Path(__file__).parent.joinpath("sample_video.mp4")

agent.print_response("Tell me about this video?", videos=[Video(filepath=video_path)])
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
 python cookbook/models/google/gemini/video_input_local_file_upload.py
 ```

 ```bash Windows
 python cookbook/models/google/gemini/video_input_local_file_upload.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/groq/basic

## Code

```python cookbook/models/groq/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.groq import Groq

agent = Agent(model=Groq(id="llama-3.3-70b-versatile"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story")
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
 python cookbook/models/groq/basic.py
 ```

 ```bash Windows
 python cookbook/models/groq/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/groq/basic_stream

## Code

```python cookbook/models/groq/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.groq import Groq

agent = Agent(model=Groq(id="llama-3.3-70b-versatile"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response on the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/groq/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/groq/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/groq/image_agent

## Code

```python cookbook/models/groq/image_agent.py
from agno.agent import Agent
from agno.media import Image
from agno.models.groq import Groq

agent = Agent(model=Groq(id="llama-3.2-90b-vision-preview"))

agent.print_response(
 "Tell me about this image",
 images=[
 Image(url="https://upload.wikimedia.org/wikipedia/commons/f/f2/LPU-v1-die.jpg"),
 ],
 stream=True,
)
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
 python cookbook/models/groq/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/groq/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/groq/knowledge

## Code

```python cookbook/models/groq/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.groq import Groq
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=False) # Comment out after first run

agent = Agent(
 model=Groq(id="llama-3.3-70b-versatile"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
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
 pip install -U groq sqlalchemy pgvector pypdf openai agno
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
 python cookbook/models/groq/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/groq/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/groq/storage

## Code

```python cookbook/models/groq/storage.py
from agno.agent import Agent
from agno.models.groq import Groq
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Groq(id="llama-3.3-70b-versatile"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
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
 pip install -U groq duckduckgo-search sqlalchemy psycopg agno
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
 python cookbook/models/groq/storage.py
 ```

 ```bash Windows
 python cookbook/models/groq/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/groq/structured_output

## Code

```python cookbook/models/groq/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.groq import Groq
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

json_mode_agent = Agent(
 model=Groq(id="llama-3.3-70b-versatile"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

json_mode_agent.print_response("New York")
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
 python cookbook/models/groq/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/groq/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/groq/tool_use

## Code

```python cookbook/models/groq/tool_use.py
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

agent = Agent(
 model=Groq(id="llama-3.1-8b-instant"),
 tools=[DuckDuckGoTools(), Newspaper4kTools()],
 description="You are a senior NYT researcher writing an article on a topic.",
 instructions=[
 "For a given topic, search for the top 5 links.",
 "Then read each URL and extract the article text, if a URL isn't available, ignore it.",
 "Analyse and prepare an NYT worthy article based on the information.",
 ],
 markdown=True,
 show_tool_calls=True,
 add_datetime_to_instructions=True,
)
agent.print_response("Simulation theory", stream=True)
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
 pip install -U groq duckduckgo-search newspaper4k lxml_html_clean agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/groq/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/groq/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/huggingface/basic

## Code

```python cookbook/models/huggingface/basic.py
from agno.agent import Agent
from agno.models.huggingface import HuggingFace

agent = Agent(
 model=HuggingFace(
 id="mistralai/Mistral-7B-Instruct-v0.2", max_tokens=4096, temperature=0
 ),
)
agent.print_response(
 "What is meaning of life and then recommend 5 best books to read about it"
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export HF_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U huggingface_hub agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/huggingface/basic.py
 ```

 ```bash Windows
 python cookbook/models/huggingface/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/huggingface/basic_stream

## Code

```python cookbook/models/huggingface/basic_stream.py
from agno.agent import Agent
from agno.models.huggingface import HuggingFace

agent = Agent(
 model=HuggingFace(
 id="mistralai/Mistral-7B-Instruct-v0.2", max_tokens=4096, temperature=0
 ),
)
agent.print_response(
 "What is meaning of life and then recommend 5 best books to read about it",
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export HF_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U huggingface_hub agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/huggingface/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/huggingface/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Llama Essay Writer
Source: https://docs.agno.com/examples/models/huggingface/llama_essay_writer

## Code

```python cookbook/models/huggingface/llama_essay_writer.py
import os
from getpass import getpass

from agno.agent import Agent
from agno.models.huggingface import HuggingFace

agent = Agent(
 model=HuggingFace(
 id="meta-llama/Meta-Llama-3-8B-Instruct",
 max_tokens=4096,
 ),
 description="You are an essay writer. Write a 300 words essay on topic that will be provided by user",
)
agent.print_response("topic: AI")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export HF_TOKEN=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U huggingface_hub agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/huggingface/llama_essay_writer.py
 ```

 ```bash Windows
 python cookbook/models/huggingface/llama_essay_writer.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Async Basic Agent
Source: https://docs.agno.com/examples/models/ibm/async_basic

## Code

```python cookbook/models/ibm/watsonx/async_basic.py
import asyncio

from agno.agent import Agent, RunResponse
from agno.models.ibm import WatsonX

agent = Agent(model=WatsonX(id="ibm/granite-20b-code-instruct"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
asyncio.run(agent.aprint_response("Share a 2 sentence horror story"))
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/async_basic.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\async_basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example shows how to use the asynchronous API of Agno with IBM WatsonX. It creates an agent and uses `asyncio.run()` to execute the asynchronous `aprint_response` method.

# Async Streaming Agent
Source: https://docs.agno.com/examples/models/ibm/async_basic_stream

## Code

```python cookbook/models/ibm/watsonx/async_basic_stream.py
import asyncio

from agno.agent import Agent, RunResponse
from agno.models.ibm import WatsonX

agent = Agent(
 model=WatsonX(id="ibm/granite-20b-code-instruct"), debug_mode=True, markdown=True
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
asyncio.run(agent.aprint_response("Share a 2 sentence horror story", stream=True))
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/async_basic_stream.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\async_basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example combines asynchronous execution with streaming. It creates an agent with `debug_mode=True` for additional logging and uses the asynchronous API with streaming to get and display responses as they're generated.

# Agent with Async Tool Usage
Source: https://docs.agno.com/examples/models/ibm/async_tool_use

## Code

```python cookbook/models/ibm/watsonx/async_tool_use.py
import asyncio

from agno.agent import Agent
from agno.models.ibm import WatsonX
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=WatsonX(id="meta-llama/llama-3-3-70b-instruct"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

asyncio.run(agent.aprint_response("Whats happening in France?", stream=True))
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/async_tool_use.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\async_tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/ibm/basic

## Code

```python cookbook/models/ibm/watsonx/basic.py
from agno.agent import Agent, RunResponse
from agno.models.ibm import WatsonX

agent = Agent(model=WatsonX(id="ibm/granite-20b-code-instruct"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/basic.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example creates an agent using the IBM WatsonX model and prints a response directly to the terminal. The `markdown=True` parameter tells the agent to format the output as markdown, which can be useful for displaying rich text content.

# Streaming Basic Agent
Source: https://docs.agno.com/examples/models/ibm/basic_stream

## Code

```python cookbook/models/ibm/watsonx/basic_stream.py
from typing import Iterator
from agno.agent import Agent, RunResponse
from agno.models.ibm import WatsonX

agent = Agent(model=WatsonX(id="ibm/granite-20b-code-instruct"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/basic_stream.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example shows how to use streaming with IBM WatsonX. Setting `stream=True` when calling `print_response()` or `run()` enables token-by-token streaming, which can provide a more interactive user experience.

# Image Agent
Source: https://docs.agno.com/examples/models/ibm/image_agent_bytes

## Code

```python cookbook/models/ibm/watsonx/image_agent_bytes.py
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.ibm import WatsonX
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=WatsonX(id="meta-llama/llama-3-2-11b-vision-instruct"),
 tools=[DuckDuckGoTools()],
 markdown=True,
)

image_path = Path(__file__).parent.joinpath("sample.jpg")

# Read the image file content as bytes
with open(image_path, "rb") as img_file:
 image_bytes = img_file.read()

agent.print_response(
 "Tell me about this image and give me the latest news about it.",
 images=[
 Image(content=image_bytes),
 ],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai duckduckgo-search agno
 ```
 </Step>

 <Step title="Add sample image">
 Place a sample image named "sample.jpg" in the same directory as the script.
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/image_agent_bytes.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\image_agent_bytes.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example shows how to use IBM WatsonX with vision capabilities. It loads an image from a file and passes it to the model along with a prompt. The model can then analyze the image and provide relevant information.

Note: This example uses a vision-capable model (`meta-llama/llama-3-2-11b-vision-instruct`) and requires a sample image file.

# RAG Agent
Source: https://docs.agno.com/examples/models/ibm/knowledge

## Code

```python cookbook/models/ibm/watsonx/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.ibm import WatsonX
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=WatsonX(id="ibm/granite-20b-code-instruct"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai sqlalchemy pgvector psycopg pypdf openai agno
 ```
 </Step>

 <Step title="Set up PostgreSQL with pgvector">
 You need a PostgreSQL database with the pgvector extension installed. Adjust the `db_url` in the code to match your database configuration.
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/knowledge.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\knowledge.py
 ```
 </CodeGroup>
 </Step>

 <Step title="For subsequent runs">
 After the first run, comment out the `knowledge_base.load(recreate=True)` line to avoid reloading the PDF.
 </Step>
</Steps>

This example shows how to integrate a knowledge base with IBM WatsonX. It loads a PDF from a URL, processes it into a vector database (PostgreSQL with pgvector in this case), and then creates an agent that can query this knowledge base.

Note: You need to install several packages (`pgvector`, `pypdf`, etc.) and have a PostgreSQL database with the pgvector extension available.

# Agent with Storage
Source: https://docs.agno.com/examples/models/ibm/storage

## Code

```python cookbook/models/ibm/watsonx/storage.py
from agno.agent import Agent
from agno.models.ibm import WatsonX
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=WatsonX(id="ibm/granite-20b-code-instruct"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai sqlalchemy psycopg duckduckgo-search agno
 ```
 </Step>

 <Step title="Set up PostgreSQL">
 Make sure you have a PostgreSQL database running. You can adjust the `db_url` in the code to match your database configuration.
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/storage.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example shows how to use PostgreSQL storage with IBM WatsonX to maintain conversation state across multiple interactions. It creates an agent with a PostgreSQL storage backend and sends multiple messages, with the conversation history being preserved between them.

Note: You need to install the `sqlalchemy` package and have a PostgreSQL database available.

# Agent with Structured Output
Source: https://docs.agno.com/examples/models/ibm/structured_output

## Code

```python cookbook/models/ibm/watsonx/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse
from agno.models.ibm import WatsonX
from pydantic import BaseModel, Field
from rich.pretty import pprint

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

movie_agent = Agent(
 model=WatsonX(id="ibm/granite-20b-code-instruct"),
 description="You help people write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# movie_agent: RunResponse = movie_agent.run("New York")
# pprint(movie_agent.content)

movie_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai pydantic rich agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/structured_output.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

This example shows how to use structured output with IBM WatsonX. It defines a Pydantic model `MovieScript` with various fields and their descriptions, then creates an agent using this model as the `response_model`. The model's output will be parsed into this structured format.

# Agent with Tools
Source: https://docs.agno.com/examples/models/ibm/tool_use

## Code

```python cookbook/models/ibm/watsonx/tool_use.py
from agno.agent import Agent
from agno.models.ibm import WatsonX
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=WatsonX(id="meta-llama/llama-3-3-70b-instruct"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export IBM_WATSONX_API_KEY=xxx
 export IBM_WATSONX_PROJECT_ID=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ibm-watsonx-ai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ibm/watsonx/tool_use.py
 ```

 ```bash Windows
 python cookbook\models\ibm\watsonx\tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/litellm/basic

## Code

```python cookbook/models/litellm/basic_gpt.py
from agno.agent import Agent
from agno.models.litellm import LiteLLM

openai_agent = Agent(
 model=LiteLLM(
 id="gpt-4o",
 name="LiteLLM",
 ),
 markdown=True,
)

openai_agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/basic_gpt.py
 ```

 ```bash Windows
 python cookbook/models/litellm/basic_gpt.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/litellm/basic_stream

## Code

```python cookbook/models/litellm/basic_stream.py
from agno.agent import Agent
from agno.models.litellm import LiteLLM

openai_agent = Agent(
 model=LiteLLM(
 id="gpt-4o",
 name="LiteLLM",
 ),
 markdown=True,
)

openai_agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/litellm/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/litellm/knowledge

## Code

```python cookbook/models/litellm/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.litellm import LiteLLM
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=LiteLLM(id="gpt-4o"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/litellm/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/litellm/storage

## Code

```python cookbook/models/litellm/storage.py
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools

# Create a storage backend using the Sqlite database
storage = SqliteStorage(
 # store sessions in the ai.sessions table
 table_name="agent_sessions_storage",
 # db_file: Sqlite database file
 db_file="tmp/data.db",
)

# Add storage to the Agent
agent = Agent(
 model=LiteLLM(id="gpt-4o"),
 storage=storage,
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)

agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/storage.py
 ```

 ```bash Windows
 python cookbook/models/litellm/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/litellm/structured_output

## Code

```python cookbook/models/litellm/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.litellm import LiteLLM
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

json_mode_agent = Agent(
 model=LiteLLM(id="gpt-4o"),
 description="You write movie scripts.",
 response_model=MovieScript,
 debug_mode=True,
)

json_mode_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/litellm/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/litellm/tool_use

## Code

```python cookbook/models/litellm/tool_use.py
from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools.yfinance import YFinanceTools

openai_agent = Agent(
 model=LiteLLM(
 id="gpt-4o",
 name="LiteLLM",
 ),
 markdown=True,
 tools=[YFinanceTools()],
)

# Ask a question that would likely trigger tool use
openai_agent.print_response("How is TSLA stock doing right now?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/litellm/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/litellm_openai/basic

Make sure to start the proxy server:

```shell
litellm --model gpt-4o --host 127.0.0.1 --port 4000
```

## Code

```python cookbook/models/litellm_openai/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.litellm import LiteLLMOpenAI

agent = Agent(model=LiteLLMOpenAI(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm[proxy] openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm_openai/basic.py
 ```

 ```bash Windows
 python cookbook/models/litellm_openai/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/litellm_openai/basic_stream

Make sure to start the proxy server:

```shell
litellm --model gpt-4o --host 127.0.0.1 --port 4000
```

## Code

```python cookbook/models/litellm_openai/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.litellm import LiteLLMOpenAI

agent = Agent(model=LiteLLMOpenAI(id="gpt-4o"), markdown=True)

agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm[proxy] openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/litellm/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/litellm_openai/tool_use

Make sure to start the proxy server:

```shell
litellm --model gpt-4o --host 127.0.0.1 --port 4000
```

## Code

```python cookbook/models/litellm_openai/tool_use.py
"""Run `pip install duckduckgo-search` to install dependencies."""

from agno.agent import Agent
from agno.models.litellm import LiteLLMOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=LiteLLMOpenAI(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export LITELLM_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U litellm[proxy] openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/litellm_openai/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/litellm_openai/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/lmstudio/basic

## Code

```python cookbook/models/lmstudio/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.lmstudio import LMStudio

agent = Agent(model=LMStudio(id="qwen2.5-7b-instruct-1m"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">`bash pip install -U agno `</Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/lmstudio/basic.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/lmstudio/basic_stream

## Code

```python cookbook/models/lmstudio/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.lmstudio import LMStudio

agent = Agent(model=LMStudio(id="qwen2.5-7b-instruct-1m"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">`bash pip install -U agno `</Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/lmstudio/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/lmstudio/image_agent

## Code

```python cookbook/models/lmstudio/image_agent.py
import httpx

from agno.agent import Agent
from agno.media import Image
from agno.models.lmstudio import LMStudio

agent = Agent(
 model=LMStudio(id="llama3.2-vision"),
 markdown=True,
)

response = httpx.get(
 "https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg"
)

agent.print_response(
 "Tell me about this image",
 images=[Image(content=response.content)],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">`bash pip install -U agno `</Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/lmstudio/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/lmstudio/knowledge

## Code

```python cookbook/models/lmstudio/knowledge.py
from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.lmstudio import LMStudio
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=OllamaEmbedder(id="llama3.2", dimensions=3072),
 ),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=LMStudio(id="qwen2.5-7b-instruct-1m"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy pgvector pypdf agno
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
 python cookbook/models/lmstudio/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/lmstudio/storage

## Code

```python cookbook/models/lmstudio/storage.py
from agno.agent import Agent
from agno.models.lmstudio import LMStudio
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=LMStudio(id="qwen2.5-7b-instruct-1m"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/lmstudio/storage.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/lmstudio/structured_output

## Code

```python cookbook/models/lmstudio/structured_output.py
import asyncio
from typing import List

from agno.agent import Agent
from agno.models.lmstudio import LMStudio
from pydantic import BaseModel, Field

class MovieScript(BaseModel):
 name: str = Field(..., description="Give a name to this movie")
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
 characters: List[str] = Field(..., description="Name of characters for this movie.")
 storyline: str = Field(
 ..., description="3 sentence storyline for the movie. Make it exciting!"
 )

# Agent that returns a structured output
structured_output_agent = Agent(
 model=LMStudio(id="qwen2.5-7b-instruct-1m"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

# Run the agent synchronously
structured_output_agent.print_response("
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/lmstudio/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/lmstudio/tool_use

## Code

```python cookbook/models/lmstudio/tool_use.py
from agno.agent import Agent
from agno.models.lmstudio import LMStudio
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=LMStudio(id="qwen2.5-7b-instruct-1m"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install LM Studio">
 Install LM Studio from [here](https://lmstudio.ai/download) and download the
 model you want to use.
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/lmstudio/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/lmstudio/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/async_basic

## Code

```python cookbook/models/meta/async_basic.py
import asyncio
from agno.agent import Agent
from agno.models.meta import Llama

async def main():
 agent = Agent(
 model=Llama(id="Llama-4-Maverick-17B"),
 markdown=True,
 )
 response = await agent.aprint_response(
 "Generate a succinct summary of the latest research on climate change."
 )
asyncio.run(main())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/async_basic.py
 ```

 ```bash Windows
 python cookbook/models/meta/async_basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/async_image_input

## Code

```python cookbook/models/meta/async_image_input.py
import asyncio
from agno.agent import Agent
from agno.media import Image
from agno.models.meta import Llama

async def main():
 agent = Agent(
 model=Llama(id="Llama-4-Scout-17B"),
 markdown=True,
 )

 await agent.aprint_response(
 "Describe the scene in this image asynchronously.",
 images=[Image(content=image_bytes)],
 stream=True,
 )

asyncio.run(main())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/async_image_input.py
 ```

 ```bash Windows
 python cookbook/models/meta/async_image_input.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/async_stream

## Code

```python cookbook/models/meta/async_stream.py
import asyncio
from agno.agent import Agent
from agno.models.meta import Llama

async def main():
 agent = Agent(
 model=Llama(id="Llama-3.3-70B"),
 markdown=True,
 )
 
 await agent.aprint_response(
 "Share a two-sentence horror story.",
 stream=True
 )

asyncio.run(main())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/async_stream.py
 ```

 ```bash Windows
 python cookbook/models/meta/async_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/async_structured_output

## Code

```python cookbook/models/meta/async_structured_output.py
import asyncio
from typing import List
from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.meta import Llama

class MovieScript(BaseModel):
 name: str = Field(..., description="Name of the movie.")
 setting: str = Field(..., description="Provide a setting for the movie.")
 ending: str = Field(..., description="Describe the movie ending.")
 genre: str = Field(..., description="Genre of the movie.")
 characters: List[str] = Field(..., description="List of characters.")
 storyline: str = Field(..., description="A 3-sentence storyline.")

agent = Agent(
 model=Llama(id="Llama-3.3-70B"),
 response_model=MovieScript,
 markdown=True,
)

asyncio.run(
 agent.aprint_response(
 "Generate a movie script outline for a sci-fi adventure."
 )
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/async_structured_output.py
 ```

 ```bash Windows
 python cookbook/models/meta/async_structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/async_tool_use

## Code

```python cookbook/models/meta/async_tool_use.py
import asyncio

from agno.agent import Agent
from agno.models.meta import Llama
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Llama(id="Llama-4-Maverick-17B-128E-Instruct-FP8"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

asyncio.run(
 agent.aprint_response("What's happening in France?", stream=True)
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/async_tool_use.py
 ```

 ```bash Windows
 python cookbook/models/meta/async_tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/meta/basic

## Code

```python cookbook/models/meta/basic.py
from agno.agent import Agent
from agno.models.meta import Llama

agent = Agent(
 model=Llama(id="Llama-4-Maverick-17B-128E-Instruct-FP8"),
 markdown=True,
)

agent.print_response("Share a 2 sentence horror story.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/basic.py
 ```

 ```bash Windows
 python cookbook/models/meta/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/basic_stream

## Code

```python cookbook/models/meta/basic_stream.py
from agno.agent import Agent
from agno.models.meta import Llama

agent = Agent(
 model=Llama(id="Llama-4-Scout-17B"),
 markdown=True,
)

agent.print_response("Explain quantum entanglement in simple terms.", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/meta/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/image_input

## Code

```python cookbook/models/meta/image_input.py
from agno.agent import Agent
from agno.media import Image
from agno.models.meta import Llama

agent = Agent(
 model=Llama(id="Llama-4-Maverick-17B-128E-Instruct-FP8"),
 markdown=True,
)

agent.print_response(
 "Describe the scene in this image.",
 images=[Image(content=image_bytes)],
 stream=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/image_input.py
 ```

 ```bash Windows
 python cookbook/models/meta/image_input.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/structured_output

## Code

```python cookbook/models/meta/structured_output.py
from typing import List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.meta import Llama

class MovieScript(BaseModel):
 name: str = Field(..., description="Name of the movie.")
 setting: str = Field(..., description="Provide a setting for the movie.")
 ending: str = Field(..., description="Describe the movie ending.")
 genre: str = Field(..., description="Genre of the movie.")
 characters: List[str] = Field(..., description="List of characters.")
 storyline: str = Field(..., description="A 3-sentence storyline.")

agent = Agent(
 model=Llama(id="Llama-3.3-70B"),
 response_model=MovieScript,
 markdown=True,
)

agent.print_response("Generate a movie script outline for a sci-fi adventure.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/meta/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# null
Source: https://docs.agno.com/examples/models/meta/tool_use

## Code

```python cookbook/models/meta/tool_calling.py
from agno.agent import Agent
from agno.models.meta import Llama
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Llama(id="Llama-4-Maverick-17B-128E-Instruct-FP8"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("What's the latest developments in AI?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your LLAMA API key">
 ```bash
 export LLAMA_API_KEY=YOUR_API_KEY
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install llama-api-client duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/meta/tool_calling.py
 ```

 ```bash Windows
 python cookbook/models/meta/tool_calling.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/mistral/basic

## Code

```python cookbook/models/mistral/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.mistral import MistralChat

mistral_api_key = os.getenv("MISTRAL_API_KEY")

agent = Agent(
 model=MistralChat(
 id="mistral-large-latest",
 api_key=mistral_api_key,
 ),
 markdown=True,
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
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
 pip install -U mistralai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/mistral/basic.py
 ```

 ```bash Windows
 python cookbook/models/mistral/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/mistral/basic_stream

## Code

```python cookbook/models/mistral/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.mistral import MistralChat

mistral_api_key = os.getenv("MISTRAL_API_KEY")

agent = Agent(
 model=MistralChat(
 id="mistral-large-latest",
 api_key=mistral_api_key,
 ),
 markdown=True,
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 pip install -U mistralai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/mistral/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/mistral/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/mistral/structured_output

## Code

```python cookbook/models/mistral/structured_output.py
import os
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.mistral import MistralChat
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field
from rich.pretty import pprint # noqa

mistral_api_key = os.getenv("MISTRAL_API_KEY")

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

json_mode_agent = Agent(
 model=MistralChat(
 id="mistral-large-latest",
 api_key=mistral_api_key,
 ),
 tools=[DuckDuckGoTools()],
 description="You help people write movie scripts.",
 response_model=MovieScript,
 show_tool_calls=True,
 debug_mode=True,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)

json_mode_agent.print_response("Find a cool movie idea about London and write it.")
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
 pip install -U mistralai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/mistral/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/mistral/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/mistral/tool_use

## Code

```python cookbook/models/mistral/tool_use.py
from agno.agent import Agent
from agno.models.mistral import MistralChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=MistralChat(
 id="mistral-large-latest",
 ),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U mistralai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/mistral/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/mistral/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/nvidia/basic

## Code

```python cookbook/models/nvidia/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.nvidia import Nvidia

agent = Agent(model=Nvidia(id="meta/llama-3.3-70b-instruct"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export NVIDIA_API_KEY=xxx
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
 python cookbook/models/nvidia/basic.py
 ```

 ```bash Windows
 python cookbook/models/nvidia/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/nvidia/basic_stream

## Code

```python cookbook/models/nvidia/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.nvidia import Nvidia

agent = Agent(model=Nvidia(id="meta/llama-3.3-70b-instruct"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export NVIDIA_API_KEY=xxx
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
 python cookbook/models/nvidia/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/nvidia/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/nvidia/tool_use

## Code

```python cookbook/models/nvidia/tool_use.py
from agno.agent import Agent
from agno.models.nvidia import Nvidia
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Nvidia(id="meta/llama-3.3-70b-instruct"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export NVIDIA_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/nvidia/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/nvidia/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/ollama/basic

## Code

```python cookbook/models/ollama/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.ollama import Ollama

agent = Agent(model=Ollama(id="llama3.1:8b"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.1:8b
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
 python cookbook/models/ollama/basic.py
 ```

 ```bash Windows
 python cookbook/models/ollama/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/ollama/basic_stream

## Code

```python cookbook/models/ollama/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.ollama import Ollama

agent = Agent(model=Ollama(id="llama3.1:8b"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.1:8b
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
 python cookbook/models/ollama/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/ollama/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/ollama/image_agent

## Code

```python cookbook/models/ollama/image_agent.py
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.ollama import Ollama

agent = Agent(
 model=Ollama(id="llama3.2-vision"),
 markdown=True,
)

image_path = Path(__file__).parent.joinpath("super-agents.png")
agent.print_response(
 "Write a 3 sentence fiction story about the image",
 images=[Image(filepath=image_path)],
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.2-vision
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
 python cookbook/models/ollama/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/ollama/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/ollama/knowledge

## Code

```python cookbook/models/ollama/knowledge.py
from agno.agent import Agent
from agno.embedder.ollama import OllamaEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.ollama import Ollama
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(
 table_name="recipes",
 db_url=db_url,
 embedder=OllamaEmbedder(id="llama3.2", dimensions=3072),
 ),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=Ollama(id="llama3.2"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.2
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ollama sqlalchemy pgvector pypdf agno
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
 python cookbook/models/ollama/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/ollama/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Set Ollama Client
Source: https://docs.agno.com/examples/models/ollama/set_client

## Code

```python cookbook/models/ollama/set_client.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.ollama import Ollama
from agno.tools.yfinance import YFinanceTools
from ollama import Client as OllamaClient

agent = Agent(
 model=Ollama(id="llama3.2", client=OllamaClient()),
 tools=[YFinanceTools(stock_price=True)],
 markdown=True,
)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.2
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ollama yfinance agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ollama/set_client.py
 ```

 ```bash Windows
 python cookbook/models/ollama/set_client.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/ollama/storage

## Code

```python cookbook/models/ollama/storage.py
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=Ollama(id="llama3.1:8b"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.1:8b
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ollama sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/ollama/storage.py
 ```

 ```bash Windows
 python cookbook/models/ollama/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/ollama/structured_output

## Code

```python cookbook/models/ollama/structured_output.py
import asyncio
from typing import List

from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field

class MovieScript(BaseModel):
 name: str = Field(..., description="Give a name to this movie")
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
 characters: List[str] = Field(..., description="Name of characters for this movie.")
 storyline: str = Field(
 ..., description="3 sentence storyline for the movie. Make it exciting!"
 )

# Agent that returns a structured output
structured_output_agent = Agent(
 model=Ollama(id="llama3.2"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

# Run the agent synchronously
structured_output_agent.print_response("Llamas ruling the world")

# Run the agent asynchronously
async def run_agents_async():
 await structured_output_agent.aprint_response("Llamas ruling the world")

asyncio.run(run_agents_async())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.2
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
 python cookbook/models/ollama/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/ollama/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/ollama/tool_use

## Code

```python cookbook/models/ollama/tool_use.py
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Ollama(id="llama3.1:8b"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install Ollama">
 Follow the [installation guide](https://github.com/ollama/ollama?tab=readme-ov-file#macos) and run:

 ```bash
 ollama pull llama3.1:8b
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U ollama duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/ollama/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/ollama/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Input Agent
Source: https://docs.agno.com/examples/models/openai/chat/audio_input_agent

## Code

```python cookbook/models/openai/chat/audio_input_agent.py
import requests
from agno.agent import Agent, RunResponse # noqa
from agno.media import Audio
from agno.models.openai import OpenAIChat

# Fetch the audio file and convert it to a base64 encoded string
url = "https://openaiassets.blob.core.windows.net/$web/API/docs/audio/alloy.wav"
response = requests.get(url)
response.raise_for_status()
wav_data = response.content

# Provide the agent with the audio file and get result as text
agent = Agent(
 model=OpenAIChat(id="gpt-4o-audio-preview", modalities=["text"]),
 markdown=True,
)
agent.print_response(
 "What is in this audio?", audio=[Audio(content=wav_data, format="wav")]
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
 pip install -U openai requests agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/openai/chat/audio_input_agent.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/audio_input_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Audio Output Agent
Source: https://docs.agno.com/examples/models/openai/chat/audio_output_agent

## Code

```python cookbook/models/openai/chat/audio_output_agent.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIChat
from agno.utils.audio import write_audio_to_file

# Provide the agent with the audio file and audio configuration and get result as text + audio
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
 python cookbook/models/openai/chat/audio_output_agent.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/audio_output_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/openai/chat/basic

## Code

```python cookbook/models/openai/chat/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIChat

agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")

agent.run_response.metrics
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
 python cookbook/models/openai/chat/basic.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/openai/chat/basic_stream

## Code

```python cookbook/models/openai/chat/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIChat

agent = Agent(model=OpenAIChat(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/openai/chat/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Generate Images
Source: https://docs.agno.com/examples/models/openai/chat/generate_images

## Code

```python cookbook/models/openai/chat/generate_images.py
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
 python cookbook/models/openai/chat/generate_images.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/generate_images.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/openai/chat/image_agent

## Code

```python cookbook/models/openai/chat/image_agent.py
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
 url="https://upload.wikimedia.org/wikipedia/commons/b/bf/Krakow_-_Kosciol_Mariacki.jpg"
 )
 ],
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
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/openai/chat/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/openai/chat/knowledge

## Code

```python cookbook/models/openai/chat/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 knowledge=knowledge_base,
 use_tools=True,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
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
 pip install -U openai sqlalchemy pgvector pypdf agno
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
 python cookbook/models/openai/chat/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Reasoning Effort
Source: https://docs.agno.com/examples/models/openai/chat/reasoning_effort

## Code

```python cookbook/reasoning/models/openai/reasoning_effort.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.yfinance import YFinanceTools

agent = Agent(
 model=OpenAIChat(id="o3-mini", reasoning_effort="high"),
 tools=[YFinanceTools(enable_all=True)],
 show_tool_calls=True,
 markdown=True,
)

agent.print_response("Write a report on the NVDA, is it a good buy?", stream=True)
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
 pip install -U openai yfinance agno
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

# Agent with Storage
Source: https://docs.agno.com/examples/models/openai/chat/storage

## Code

```python cookbook/models/openai/chat/storage.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
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
 pip install -U openai sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/openai/chat/storage.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/openai/chat/structured_output

## Code

```python cookbook/models/openai/chat/structured_output.py
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

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)
# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)

json_mode_agent.print_response("New York")
structured_output_agent.print_response("New York")
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
 python cookbook/models/openai/chat/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/openai/chat/tool_use

## Code

```python cookbook/models/openai/chat/tool_use.py
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/openai/chat/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/openai/chat/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/openai/responses/basic

## Code

```python cookbook/models/openai/responses/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIResponses

agent = Agent(model=OpenAIResponses(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")

agent.run_response.metrics
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
 python cookbook/models/openai/responses/basic.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/openai/responses/basic_stream

## Code

```python cookbook/models/openai/responses/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIResponses

agent = Agent(model=OpenAIResponses(id="gpt-4o"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/openai/responses/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent
Source: https://docs.agno.com/examples/models/openai/responses/image_agent

## Code

```python cookbook/models/openai/responses/image_agent.py
from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIResponses
from agno.tools.googlesearch import GoogleSearchTools

agent = Agent(
 model=OpenAIResponses(id="gpt-4o"),
 tools=[GoogleSearchTools()],
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
 pip install -U openai agno googlesearch-python
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/openai/responses/image_agent.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Image Agent (Bytes Content)
Source: https://docs.agno.com/examples/models/openai/responses/image_agent_bytes

## Code

```python cookbook/models/openai/responses/image_agent_bytes.py
from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIResponses
from agno.tools.googlesearch import GoogleSearchTools
from agno.utils.media import download_image

agent = Agent(
 model=OpenAIResponses(id="gpt-4o"),
 tools=[GoogleSearchTools()],
 markdown=True,
)

image_path = Path(__file__).parent.joinpath("sample.jpg")

download_image(
 url="https://upload.wikimedia.org/wikipedia/commons/0/0c/GoldenGateBridge-001.jpg",
 output_path=str(image_path),
)

# Read the image file content as bytes
image_bytes = image_path.read_bytes()

agent.print_response(
 "Tell me about this image and give me the latest news about it.",
 images=[
 Image(content=image_bytes),
 ],
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
 pip install -U openai agno googlesearch-python
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/openai/responses/image_agent_bytes.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/image_agent.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Knowledge
Source: https://docs.agno.com/examples/models/openai/responses/knowledge

## Code

```python cookbook/models/openai/responses/knowledge.py
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.openai import OpenAIResponses
from agno.vectordb.pgvector import PgVector

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

knowledge_base = PDFUrlKnowledgeBase(
 urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
 vector_db=PgVector(table_name="recipes", db_url=db_url),
)
knowledge_base.load(recreate=True) # Comment out after first run

agent = Agent(
 model=OpenAIResponses(id="gpt-4o"),
 knowledge=knowledge_base,
 show_tool_calls=True,
)
agent.print_response("How to make Thai curry?", markdown=True)
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
 pip install -U openai sqlalchemy pgvector pypdf agno
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
 python cookbook/models/openai/responses/knowledge.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/knowledge.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with PDF Input (Local File)
Source: https://docs.agno.com/examples/models/openai/responses/pdf_input_local

## Code

```python cookbook/models/openai/responses/pdf_input_local.py
from pathlib import Path

from agno.agent import Agent
from agno.media import File
from agno.models.openai.responses import OpenAIResponses
from agno.utils.media import download_file

pdf_path = Path(__file__).parent.joinpath("ThaiRecipes.pdf")

# Download the file using the download_file function
download_file(
 "https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf", str(pdf_path)
)

agent = Agent(
 model=OpenAIResponses(id="gpt-4o-mini"),
 tools=[{"type": "file_search"}],
 markdown=True,
 add_history_to_messages=True,
)

agent.print_response(
 "Summarize the contents of the attached file.",
 files=[File(filepath=pdf_path)],
)
agent.print_response("Suggest me a recipe from the attached file.")
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
 python cookbook/models/openai/responses/pdf_input_local.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/pdf_input_local.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with PDF Input (URL)
Source: https://docs.agno.com/examples/models/openai/responses/pdf_input_url

## Code

```python cookbook/models/openai/responses/pdf_input_url.py
from agno.agent import Agent
from agno.media import File
from agno.models.openai.responses import OpenAIResponses

agent = Agent(
 model=OpenAIResponses(id="gpt-4o-mini"),
 tools=[{"type": "file_search"}, {"type": "web_search_preview"}],
 markdown=True,
)

agent.print_response(
 "Summarize the contents of the attached file and search the web for more information.",
 files=[File(url="https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf")],
)

print("Citations:")
print(agent.run_response.citations)
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
 python cookbook/models/openai/responses/pdf_input_url.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/pdf_input_url.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Storage
Source: https://docs.agno.com/examples/models/openai/responses/storage

## Code

```python cookbook/models/openai/responses/storage.py
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.storage.postgres import PostgresStorage
from agno.tools.duckduckgo import DuckDuckGoTools

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

agent = Agent(
 model=OpenAIResponses(id="gpt-4o"),
 storage=PostgresStorage(table_name="agent_sessions", db_url=db_url),
 tools=[DuckDuckGoTools()],
 add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
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
 pip install -U openai sqlalchemy psycopg duckduckgo-search agno
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
 python cookbook/models/openai/responses/storage.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/storage.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/openai/responses/structured_output

## Code

```python cookbook/models/openai/responses/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.openai import OpenAIResponses
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
 model=OpenAIResponses(id="gpt-4o"),
 description="You write movie scripts.",
 response_model=MovieScript,
 use_json_mode=True,
)

# Agent that uses structured outputs
structured_output_agent = Agent(
 model=OpenAIResponses(id="gpt-4o"), 
 description="You write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)
# structured_output_response: RunResponse = structured_output_agent.run("New York")
# pprint(structured_output_response.content)

json_mode_agent.print_response("New York")
structured_output_agent.print_response("New York")
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
 python cookbook/models/openai/responses/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/openai/responses/tool_use

## Code

```python cookbook/models/openai/responses/tool_use.py
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=OpenAIResponses(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/openai/responses/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/openai/responses/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/perplexity/basic

## Code

```python cookbook/models/perplexity/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.perplexity import Perplexity

agent = Agent(model=Perplexity(id="sonar-pro"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export PERPLEXITY_API_KEY=xxx
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
 python cookbook/models/perplexity/basic.py
 ```

 ```bash Windows
 python cookbook/models/perplexity/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/perplexity/basic_stream

## Code

```python cookbook/models/perplexity/basic_stream.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.perplexity import Perplexity

agent = Agent(model=Perplexity(id="sonar-pro"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export PERPLEXITY_API_KEY=xxx
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
 python cookbook/models/perplexity/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/perplexity/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/together/basic

## Code

```python cookbook/models/together/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.together import Together

agent = Agent(
 model=Together(id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"), markdown=True
)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export TOGETHER_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U together openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/together/basic.py
 ```

 ```bash Windows
 python cookbook/models/together/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/together/basic_stream

## Code

```python cookbook/models/together/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.together import Together

agent = Agent(
 model=Together(id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"), markdown=True
)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export TOGETHER_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U together openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/together/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/together/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Structured Outputs
Source: https://docs.agno.com/examples/models/together/structured_output

## Code

```python cookbook/models/together/structured_output.py
from typing import List

from agno.agent import Agent, RunResponse # noqa
from agno.models.together import Together
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
 model=Together(id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
 description="You write movie scripts.",
 response_model=MovieScript,
)

# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.run("New York")
# pprint(json_mode_response.content)

json_mode_agent.print_response("New York")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export TOGETHER_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U together openai agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/together/structured_output.py
 ```

 ```bash Windows
 python cookbook/models/together/structured_output.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/together/tool_use

## Code

```python cookbook/models/together/tool_use.py
from agno.agent import Agent
from agno.models.together import Together
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=Together(id="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export TOGETHER_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U together openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/together/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/together/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/vercel/basic

## Code

```python cookbook/models/vercel/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.vercel import v0

agent = Agent(model=v0(id="v0-1.0-md"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export V0_API_KEY=xxx
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
 python cookbook/models/vercel/basic.py
 ```

 ```bash Windows
 python cookbook/models/vercel/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/vercel/basic_stream

## Code

```python cookbook/models/vercel/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.vercel import v0

agent = Agent(model=v0(id="v0-1.0-md"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export V0_API_KEY=xxx
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
 python cookbook/models/vercel/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/vercel/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/vercel/tool_use

## Code

```python cookbook/models/vercel/tool_use.py
from agno.agent import Agent
from agno.models.vercel import v0
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=v0(id="v0-1.0-md"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Set your API key">
 ```bash
 export V0_API_KEY=xxx
 ```
 </Step>

 <Step title="Install libraries">
 ```bash
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/vercel/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/vercel/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Basic Agent
Source: https://docs.agno.com/examples/models/xai/basic

## Code

```python cookbook/models/xai/basic.py
from agno.agent import Agent, RunResponse # noqa
from agno.models.xai import xAI

agent = Agent(model=xAI(id="grok-beta"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
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
 python cookbook/models/xai/basic.py
 ```

 ```bash Windows
 python cookbook/models/xai/basic.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Streaming Agent
Source: https://docs.agno.com/examples/models/xai/basic_stream

## Code

```python cookbook/models/xai/basic_stream.py
from typing import Iterator # noqa
from agno.agent import Agent, RunResponse # noqa
from agno.models.xai import xAI

agent = Agent(model=xAI(id="grok-beta"), markdown=True)

# Get the response in a variable
# run_response: Iterator[RunResponse] = agent.run("Share a 2 sentence horror story", stream=True)
# for chunk in run_response:
# print(chunk.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story", stream=True)
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
 python cookbook/models/xai/basic_stream.py
 ```

 ```bash Windows
 python cookbook/models/xai/basic_stream.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agent with Tools
Source: https://docs.agno.com/examples/models/xai/tool_use

## Code

```python cookbook/models/xai/tool_use.py
from agno.agent import Agent
from agno.models.xai import xAI
from agno.tools.duckduckgo import DuckDuckGoTools

agent = Agent(
 model=xAI(id="grok-beta"),
 tools=[DuckDuckGoTools()],
 show_tool_calls=True,
 markdown=True,
)
agent.print_response("Whats happening in France?", stream=True)
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
 pip install -U openai duckduckgo-search agno
 ```
 </Step>

 <Step title="Run Agent">
 <CodeGroup>
 ```bash Mac
 python cookbook/models/xai/tool_use.py
 ```

 ```bash Windows
 python cookbook/models/xai/tool_use.py
 ```
 </CodeGroup>
 </Step>
</Steps>

# Agentic RAG
Source: https://docs.agno.com/examples/streamlit/agentic-rag

This example application shows how to build a sophisticated RAG (Retrieval Augmented Generation) system that leverages search of a knowledge base with LLMs to provide deep insights into the data.

## The agent can:

* Process and understand documents from multiple sources (PDFs, websites, text files)
* Build a searchable knowledge base using vector embeddings
* Maintain conversation context and memory across sessions
* Provide relevant citations and sources for its responses
* Generate summaries and extract key insights
* Answer follow-up questions and clarifications

## The agent uses:

* Vector similarity search for relevant document retrieval
* Conversation memory for contextual responses
* Citation tracking for source attribution
* Dynamic knowledge base updates

<video autoPlay muted controls className="w-full aspect-video" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/videos/agentic_rag.mp4" />

## Example queries to try:

* "What are the key points from this document?"
* "Can you summarize the main arguments and supporting evidence?"
* "What are the important statistics and findings?"
* "How does this relate to \[topic X]?"
* "What are the limitations or gaps in this analysis?"
* "Can you explain \[concept X] in more detail?"
* "What other sources support or contradict these claims?"

## Code

The complete code is available in the [Agno repository](https://github.com/agno-agi/agno).

## Usage

<Steps>
 <Step title="Clone the repository">
 ```bash
 git clone https://github.com/agno-agi/agno.git
 cd agno
 ```
 </Step>

 <Step title="Create virtual environment">
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```
 </Step>

 <Step title="Install dependencies">
 ```bash
 pip install -r cookbook/examples/streamlit_apps/agentic_rag/requirements.txt
 ```
 </Step>

 <Step title="Run PgVector">
 First, install [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/).

 Then run either using the helper script:

 ```bash
 ./cookbook/scripts/run_pgvector.sh
 ```

 Or directly with Docker:

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

 <Step title="Set up API keys">
 ```bash
 # Required
 export OPENAI_API_KEY=***
 # Optional
 export ANTHROPIC_API_KEY=***
 export GOOGLE_API_KEY=***

 ```

 We recommend using gpt-4o for optimal performance.
 </Step>

 <Step title="Launch the app">
 ```bash
 streamlit run cookbook/examples/streamlit_apps/agentic_rag/app.py
 ```

 Open [localhost:8501](http://localhost:8501) to start using the Agentic RAG.
 </Step>
</Steps>

Need help? Join our [Discourse community](https://community.agno.com) for support!

# Sage: Answer Engine
Source: https://docs.agno.com/examples/streamlit/answer-engine

This example shows how to build Sage, a Perplexity-like Answer Engine that intelligently determines whether to perform a web search or conduct a deep analysis using ExaTools based on the user's query.

Sage:

1. Uses real-time web search (DuckDuckGo) and deep contextual analysis (ExaTools) to provide comprehensive answers
2. Intelligently selects tools based on query complexity
3. Provides an interactive Streamlit UI with session management and chat history export
4. Supports multiple LLM providers (OpenAI, Anthropic, Google, Groq)

## Key capabilities

* Natural language query understanding and processing
* Real-time web search integration with DuckDuckGo
* Deep contextual analysis using ExaTools
* Multiple LLM provider support
* Session management using SQLite
* Chat history export
* Interactive Streamlit UI

<video autoPlay muted controls className="w-full aspect-video" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/videos/answer-engine.mp4" />

## Simple queries to try

* "Tell me about the tariffs the US is imposing in 2025"
* "Which is a better reasoning model: o3-mini or DeepSeek R1?"
* "Tell me about Agno"
* "What are the latest trends in renewable energy?"

## Advanced analysis queries

* "Evaluate how emerging AI regulations could influence innovation"
* "Compare the environmental impact of electric vs hydrogen vehicles"
* "Analyze the global semiconductor supply chain challenges"
* "Explain the implications of quantum computing on cryptography"

## Code

The complete code is available in the [Agno repository](https://github.com/agno-agi/agno).

## Usage

<Steps>
 <Step title="Clone the repository">
 ```bash
 git clone https://github.com/agno-agi/agno.git
 cd agno
 ```
 </Step>

 <Step title="Create virtual environment">
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate # On Windows: .venv\Scripts\activate
 ```
 </Step>

 <Step title="Install dependencies">
 ```bash
 pip install -r cookbook/examples/streamlit_apps/answer_engine/requirements.txt
 ```
 </Step>

 <Step title="Set up API keys">
 ```bash
 # Required
 export OPENAI_API_KEY=***
 export EXA_API_KEY=***

 # Optional (for additional models)
 export ANTHROPIC_API_KEY=***
 export GOOGLE_API_KEY=***
 export GROQ_API_KEY=***
 ```

 We recommend using gpt-4o for optimal performance.
 </Step>

 <Step title="Launch the app">
 ```bash
 streamlit run cookbook/examples/streamlit_apps/answer_engine/app.py
 ```

 Open [localhost:8501](http://localhost:8501) to start using Sage.
 </Step>
</Steps>

## Model Selection

The application supports multiple model providers:

* OpenAI (o3-mini, gpt-4o)
* Anthropic (claude-3-5-sonnet)
* Google (gemini-2.0-flash-exp)
* Groq (llama-3.3-70b-versatile)

## Agent Configuration

The agent configuration is in `agents.py` and the prompts are in `prompts.py`:

* To modify prompts, update the `prompts.py` file
* To add new tools or models, update the `agents.py` file

## Support

Need help? Join our [Discourse community](https://community.agno.com) for support!

# Chess Battle
Source: https://docs.agno.com/examples/streamlit/chess-team

Chess Battle is a chess application where multiple AI agents collaborate to play chess against each other, demonstrating the power of multi-agent systems in complex game environments.

### Key Capabilities

* Multi-Agent System: Features White and Black Piece Agents for move selection
* Move Validation: Dedicated Legal Move Agent ensures game rule compliance
* Game Coordination: Master Agent oversees the game flow and end conditions
* Interactive UI: Built with Streamlit for real-time game visualization

<video autoPlay muted controls className="w-full aspect-video" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/videos/chess-team.mp4" />

### System Components

* White Piece Agent: Strategizes and selects moves for white pieces
* Black Piece Agent: Controls and determines moves for black pieces
* Legal Move Agent: Validates all proposed moves against chess rules
* Master Agent: Coordinates the game flow and monitors game status

### Advanced Features

The system demonstrates complex agent interactions where each AI component has a specific role. The agents communicate and coordinate to create a complete chess-playing experience, showcasing how multiple specialized AIs can work together effectively.

### Code

The complete code is available in the [Agno repository](https://github.com/agno-agi/agno/tree/main/cookbook/examples/streamlit_apps/chess_team).

### Usage

<Steps>
 <Step title="Clone the repository">
 ```bash
 git clone https://github.com/agno-agi/agno.git
 cd agno
 ```
 </Step>

 <Step title="Create a Virtual Environment">
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate # On Windows use: .venv\Scripts\activate
 ```
 </Step>

 <Step title="Install Dependencies">
 ```bash
 pip install -r cookbook/examples/streamlit_apps/chess_team/requirements.txt
 ```
 </Step>

 <Step title="Set up API Key">
 The Chess Team Agent uses the Anthropic API for agent reasoning:

 ```bash
 export ANTHROPIC_API_KEY=your_api_key_here
 ```
 </Step>

 <Step title="Launch the App">
 ```bash
 streamlit run cookbook/examples/streamlit_apps/chess_team/app.py
 ```
 </Step>

 <Step title="Open the App">
 Then, open [http://localhost:8501](http://localhost:8501) in your browser to start watching the AI agents play chess.
 </Step>
</Steps>

### Pro Tips

* Watch Complete Games: Observe full matches to understand agent decision-making
* Monitor Agent Interactions: Pay attention to how agents communicate and coordinate

Need help? Join our [Discourse community](https://agno.link/community) for support!

# Game Generator
Source: https://docs.agno.com/examples/streamlit/game-generator

**GameGenerator** generates HTML5 games based on user descriptions.

Create a file `game_generator.py` with the following code:

```python game_generator.py
import json
from pathlib import Path
from typing import Iterator

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.run.response import RunEvent
from agno.storage.workflow.sqlite import SqliteWorkflowStorage
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.utils.string import hash_string_sha256
from agno.utils.web import open_html_file
from agno.workflow import Workflow
from pydantic import BaseModel, Field

games_dir = Path(__file__).parent.joinpath("games")
games_dir.mkdir(parents=True, exist_ok=True)
game_output_path = games_dir / "game_output_file.html"
game_output_path.unlink(missing_ok=True)

class GameOutput(BaseModel):
 reasoning: str = Field(..., description="Explain your reasoning")
 code: str = Field(..., description="The html5 code for the game")
 instructions: str = Field(..., description="Instructions how to play the game")

class QAOutput(BaseModel):
 reasoning: str = Field(..., description="Explain your reasoning")
 correct: bool = Field(False, description="Does the game pass your criteria?")

class GameGenerator(Workflow):
 # This description is only used in the workflow UI
 description: str = "Generator for single-page HTML5 games"

 game_developer: Agent = Agent(
 name="Game Developer Agent",
 description="You are a game developer that produces working HTML5 code.",
 model=OpenAIChat(id="gpt-4o"),
 instructions=[
 "Create a game based on the user's prompt. "
 "The game should be HTML5, completely self-contained and must be runnable simply by opening on a browser",
 "Ensure the game has a alert that pops up if the user dies and then allows the user to restart or exit the game.",
 "Ensure instructions for the game are displayed on the HTML page."
 "Use user-friendly colours and make the game canvas large enough for the game to be playable on a larger screen.",
 ],
 response_model=GameOutput,
 )

 qa_agent: Agent = Agent(
 name="QA Agent",
 model=OpenAIChat(id="gpt-4o"),
 description="You are a game QA and you evaluate html5 code for correctness.",
 instructions=[
 "You will be given some HTML5 code."
 "Your task is to read the code and evaluate it for correctness, but also that it matches the original task description.",
 ],
 response_model=QAOutput,
 )

 def run(self, game_description: str) -> Iterator[RunResponse]:
 logger.info(f"Game description: {game_description}")

 game_output = self.game_developer.run(game_description)

 if (
 game_output
 and game_output.content
 and isinstance(game_output.content, GameOutput)
 ):
 game_code = game_output.content.code
 logger.info(f"Game code: {game_code}")
 else:
 yield RunResponse(
 run_id=self.run_id,
 event=RunEvent.workflow_completed,
 content="Sorry, could not generate a game.",
 )
 return

 logger.info("QA'ing the game code")
 qa_input = {
 "game_description": game_description,
 "game_code": game_code,
 }
 qa_output = self.qa_agent.run(json.dumps(qa_input, indent=2))

 if qa_output and qa_output.content and isinstance(qa_output.content, QAOutput):
 logger.info(qa_output.content)
 if not qa_output.content.correct:
 raise Exception(f"QA failed for code: {game_code}")

 # Store the resulting code
 game_output_path.write_text(game_code)

 yield RunResponse(
 run_id=self.run_id,
 event=RunEvent.workflow_completed,
 content=game_output.content.instructions,
 )
 else:
 yield RunResponse(
 run_id=self.run_id,
 event=RunEvent.workflow_completed,
 content="Sorry, could not QA the game.",
 )
 return

# Run the workflow if the script is executed directly
if __name__ == "__main__":
 from rich.prompt import Prompt

 game_description = Prompt.ask(
 "[bold]Describe the game you want to make (keep it simple)[/bold]\n✨",
 # default="An asteroids game."
 default="An asteroids game. Make sure the asteroids move randomly and are random sizes. They should continually spawn more and become more difficult over time. Keep score. Make my spaceship's movement realistic.",
 )

 hash_of_description = hash_string_sha256(game_description)

 # Initialize the investment analyst workflow
 game_generator = GameGenerator(
 session_id=f"game-gen-{hash_of_description}",
 storage=SqliteWorkflowStorage(
 table_name="game_generator_workflows",
 db_file="tmp/workflows.db",
 ),
 )

 # Execute the workflow
 result: Iterator[RunResponse] = game_generator.run(
 game_description=game_description
 )

 # Print the report
 pprint_run_response(result)

 if game_output_path.exists():
 open_html_file(game_output_path)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install openai agno
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python game_generator.py.py
 ```
 </Step>
</Steps>

# GeoBuddy
Source: https://docs.agno.com/examples/streamlit/geobuddy

GeoBuddy is a geography agent that analyzes images to predict locations based on visible cues such as landmarks, architecture, and cultural symbols.

### Key Capabilities

* Location Identification: Predicts location details from uploaded images
* Detailed Reasoning: Explains predictions based on visual cues
* User-Friendly Ul: Built with Streamlit for an intuitive experience

<video autoPlay muted controls className="w-full aspect-video" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/videos/geobuddy.mp4" />

### Simple Examples to Try

* Landscape: A city skyline, a mountain panorama, or a famous landmark
* Architecture: Distinct buildings, bridges, or unique cityscapes
* Cultural Clues: Text on signboards, language hints, flags, or unique clothing

### Advanced Usage

Try providing images with subtle details, like store signs in different languages or iconic but less globally famous landmarks. GeoBuddy will attempt to reason more deeply about architectural style, environment (e.g. desert vs. tropical), and cultural references.

### Code

The complete code is available in the [Agno repository](https://github.com/agno-agi/agno).

### Usage

<Steps>
 <Step title="Clone the repository">
 ```bash
 git clone https://github.com/agno-agi/agno.git
 cd agno
 ```
 </Step>

 <Step title="Create a Virtual Environment">
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```
 </Step>

 <Step title="Install Dependencies">
 ```bash
 pip install -r cookbook/examples/streamlit_apps/geobuddy/requirements.txt
 ```
 </Step>

 <Step title="Set up API Key">
 GeoBuddy uses the Google PaLM API for advanced image reasoning:

 ```bash
 export GOOGLE_API_KEY=***
 ```
 </Step>

 <Step title="Launch the App">
 ```bash
 streamlit run cookbook/examples/streamlit_apps/geobuddy/app.py
 ```
 </Step>

 <Step title="Open the App">
 Then, open [http://localhost:8501](http://localhost:8501) in your browser to start using GeoBuddy.
 </Step>
</Steps>

### Pro Tips

* High-Resolution Images: Clearer images with visible signboards or landmarks improve accuracy.
* Variety of Angles: Different angles (e.g. street-level vs. aerial views) can showcase unique clues.
* Contextual Clues: Sometimes minor details like license plates, local architectural elements or even vegetation can significantly influence the location guess.

Need help? Join our [Discourse community](https://community.agno.com) for support!

# SQL Agent
Source: https://docs.agno.com/examples/streamlit/text-to-sql

This example shows how to build a text-to-SQL system that:

1. Uses Agentic RAG to search for table metadata, sample queries and rules for writing better SQL queries.
2. Uses dynamic few-shot examples and rules to improve query construction.
3. Provides an interactive Streamlit UI for users to query the database.

We'll use the F1 dataset as an example, but you can easily extend it to other datasets.

### Key capabilities

* Natural language to SQL conversion
* Retrieve table metadata, sample queries and rules using Agentic RAG
* Better query construction with the help of dynamic few-shot examples and rules
* Interactive Streamlit UI

<video autoPlay muted controls className="w-full aspect-video" src="https://mintlify.s3.us-west-1.amazonaws.com/agno/videos/sql_agent.mp4" />

### Simple queries to try

* "Who are the top 5 drivers with the most race wins?"
* "Compare Mercedes vs Ferrari performance in constructors championships"
* "Show me the progression of fastest lap times at Monza"
* "Which drivers have won championships with multiple teams?"
* "What tracks have hosted the most races?"
* "Show me Lewis Hamilton's win percentage by season"

### Advanced queries with table joins

* "How many races did the championship winners win each year?"
* "Compare the number of race wins vs championship positions for constructors in 2019"
* "Show me Lewis Hamilton's race wins and championship positions by year"
* "Which drivers have both won races and set fastest laps at Monaco?"
* "Show me Ferrari's race wins and constructor championship positions from 2015-2020"

## Code

The complete code is available in the [Agno repository](https://github.com/agno-agi/agno).

## Usage

<Steps>
 <Step title="Clone the repository">
 ```bash
 git clone https://github.com/agno-agi/agno.git
 cd agno
 ```
 </Step>

 <Step title="Create virtual environment">
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```
 </Step>

 <Step title="Install dependencies">
 ```bash
 pip install -r cookbook/examples/streamlit_apps/sql_agent/requirements.txt
 ```
 </Step>

 <Step title="Run PgVector">
 First, install [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/).

 Then run either using the helper script:

 ```bash
 ./cookbook/scripts/run_pgvector.sh
 ```

 Or directly with Docker:

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

 <Step title="Load F1 data">
 ```bash
 python cookbook/examples/streamlit_apps/sql_agent/load_f1_data.py
 ```
 </Step>

 <Step title="Load knowledge base">
 The knowledge base contains table metadata, rules and sample queries that help the Agent generate better responses.

 ```bash
 python cookbook/examples/streamlit_apps/sql_agent/load_knowledge.py
 ```

 Pro tips for enhancing the knowledge base:

 * Add `table_rules` and `column_rules` to guide the Agent on query formats
 * Add sample queries to `cookbook/examples/apps/sql_agent/knowledge_base/sample_queries.sql`
 </Step>

 <Step title="Set up API keys">
 ```bash
 # Required
 export OPENAI_API_KEY=***

 # Optional
 export ANTHROPIC_API_KEY=***
 export GOOGLE_API_KEY=***
 export GROQ_API_KEY=***
 ```

 We recommend using gpt-4o for optimal performance.
 </Step>

 <Step title="Launch the app">
 ```bash
 streamlit run cookbook/examples/streamlit_apps/sql_agent/app.py
 ```

 Open [localhost:8501](http://localhost:8501) to start using the SQL Agent.
 </Step>
</Steps>

Need help? Join our [Discourse community](https://community.agno.com) for support!

# Discussion Team
Source: https://docs.agno.com/examples/teams/collaborate/discussion_team

This example shows how to create a discussion team that allows multiple agents to collaborate on a topic.

## Code

```python discussion_team.py
import asyncio
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools

reddit_researcher = Agent(
 name="Reddit Researcher",
 role="Research a topic on Reddit",
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools()],
 add_name_to_instructions=True,
 instructions=dedent("""
 You are a Reddit researcher.
 You will be given a topic to research on Reddit.
 You will need to find the most relevant posts on Reddit.
 """),
)

hackernews_researcher = Agent(
 name="HackerNews Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Research a topic on HackerNews.",
 tools=[HackerNewsTools()],
 add_name_to_instructions=True,
 instructions=dedent("""
 You are a HackerNews researcher.
 You will be given a topic to research on HackerNews.
 You will need to find the most relevant posts on HackerNews.
 """),
)

academic_paper_researcher = Agent(
 name="Academic Paper Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Research academic papers and scholarly content",
 tools=[GoogleSearchTools(), ArxivTools()],
 add_name_to_instructions=True,
 instructions=dedent("""
 You are a academic paper researcher.
 You will be given a topic to research in academic literature.
 You will need to find relevant scholarly articles, papers, and academic discussions.
 Focus on peer-reviewed content and citations from reputable sources.
 Provide brief summaries of key findings and methodologies.
 """),
)

twitter_researcher = Agent(
 name="Twitter Researcher",
 model=OpenAIChat("gpt-4o"),
 role="Research trending discussions and real-time updates",
 tools=[DuckDuckGoTools()],
 add_name_to_instructions=True,
 instructions=dedent("""
 You are a Twitter/X researcher.
 You will be given a topic to research on Twitter/X.
 You will need to find trending discussions, influential voices, and real-time updates.
 Focus on verified accounts and credible sources when possible.
 Track relevant hashtags and ongoing conversations.
 """),
)

agent_team = Team(
 name="Discussion Team",
 mode="collaborate",
 model=OpenAIChat("gpt-4o"),
 members=[
 reddit_researcher,
 hackernews_researcher,
 academic_paper_researcher,
 twitter_researcher,
 ],
 instructions=[
 "You are a discussion master.",
 "You have to stop the discussion when you think the team has reached a consensus.",
 ],
 success_criteria="The team has reached a consensus.",
 enable_agentic_context=True,
 update_team_context=True,
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

if __name__ == "__main__":
 asyncio.run(
 agent_team.print_response(
 message="Start the discussion on the topic: 'What is the best way to learn to code?'",
 stream=True,
 stream_intermediate_steps=True,
 )
 )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai duckduckgo-search arxiv pypdf googlesearch-python pycountry 
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python discussion_team.py
 ```
 </Step>
</Steps>

# Autonomous Startup Team
Source: https://docs.agno.com/examples/teams/coordinate/autonomous_startup_team

This example shows how to create an autonomous startup team that can self-organize and drive innovative projects.

## Code

```python autonomous_startup_team.py
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.slack import SlackTools
from agno.tools.yfinance import YFinanceTools
from agno.vectordb.pgvector.pgvector import PgVector

knowledge_base = PDFKnowledgeBase(
 path="tmp/data",
 vector_db=PgVector(
 table_name="autonomous_startup_team",
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 ),
 reader=PDFReader(chunk=True),
)

knowledge_base.load(recreate=False)

support_channel = "testing"
sales_channel = "sales"

legal_compliance_agent = Agent(
 name="Legal Compliance Agent",
 role="Legal Compliance",
 model=OpenAIChat("gpt-4o"),
 tools=[ExaTools()],
 knowledge=knowledge_base,
 instructions=[
 "You are the Legal Compliance Agent of a startup, responsible for ensuring legal and regulatory compliance.",
 "Key Responsibilities:",
 "1. Review and validate all legal documents and contracts",
 "2. Monitor regulatory changes and update compliance policies",
 "3. Assess legal risks in business operations and product development",
 "4. Ensure data privacy and security compliance (GDPR, CCPA, etc.)",
 "5. Provide legal guidance on intellectual property protection",
 "6. Create and maintain compliance documentation",
 "7. Review marketing materials for legal compliance",
 "8. Advise on employment law and HR policies",
 ],
 add_datetime_to_instructions=True,
 markdown=True,
)

product_manager_agent = Agent(
 name="Product Manager Agent",
 role="Product Manager",
 model=OpenAIChat("gpt-4o"),
 knowledge=knowledge_base,
 instructions=[
 "You are the Product Manager of a startup, responsible for product strategy and execution.",
 "Key Responsibilities:",
 "1. Define and maintain the product roadmap",
 "2. Gather and analyze user feedback to identify needs",
 "3. Write detailed product requirements and specifications",
 "4. Prioritize features based on business impact and user value",
 "5. Collaborate with technical teams on implementation feasibility",
 "6. Monitor product metrics and KPIs",
 "7. Conduct competitive analysis",
 "8. Lead product launches and go-to-market strategies",
 "9. Balance user needs with business objectives",
 ],
 add_datetime_to_instructions=True,
 markdown=True,
 tools=[],
)

market_research_agent = Agent(
 name="Market Research Agent",
 role="Market Research",
 model=OpenAIChat("gpt-4o"),
 tools=[DuckDuckGoTools(), ExaTools()],
 knowledge=knowledge_base,
 instructions=[
 "You are the Market Research Agent of a startup, responsible for market intelligence and analysis.",
 "Key Responsibilities:",
 "1. Conduct comprehensive market analysis and size estimation",
 "2. Track and analyze competitor strategies and offerings",
 "3. Identify market trends and emerging opportunities",
 "4. Research customer segments and buyer personas",
 "5. Analyze pricing strategies in the market",
 "6. Monitor industry news and developments",
 "7. Create detailed market research reports",
 "8. Provide data-driven insights for decision making",
 ],
 add_datetime_to_instructions=True,
 markdown=True,
)

sales_agent = Agent(
 name="Sales Agent",
 role="Sales",
 model=OpenAIChat("gpt-4o"),
 tools=[SlackTools()],
 knowledge=knowledge_base,
 instructions=[
 "You are the Sales & Partnerships Agent of a startup, responsible for driving revenue growth and strategic partnerships.",
 "Key Responsibilities:",
 "1. Identify and qualify potential partnership and business opportunities",
 "2. Evaluate partnership proposals and negotiate terms",
 "3. Maintain relationships with existing partners and clients",
 "5. Collaborate with Legal Compliance Agent on contract reviews",
 "6. Work with Product Manager on feature requests from partners",
 f"7. Document and communicate all partnership details in #{sales_channel} channel",
 "",
 "Communication Guidelines:",
 "1. Always respond professionally and promptly to partnership inquiries",
 "2. Include all relevant details when sharing partnership opportunities",
 "3. Highlight potential risks and benefits in partnership proposals",
 "4. Maintain clear documentation of all discussions and agreements",
 "5. Ensure proper handoff to relevant team members when needed",
 ],
 add_datetime_to_instructions=True,
 markdown=True,
)

financial_analyst_agent = Agent(
 name="Financial Analyst Agent",
 role="Financial Analyst",
 model=OpenAIChat("gpt-4o"),
 knowledge=knowledge_base,
 tools=[YFinanceTools()],
 instructions=[
 "You are the Financial Analyst of a startup, responsible for financial planning and analysis.",
 "Key Responsibilities:",
 "1. Develop financial models and projections",
 "2. Create and analyze revenue forecasts",
 "3. Evaluate pricing strategies and unit economics",
 "4. Prepare investor reports and presentations",
 "5. Monitor cash flow and burn rate",
 "6. Analyze market conditions and financial trends",
 "7. Assess potential investment opportunities",
 "8. Track key financial metrics and KPIs",
 "9. Provide financial insights for strategic decisions",
 ],
 add_datetime_to_instructions=True,
 markdown=True,
)

customer_support_agent = Agent(
 name="Customer Support Agent",
 role="Customer Support",
 model=OpenAIChat("gpt-4o"),
 knowledge=knowledge_base,
 tools=[SlackTools()],
 instructions=[
 "You are the Customer Support Agent of a startup, responsible for handling customer inquiries and maintaining customer satisfaction.",
 f"When a user reports an issue or issue or the question you cannot answer, always send it to the #{support_channel} Slack channel with all relevant details.",
 "Always maintain a professional and helpful demeanor while ensuring proper routing of issues to the right channels.",
 ],
 add_datetime_to_instructions=True,
 markdown=True,
)

autonomous_startup_team = Team(
 name="CEO Agent",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 instructions=[
 "You are the CEO of a startup, responsible for overall leadership and success.",
 " Always transfer task to product manager agent so it can search the knowledge base.",
 "Instruct all agents to use the knowledge base to answer questions.",
 "Key Responsibilities:",
 "1. Set and communicate company vision and strategy",
 "2. Coordinate and prioritize team activities",
 "3. Make high-level strategic decisions",
 "4. Evaluate opportunities and risks",
 "5. Manage resource allocation",
 "6. Drive growth and innovation",
 "7. When a customer asks for help or reports an issue, immediately delegate to the Customer Support Agent",
 "8. When any partnership, sales, or business development inquiries come in, immediately delegate to the Sales Agent",
 "",
 "Team Coordination Guidelines:",
 "1. Product Development:",
 " - Consult Product Manager for feature prioritization",
 " - Use Market Research for validation",
 " - Verify Legal Compliance for new features",
 "2. Market Entry:",
 " - Combine Market Research and Sales insights",
 " - Validate financial viability with Financial Analyst",
 "3. Strategic Planning:",
 " - Gather input from all team members",
 " - Prioritize based on market opportunity and resources",
 "4. Risk Management:",
 " - Consult Legal Compliance for regulatory risks",
 " - Review Financial Analyst's risk assessments",
 "5. Customer Support:",
 " - Ensure all customer inquiries are handled promptly and professionally",
 " - Maintain a positive and helpful attitude",
 " - Escalate critical issues to the appropriate team",
 "",
 "Always maintain a balanced view of short-term execution and long-term strategy.",
 ],
 members=[
 product_manager_agent,
 market_research_agent,
 financial_analyst_agent,
 legal_compliance_agent,
 customer_support_agent,
 sales_agent,
 ],
 add_datetime_to_instructions=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)

autonomous_startup_team.print_response(
 message="I want to start a startup that sells AI agents to businesses. What is the best way to do this?",
 stream=True,
 stream_intermediate_steps=True,
)

autonomous_startup_team.print_response(
 message="Give me good marketing campaign for buzzai?",
 stream=True,
 stream_intermediate_steps=True,
)

autonomous_startup_team.print_response(
 message="What is my company and what are the monetization strategies?",
 stream=True,
 stream_intermediate_steps=True,
)
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai duckduckgo-search exa_py slack yfinance
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export SLACK_TOKEN=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python autonomous_startup_team.py
 ```
 </Step>
</Steps>

# HackerNews Team
Source: https://docs.agno.com/examples/teams/coordinate/hackernews_team

This example shows how to create a HackerNews team that can aggregate, curate, and discuss trending topics from HackerNews.

## Code

```python hackernews_team.py
from typing import List

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools
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

article_reader = Agent(
 name="Article Reader",
 role="Reads articles from URLs.",
 tools=[Newspaper4kTools()],
)

hn_team = Team(
 name="HackerNews Team",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[hn_researcher, web_searcher, article_reader],
 instructions=[
 "First, search hackernews for what the user is asking about.",
 "Then, ask the article reader to read the links for the stories to get more information.",
 "Important: you must provide the article reader with the links to read.",
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

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai duckduckgo-search newspaper4k lxml_html_clean
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python hackernews_team.py
 ```
 </Step>
</Steps>

# News Agency Team
Source: https://docs.agno.com/examples/teams/coordinate/news_agency_team

This example shows how to create a news agency team that can search the web, write an article, and edit it.

## Code

```python news_agency_team.py

from pathlib import Path

from agno.agent import Agent
from agno.models.openai.chat import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools

urls_file = Path(__file__).parent.joinpath("tmp", "urls__{session_id}.md")
urls_file.parent.mkdir(parents=True, exist_ok=True)

searcher = Agent(
 name="Searcher",
 role="Searches the top URLs for a topic",
 instructions=[
 "Given a topic, first generate a list of 3 search terms related to that topic.",
 "For each search term, search the web and analyze the results.Return the 10 most relevant URLs to the topic.",
 "You are writing for the New York Times, so the quality of the sources is important.",
 ],
 tools=[DuckDuckGoTools()],
 add_datetime_to_instructions=True,
)
writer = Agent(
 name="Writer",
 role="Writes a high-quality article",
 description=(
 "You are a senior writer for the New York Times. Given a topic and a list of URLs, "
 "your goal is to write a high-quality NYT-worthy article on the topic."
 ),
 instructions=[
 "First read all urls using `read_article`."
 "Then write a high-quality NYT-worthy article on the topic."
 "The article should be well-structured, informative, engaging and catchy.",
 "Ensure the length is at least as long as a NYT cover story -- at a minimum, 15 paragraphs.",
 "Ensure you provide a nuanced and balanced opinion, quoting facts where possible.",
 "Focus on clarity, coherence, and overall quality.",
 "Never make up facts or plagiarize. Always provide proper attribution.",
 "Remember: you are writing for the New York Times, so the quality of the article is important.",
 ],
 tools=[Newspaper4kTools()],
 add_datetime_to_instructions=True,
)

editor = Team(
 name="Editor",
 mode="coordinate",
 model=OpenAIChat("gpt-4o"),
 members=[searcher, writer],
 description="You are a senior NYT editor. Given a topic, your goal is to write a NYT worthy article.",
 instructions=[
 "First ask the search journalist to search for the most relevant URLs for that topic.",
 "Then ask the writer to get an engaging draft of the article.",
 "Edit, proofread, and refine the article to ensure it meets the high standards of the New York Times.",
 "The article should be extremely articulate and well written. "
 "Focus on clarity, coherence, and overall quality.",
 "Remember: you are the final gatekeeper before the article is published, so make sure the article is perfect.",
 ],
 add_datetime_to_instructions=True,
 enable_agentic_context=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
)
editor.print_response("Write an article about latest developments in AI.")
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai duckduckgo-search newspaper4k lxml_html_clean
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python news_agency_team.py
 ```
 </Step>
</Steps>

# AI Support Team
Source: https://docs.agno.com/examples/teams/route/ai_support_team

This example illustrates how to create an AI support team that can route customer inquiries to the appropriate agent based on the nature of the inquiry.

## Code

```python ai_support_team.py

from agno.agent import Agent
from agno.knowledge.website import WebsiteKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.exa import ExaTools
from agno.tools.slack import SlackTools
from agno.vectordb.pgvector.pgvector import PgVector

knowledge_base = WebsiteKnowledgeBase(
 urls=["https://docs.agno.com/introduction"],
 # Number of links to follow from the seed URLs
 max_links=10,
 # Table name: ai.website_documents
 vector_db=PgVector(
 table_name="website_documents",
 db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
 ),
)
knowledge_base.load(recreate=False)
support_channel = "testing"
feedback_channel = "testing"

doc_researcher_agent = Agent(
 name="Doc researcher Agent",
 role="Search the knowledge base for information",
 model=OpenAIChat(id="gpt-4o"),
 tools=[DuckDuckGoTools(), ExaTools()],
 knowledge=knowledge_base,
 search_knowledge=True,
 instructions=[
 "You are a documentation expert for given product. Search the knowledge base thoroughly to answer user questions.",
 "Always provide accurate information based on the documentation.",
 "If the question matches an FAQ, provide the specific FAQ answer from the documentation.",
 "When relevant, include direct links to specific documentation pages that address the user's question.",
 "If you're unsure about an answer, acknowledge it and suggest where the user might find more information.",
 "Format your responses clearly with headings, bullet points, and code examples when appropriate.",
 "Always verify that your answer directly addresses the user's specific question.",
 "If you cannot find the answer in the documentation knowledge base, use the DuckDuckGoTools or ExaTools to search the web for relevant information to answer the user's question.",
 ],
)

escalation_manager_agent = Agent(
 name="Escalation Manager Agent",
 role="Escalate the issue to the slack channel",
 model=OpenAIChat(id="gpt-4o"),
 tools=[SlackTools()],
 instructions=[
 "You are an escalation manager responsible for routing critical issues to the support team.",
 f"When a user reports an issue, always send it to the #{support_channel} Slack channel with all relevant details using the send_message toolkit function.",
 "Include the user's name, contact information (if available), and a clear description of the issue.",
 "After escalating the issue, respond to the user confirming that their issue has been escalated.",
 "Your response should be professional and reassuring, letting them know the support team will address it soon.",
 "Always include a ticket or reference number if available to help the user track their issue.",
 "Never attempt to solve technical problems yourself - your role is strictly to escalate and communicate.",
 ],
)

feedback_collector_agent = Agent(
 name="Feedback Collector Agent",
 role="Collect feedback from the user",
 model=OpenAIChat(id="gpt-4o"),
 tools=[SlackTools()],
 description="You are an AI agent that can collect feedback from the user.",
 instructions=[
 "You are responsible for collecting user feedback about the product or feature requests.",
 f"When a user provides feedback or suggests a feature, use the Slack tool to send it to the #{feedback_channel} channel using the send_message toolkit function.",
 "Include all relevant details from the user's feedback in your Slack message.",
 "After sending the feedback to Slack, respond to the user professionally, thanking them for their input.",
 "Your response should acknowledge their feedback and assure them that it will be taken into consideration.",
 "Be warm and appreciative in your tone, as user feedback is valuable for improving our product.",
 "Do not promise specific timelines or guarantee that their suggestions will be implemented.",
 ],
)

customer_support_team = Team(
 name="Customer Support Team",
 mode="route",
 model=OpenAIChat("gpt-4.5-preview"),
 enable_team_history=True,
 members=[doc_researcher_agent, escalation_manager_agent, feedback_collector_agent],
 show_tool_calls=True,
 markdown=True,
 debug_mode=True,
 show_members_responses=True,
 instructions=[
 "You are the lead customer support agent responsible for classifying and routing customer inquiries.",
 "Carefully analyze each user message and determine if it is: a question that needs documentation research, a bug report that requires escalation, or product feedback.",
 "For general questions about the product, route to the doc_researcher_agent who will search documentation for answers.",
 "If the doc_researcher_agent cannot find an answer to a question, escalate it to the escalation_manager_agent.",
 "For bug reports or technical issues, immediately route to the escalation_manager_agent.",
 "For feature requests or product feedback, route to the feedback_collector_agent.",
 "Always provide a clear explanation of why you're routing the inquiry to a specific agent.",
 "After receiving a response from the appropriate agent, relay that information back to the user in a professional and helpful manner.",
 "Ensure a seamless experience for the user by maintaining context throughout the conversation.",
 ],
)

# Add in the query and the agent redirects it to the appropriate agent
customer_support_team.print_response(
 "Hi Team, I want to build an educational platform where the models are have access to tons of study materials, How can Agno platform help me build this?",
 stream=True,
)
# customer_support_team.print_response(
# "[Feature Request] Support json schemas in Gemini client in addition to pydantic base model",
# stream=True,
# )
# customer_support_team.print_response(
# "[Feature Request] Can you please update me on the above feature",
# stream=True,
# )
# customer_support_team.print_response(
# "[Bug] Async tools in team of agents not awaited properly, causing runtime errors ",
# stream=True,
# )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai duckduckgo-search slack_sdk exa_py
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export SLACK_TOKEN=****
 export EXA_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python ai_support_team.py
 ```
 </Step>
</Steps>

# Multi Language Team
Source: https://docs.agno.com/examples/teams/route/multi_language_team

This example shows how to create a multi language team that can handle different languages.

## Code

```python multi_language_team.py

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.deepseek import DeepSeek
from agno.models.mistral import MistralChat
from agno.models.openai import OpenAIChat
from agno.team.team import Team

english_agent = Agent(
 name="English Agent",
 role="You can only answer in English",
 model=OpenAIChat(id="gpt-4.5-preview"),
 instructions=[
 "You must only respond in English",
 ],
)

japanese_agent = Agent(
 name="Japanese Agent",
 role="You can only answer in Japanese",
 model=DeepSeek(id="deepseek-chat"),
 instructions=[
 "You must only respond in Japanese",
 ],
)
chinese_agent = Agent(
 name="Chinese Agent",
 role="You can only answer in Chinese",
 model=DeepSeek(id="deepseek-chat"),
 instructions=[
 "You must only respond in Chinese",
 ],
)
spanish_agent = Agent(
 name="Spanish Agent",
 role="You can only answer in Spanish",
 model=OpenAIChat(id="gpt-4.5-preview"),
 instructions=[
 "You must only respond in Spanish",
 ],
)

french_agent = Agent(
 name="French Agent",
 role="You can only answer in French",
 model=MistralChat(id="mistral-large-latest"),
 instructions=[
 "You must only respond in French",
 ],
)

german_agent = Agent(
 name="German Agent",
 role="You can only answer in German",
 model=Claude("claude-3-5-sonnet-20241022"),
 instructions=[
 "You must only respond in German",
 ],
)
multi_language_team = Team(
 name="Multi Language Team",
 mode="route",
 model=OpenAIChat("gpt-4.5-preview"),
 members=[
 english_agent,
 spanish_agent,
 japanese_agent,
 french_agent,
 german_agent,
 chinese_agent,
 ],
 show_tool_calls=True,
 markdown=True,
 instructions=[
 "You are a language router that directs questions to the appropriate language agent.",
 "If the user asks in a language whose agent is not a team member, respond in English with:",
 "'I can only answer in the following languages: English, Spanish, Japanese, French and German. Please ask your question in one of these languages.'",
 "Always check the language of the user's input before routing to an agent.",
 "For unsupported languages like Italian, respond in English with the above message.",
 ],
 show_members_responses=True,
)

# Ask "How are you?" in all supported languages
# multi_language_team.print_response(
# "How are you?", stream=True # English
# )

# multi_language_team.print_response(
# "你好吗？", stream=True # Chinese
# )

# multi_language_team.print_response(
# "お元気ですか?", stream=True # Japanese
# )

multi_language_team.print_response(
 "Comment allez-vous?",
 stream=True, # French
)

# multi_language_team.print_response(
# "Wie geht es Ihnen?", stream=True # German
# )

# multi_language_team.print_response(
# "Come stai?", stream=True # Italian
# )
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai anthropic mistralai
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 export ANTHROPIC_API_KEY=****
 export DEEPSEEK_API_KEY=****
 export MISTRAL_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python multi_language_team.py
 ```
 </Step>
</Steps>

# Team Session State
Source: https://docs.agno.com/examples/teams/shared_state/team_session_state

This example demonstrates how a shared team\_session\_state can propagate and persist across nested agents and subteams, enabling seamless state management for collaborative tasks.

## Code

```python cookbook/teams/team_with_nested_shared_state.py

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
 agent_id="shopping_list_manager",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[add_item, remove_item, remove_all_items],
 instructions=[
 "Manage the shopping list by adding and removing items",
 "Always confirm when items are added or removed",
 "If the task is done, update the session state to log the changes & chores you've performed",
 ],
)

# Shopping management team - new layer for handling all shopping list modifications
shopping_mgmt_team = Team(
 name="Shopping Management Team",
 team_id="shopping_management",
 mode="coordinate",
 model=OpenAIChat(id="gpt-4o-mini"),
 show_tool_calls=True,
 members=[shopping_list_agent],
 instructions=[
 "Manage adding and removing items from the shopping list using the Shopping List Agent",
 "Forward requests to add or remove items to the Shopping List Agent",
 ],
)

def get_ingredients(agent: Agent) -> str:
 """Retrieve ingredients from the shopping list to use for recipe suggestions.

 Args:
 meal_type (str): Type of meal to suggest (breakfast, lunch, dinner, snack, or any)
 """
 shopping_list = agent.team_session_state["shopping_list"]

 if not shopping_list:
 return "The shopping list is empty. Add some ingredients first to get recipe suggestions."

 # Just return the ingredients - the agent will create recipes
 return f"Available ingredients from shopping list: {', '.join(shopping_list)}"

recipe_agent = Agent(
 name="Recipe Suggester",
 agent_id="recipe_suggester",
 role="Suggest recipes based on available ingredients",
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[get_ingredients],
 instructions=[
 "First, use the get_ingredients tool to get the current ingredients from the shopping list",
 "After getting the ingredients, create detailed recipe suggestions based on those ingredients",
 "Create at least 3 different recipe ideas using the available ingredients",
 "For each recipe, include: name, ingredients needed (highlighting which ones are from the shopping list), and brief preparation steps",
 "Be creative but practical with recipe suggestions",
 "Consider common pantry items that people usually have available in addition to shopping list items",
 "Consider dietary preferences if mentioned by the user",
 "If no meal type is specified, suggest a variety of options (breakfast, lunch, dinner, snacks)",
 ],
)

def list_items(team: Team) -> str:
 """List all items in the shopping list."""
 shopping_list = team.team_session_state["shopping_list"]

 if not shopping_list:
 return "The shopping list is empty."

 items_text = "\n".join([f"- {item}" for item in shopping_list])
 return f"Current shopping list:\n{items_text}"

# Create meal planning subteam
meal_planning_team = Team(
 name="Meal Planning Team",
 team_id="meal_planning",
 mode="coordinate",
 model=OpenAIChat(id="gpt-4o-mini"),
 members=[recipe_agent],
 instructions=[
 "You are a meal planning team that suggests recipes based on shopping list items.",
 "IMPORTANT: When users ask 'What can I make with these ingredients?' or any recipe-related questions, IMMEDIATELY forward the EXACT SAME request to the recipe_agent WITHOUT asking for further information.",
 "DO NOT ask the user for ingredients - the recipe_agent will work with what's already in the shopping list.",
 "Your primary job is to forward recipe requests directly to the recipe_agent without modification.",
 ],
)

def add_chore(team: Team, chore: str, priority: str = "medium") -> str:
 """Add a chore to the list with priority level.

 Args:
 chore (str): The chore to add to the list
 priority (str): Priority level of the chore (low, medium, high)

 Returns:
 str: Confirmation message
 """
 # Initialize chores list if it doesn't exist
 if "chores" not in team.session_state:
 team.session_state["chores"] = []

 # Validate priority
 valid_priorities = ["low", "medium", "high"]
 if priority.lower() not in valid_priorities:
 priority = "medium" # Default to medium if invalid

 # Add the chore with timestamp and priority
 from datetime import datetime

 chore_entry = {
 "description": chore,
 "priority": priority.lower(),
 "added_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
 }

 team.session_state["chores"].append(chore_entry)

 return f"Added chore: '{chore}' with {priority} priority"

shopping_team = Team(
 name="Shopping List Team",
 mode="coordinate",
 model=OpenAIChat(id="gpt-4o-mini"),
 team_session_state={"shopping_list": []},
 tools=[list_items, add_chore],
 session_state={"chores": []},
 team_id="shopping_list_team",
 members=[
 shopping_mgmt_team,
 meal_planning_team,
 ],
 show_tool_calls=True,
 markdown=True,
 instructions=[
 "You are a team that manages a shopping list & helps plan meals using that list.",
 "If you need to add or remove items from the shopping list, forward the full request to the Shopping Management Team.",
 "IMPORTANT: If the user asks about recipes or what they can make with ingredients, IMMEDIATELY forward the EXACT request to the meal_planning_team with NO additional questions.",
 "Example: When user asks 'What can I make with these ingredients?', you should simply forward this exact request to meal_planning_team without asking for more information.",
 "If you need to list the items in the shopping list, use the list_items tool.",
 "If the user got something from the shopping list, it means it can be removed from the shopping list.",
 "After each completed task, use the add_chore tool to log exactly what was done with high priority.",
 ],
 show_members_responses=True,
)

# Example usage
shopping_team.print_response(
 "Add milk, eggs, and bread to the shopping list", stream=True
)
print(f"Session state: {shopping_team.team_session_state}")

shopping_team.print_response("I got bread", stream=True)
print(f"Session state: {shopping_team.team_session_state}")

shopping_team.print_response("I need apples and oranges", stream=True)
print(f"Session state: {shopping_team.team_session_state}")

shopping_team.print_response("whats on my list?", stream=True)
print(f"Session state: {shopping_team.team_session_state}")

# Try the meal planning feature
shopping_team.print_response("What can I make with these ingredients?", stream=True)
print(f"Session state: {shopping_team.team_session_state}")

shopping_team.print_response(
 "Clear everything from my list and start over with just bananas and yogurt",
 stream=True,
)
print(f"Shared Session state: {shopping_team.team_session_state}")

print(f"Team session state: {shopping_team.session_state}")

```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install required libraries">
 ```bash
 pip install openai
 ```
 </Step>

 <Step title="Set environment variables">
 ```bash
 export OPENAI_API_KEY=****
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python cookbook/teams/team_with_nested_shared_state.py
 ```
 </Step>
</Steps>

# Async Hacker News Reporter
Source: https://docs.agno.com/examples/workflows/async-hackernews-reporter

An asynchronous Hacker News reporter using workflows that fetches the latest news

**AsyncHackerNewsReporter** is a workflow designed to asynchronously fetch the top stories from Hacker News and generate a comprehensive report on them. This workflow utilizes the `arun` method to efficiently handle multiple asynchronous tasks, ensuring a smooth and non-blocking operation.

```python async_workflow.py
import asyncio
import json
from typing import AsyncIterator

import httpx
from agno.agent import Agent, RunResponse
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import RunEvent, Workflow

class AsyncHackerNewsReporter(Workflow):
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

 async def get_top_hackernews_stories(self, num_stories: int = 10) -> str:
 """Use this function to get top stories from Hacker News.

 Args:
 num_stories (int): Number of stories to return. Defaults to 10.

 Returns:
 str: JSON string of top stories.
 """
 async with httpx.AsyncClient() as client:
 # Fetch top story IDs
 response = await client.get(
 "https://hacker-news.firebaseio.com/v0/topstories.json"
 )
 story_ids = response.json()

 # Fetch story details concurrently
 tasks = [
 client.get(
 f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
 )
 for story_id in story_ids[:num_stories]
 ]
 responses = await asyncio.gather(*tasks)

 stories = []
 for response in responses:
 story = response.json()
 story["username"] = story["by"]
 stories.append(story)

 return json.dumps(stories)

 async def arun(self, num_stories: int = 5) -> AsyncIterator[RunResponse]:
 # Set the tools for hn_agent here to avoid circular reference
 self.hn_agent.tools = [self.get_top_hackernews_stories]

 logger.info(f"Getting top {num_stories} stories from HackerNews.")
 top_stories: RunResponse = await self.hn_agent.arun(num_stories=num_stories)
 if top_stories is None or not top_stories.content:
 yield RunResponse(
 run_id=self.run_id,
 content="Sorry, could not get the top stories.",
 event=RunEvent.workflow_completed,
 )
 return

 logger.info("Reading each story and writing a report.")
 # Get the async iterator from writer.arun()
 writer_response = await self.writer.arun(top_stories.content, stream=True)

 # Stream the writer's response directly
 async for response in writer_response:
 if response.content:
 yield RunResponse(
 content=response.content, event=response.event, run_id=self.run_id
 )

if __name__ == "__main__":
 import asyncio

 async def main():
 # Initialize the workflow
 workflow = AsyncHackerNewsReporter(debug_mode=False)

 # Run the workflow and collect the final response
 final_content = []
 try:
 async for response in workflow.arun(num_stories=5):
 if response.content:
 final_content.append(response.content)
 except Exception as e:
 logger.error(f"Error running workflow: {e}")
 return

 # Create final response with combined content
 if final_content:
 final_response = RunResponse(
 content="".join(final_content), event=RunEvent.workflow_completed
 )
 # Pretty print the final response
 pprint_run_response(final_response, markdown=True, show_time=True)

 # Run the async main function
 asyncio.run(main())
```

## Usage

<Steps>
 <Snippet file="create-venv-step.mdx" />

 <Step title="Install libraries">
 ```bash
 pip install agno newspaper4k lxml_html_clean openai httpx
 ```
 </Step>

 <Step title="Run the agent">
 ```bash
 python async_workflow.py
 ```
 </Step>
</Steps>

# Blog Post Generator
Source: https://docs.agno.com/examples/workflows/blog-post-generator

This advanced example demonstrates how to build a sophisticated blog post generator that combines
web research capabilities with professional writing expertise. The workflow uses a multi-stage
approach:

1. Intelligent web research and source gathering
2. Content extraction and processing
3. Professional blog post writing with proper citations

Key capabilities:

* Advanced web research and source evaluation
* Content scraping and processing
* Professional writing with SEO optimization
* Automatic content caching for efficiency
* Source attribution and fact verification

Example blog topics to try:

* "The Rise of Artificial General Intelligence: Latest Breakthroughs"
* "How Quantum Computing is Revolutionizing Cybersecurity"
* "Sustainable Living in 2024: Practical Tips for Reducing Carbon Footprint"
* "The Future of Work: AI and Human Collaboration"
* "Space Tourism: From Science Fiction to Reality"
* "Mindfulness and Mental Health in the Digital Age"
* "The Evolution of Electric Vehicles: Current State and Future Trends"

Run `pip install openai duckduckgo-search newspaper4k lxml_html_clean sqlalchemy agno` to install dependencies.
"""

```python blog_post_generator.py
import json
from textwrap import dedent
from typing import Dict, Iterator, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.utils.pprint import pprint_run_response
from agno.workflow import RunEvent, RunResponse, Workflow
from pydantic import BaseModel, Field

class NewsArticle(BaseModel):
 title: str = Field(..., description="Title of the article.")
 url: str = Field(..., description="Link to the article.")
 summary: Optional[str] = Field(
 ..., description="Summary of the article if available."
 )

class SearchResults(BaseModel):
 articles: list[NewsArticle]

class ScrapedArticle(BaseModel):
 title: str = Field(..., description="Title of the article.")
 url: str = Field(..., description="Link to the article.")
 summary: Optional[str] = Field(
 ..., description="Summary of the article if available."
 )
 content: Optional[str] = Field(
 ...,
 description="Full article content in markdown format. None if content is unavailable.",
 )

class BlogPostGenerator(Workflow):
 """Advanced workflow for generating professional blog posts with proper research and citations."""

 description: str = dedent("""\
 An intelligent blog post generator that creates engaging, well-researched content.
 This workflow orchestrates multiple AI agents to research, analyze, and craft
 compelling blog posts that combine journalistic rigor with engaging storytelling.
 The system excels at creating content that is both informative and optimized for
 digital consumption.
 """)

 # Search Agent: Handles intelligent web searching and source gathering
 searcher: Agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[DuckDuckGoTools()],
 description=dedent("""\
 You are BlogResearch-X, an elite research assistant specializing in discovering
 high-quality sources for compelling blog content. Your expertise includes:

 - Finding authoritative and trending sources
 - Evaluating content credibility and relevance
 - Identifying diverse perspectives and expert opinions
 - Discovering unique angles and insights
 - Ensuring comprehensive topic coverage\
 """),
 instructions=dedent("""\
 1. Search Strategy 🔍
 - Find 10-15 relevant sources and select the 5-7 best ones
 - Prioritize recent, authoritative content
 - Look for unique angles and expert insights
 2. Source Evaluation 📊
 - Verify source credibility and expertise
 - Check publication dates for timeliness
 - Assess content depth and uniqueness
 3. Diversity of Perspectives 🌐
 - Include different viewpoints
 - Gather both mainstream and expert opinions
 - Find supporting data and statistics\
 """),
 response_model=SearchResults,
 )

 # Content Scraper: Extracts and processes article content
 article_scraper: Agent = Agent(
 model=OpenAIChat(id="gpt-4o-mini"),
 tools=[Newspaper4kTools()],
 description=dedent("""\
 You are ContentBot-X, a specialist in extracting and processing digital content
 for blog creation. Your expertise includes:

 - Efficient content extraction
 - Smart formatting and structuring
 - Key information identification
 - Quote and statistic preservation
 - Maintaining source attribution\
 """),
 instructions=dedent("""\
 1. Content Extraction 📑
 - Extract content from the article
 - Preserve important quotes and statistics
 - Maintain proper attribution
 - Handle paywalls gracefully
 2. Content Processing 🔄
 - Format text in clean markdown
 - Preserve key information
 - Structure content logically
 3. Quality Control ✅
 - Verify content relevance
 - Ensure accurate extraction
 - Maintain readability\
 """),
 response_model=ScrapedArticle,
 )

 # Content Writer Agent: Crafts engaging blog posts from re
 writer: Agent = Agent(
 model=OpenAIChat(id="gpt-4o"),
 description=dedent("""\
 You are BlogMaster-X, an elite content creator combining journalistic excellence
 with digital marketing expertise. Your strengths include:

 - Crafting viral-worthy headlines
 - Writing engaging introductions
 - Structuring content for digital consumption
 - Incorporating research seamlessly
 - Optimizing for SEO while maintaining quality
 - Creating shareable conclusions\
 """),
 instructions=dedent("""\
 1. Content Strategy 📝
 - Craft attention-grabbing headlines
 - Write compelling introductions
 - Structure content for engagement
 - Include relevant subheadings
 2. Writing Excellence ✍️
 - Balance expertise with accessibility
 - Use clear, engaging language
 - Include relevant examples
 - Incorporate statistics naturally
 3. Source Integration 🔍
 - Cite sources properly
 - Include expert quotes
 - Maintain factual accuracy
 4. Digital Optimization 💻
 - Structure for scanability
 - Include shareable takeaways
 - Optimize for SEO
 - Add engaging subheadings\
 """),
 expected_output=dedent("""\
 # {Viral-Worthy Headline}

 ## Introduction
 {Engaging hook and context}

 ## {Compelling Section 1}
 {Key insights and analysis}
 {Expert quotes and statistics}

 ## {Engaging Section 2}
 {Deeper exploration}
 {Real-world examples}

 ## {Practical Section 3}
 {Actionable insights}
 {Expert recommendations}

 ## Key Takeaways
 - {Shareable insight 1}
 - {Practical takeaway 2}
 - {Notable finding 3}

 ## Sources
 {Properly attributed sources with links}\
 """),
 markdown=True,
 )

 def run(
 self,
 topic: str,
 use_search_cache: bool = True,
 use_scrape_cache: bool = True,
 use_cached_report: bool = True,
 ) -> Iterator[RunResponse]:
 logger.info(f"Generating a blog post on: {topic}")

 # Use the cached blog post if use_cache is True
 if use_cached_report:
 cached_blog_post = self.get_cached_blog_post(topic)
 if cached_blog_post:
 yield RunResponse(
 content=cached_blog_post, event=RunEvent.workflow_completed
 )
 return

 # Search the web for articles on the topic
 search_results: Optional[SearchResults] = self.get_search_results(
 topic, use_search_cache
 )
 # If no search_results are found for the topic, end the workflow
 if search_results is None or len(search_results.articles) == 0:
 yield RunResponse(
 event=RunEvent.workflow_completed,
 content=f"Sorry, could not find any articles on the topic: {topic}",
 )
 return

 # Scrape the search results
 scraped_articles: Dict[str, ScrapedArticle] = self.scrape_articles(
 topic, search_results, use_scrape_cache
 )

 # Prepare the input for the writer
 writer_input = {
 "topic": topic,
 "articles": [v.model_dump() for v in scraped_articles.values()],
 }

 # Run the writer and yield the response
 yield from self.writer.run(json.dumps(writer_input, indent=4), stream=True)

 # Save the blog post in the cache
 self.add_blog_post_to_cache(topic, self.writer.run_response.content)

 def get_cached_blog_post(self, topic: str) -> Optional[str]:
 logger.info("Checking if cached blog post exists")

 return self.session_state.get("blog_posts", {}).get(topic)

 def add_blog_post_to_cache(self, topic: str, blog_post: str):
 logger.info(f"Saving blog post for topic: {topic}")
 self.session_state.setdefault("blog_posts", {})
 self.session_state["blog_posts"][topic] = blog_post

 def get_cached_search_results(self, topic: str) -> Optional[SearchResults]:
 logger.info("Checking if cached search results exist")
 search_results = self.session_state.get("search_results", {}).get(topic)
 return (
 SearchResults.model_validate(search_results)
 if search_results and isinstance(search_results, dict)
 else search_results
 )

 def add_search_results_to_cache(self, topic: str, search_results: SearchResults):
 logger.info(f"Saving search results for topic: {topic}")
 self.session_state.setdefault("search_results", {})
 self.session_state["search_results"][topic] = search_results

 def get_cached_scraped_articles(
 self, topic: str
 ) -> Optional[Dict[str, ScrapedArticle]]:
 logger.info("Checking if cached scraped articles exist")
 scraped_articles = self.session_state.get("scraped_articles", {}).get(topic)
 return (
 ScrapedArticle.model_validate(scraped_articles)
 if scraped_articles and isinstance(scraped_articles, dict)
 else scraped_articles
 )

 def add_scraped_articles_to_cache(
 self, topic: str, scraped_articles: Dict[str, ScrapedArticle]
 ):
 logger.info(f"Saving scraped articles for topic: {topic}")
 self.session_state.setdefault("scraped_articles", {})
 self.session_state["scraped_articles"][topic] = scraped_articles

 def get_search_results(
 self, topic: str, use_search_cache: bool, num_attempts: int = 3
 ) -> Optional[SearchResults]:
 # Get cached search_results from the session state if use_search_cache is True
 if use_search_cache:
 try:
 search_results_from_cache = self.get_cached_search_results(topic)
 if search_results_from_cache is not None:
 search_results = SearchResults.model_validate(
 search_results_from_cache
 )
 logger.info(
 f"Found {len(search_results.articles)} articles in cache."
 )
 return search_results
 except Exception as e:
 logger.warning(f"Could not read search results from cache: {e}")

 # If there are no cached search_results, use the searcher to find the latest articles
 for attempt in range(num_attempts):
 try:
 searcher_response: RunResponse = self.searcher.run(topic)
