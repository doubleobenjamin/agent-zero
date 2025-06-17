from __future__ import annotations
import glob
import os
import hashlib
import json
from typing import Any, Dict, Literal, TypedDict, Optional, List # Added Optional, List
from langchain_community.document_loaders import (
    CSVLoader,
    # JSONLoader, # Will use TextLoader for JSON as per new FILE_LOADERS from prompt for load_knowledge_enhanced
    TextLoader, # Added TextLoader for use in new FILE_LOADERS
    PDFMinerLoader, # Added PDFMinerLoader for new FILE_LOADERS
    UnstructuredMarkdownLoader, # Added UnstructuredMarkdownLoader for new FILE_LOADERS
    HTMLLoader, # Added HTMLLoader for new FILE_LOADERS
    JSONLoader, # Re-added JSONLoader as it's in the prompt's FILE_LOADERS
    PyPDFLoader,
    PyPDFLoader, # Kept PyPDFLoader for existing load_knowledge
    # TextLoader, # Already added above
    UnstructuredHTMLLoader, # Kept for existing load_knowledge
    # UnstructuredMarkdownLoader, # Already added above
)
from langchain.text_splitter import RecursiveCharacterTextSplitter # Added
from python.helpers import files
from python.helpers.log import LogItem
from python.helpers.print_style import PrintStyle
from python.helpers.memory import Memory # Added for type hint & MAL access

text_loader_kwargs = {"autodetect_encoding": True}


# --- New code for load_knowledge_enhanced ---

FILE_LOADERS = {
    ".txt": TextLoader,
    ".pdf": PDFMinerLoader, # Using PDFMinerLoader as per prompt for new function
    ".md": UnstructuredMarkdownLoader, # Using UnstructuredMarkdownLoader for new function
    ".csv": CSVLoader,
    ".html": HTMLLoader,
    ".json": JSONLoader, # Using JSONLoader for new function
}

DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200

async def load_knowledge_enhanced(
    log_item: Optional[LogItem],
    knowledge_dir: str,
    metadata: Dict[str, Any], # Contains 'area'
    agent: Memory.Agent, # Agent instance to get MAL (Agent type from Memory due to forward ref)
    filename_pattern: str = "**/*",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> None: # Returns None as it directly ingests via MAL
    """
    Loads documents from a directory, chunks them, and ingests them using the Memory Abstraction Layer.
    """
    if not agent:
        if log_item: await log_item.log("Error: Agent instance not provided to load_knowledge_enhanced.", style="error")
        return

    memory_layer = await Memory.get_abstraction_layer(agent)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    processed_files = 0
    for file_path in glob.glob(os.path.join(knowledge_dir, filename_pattern), recursive=True):
        if os.path.isdir(file_path):
            continue

        file_ext = os.path.splitext(file_path)[1].lower()
        LoaderClass = FILE_LOADERS.get(file_ext) # Renamed to avoid conflict with 'loader' instance

        if not LoaderClass:
            if log_item: await log_item.log(f"Skipping file {file_path}, unsupported extension {file_ext}.")
            continue

        if log_item: await log_item.log(f"Processing knowledge file: {file_path} for area {metadata.get('area')}")

        try:
            # Some loaders might need specific encoding etc. For now, using default instantiation.
            # TextLoader from langchain_community.document_loaders takes file_path and encoding.
            # Others like PDFMinerLoader just take file_path.
            if LoaderClass is TextLoader: # Example: provide encoding for text-based loaders
                 loader = LoaderClass(file_path, autodetect_encoding=True)
            else:
                 loader = LoaderClass(file_path)

            langchain_documents = loader.load() # Returns List[LangchainDocument]

            # Split documents into chunks
            split_docs = text_splitter.split_documents(langchain_documents)

            documents_to_ingest = []
            for i, chunk_doc in enumerate(split_docs):
                doc_metadata = {
                    **metadata, # Includes 'area'
                    "source_file": file_path,
                    "filename": os.path.basename(file_path),
                    "chunk_index": i,
                    "total_chunks": len(split_docs),
                }
                documents_to_ingest.append({
                    "content": chunk_doc.page_content,
                    "metadata": doc_metadata
                })

            if documents_to_ingest:
                # Use process_knowledge_documents for batch insertion via MAL
                doc_ids = await memory_layer.process_knowledge_documents(documents_to_ingest)
                if log_item: await log_item.log(f"Ingested {len(doc_ids)} chunks from {file_path}.")
                processed_files += 1
            else:
                if log_item: await log_item.log(f"No content to ingest from {file_path}.")

        except Exception as e:
            if log_item: await log_item.log(f"Failed to process or ingest {file_path}: {e}", style="error")

    if log_item: await log_item.log(f"Finished knowledge loading from {knowledge_dir}. Processed {processed_files} files.")

# --- End of new code ---


class KnowledgeImport(TypedDict):
    file: str
    checksum: str
    ids: list[str]
    state: Literal["changed", "original", "removed"]
    documents: list[Any]


def calculate_checksum(file_path: str) -> str:
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def load_knowledge(
    log_item: LogItem | None,
    knowledge_dir: str,
    index: Dict[str, KnowledgeImport],
    metadata: dict[str, Any] = {},
    filename_pattern: str = "**/*",
) -> Dict[str, KnowledgeImport]:

    # from python.helpers.memory import Memory

    # Mapping file extensions to corresponding loader classes
    file_types_loaders = {
        "txt": TextLoader,
        "pdf": PyPDFLoader,
        "csv": CSVLoader,
        "html": UnstructuredHTMLLoader,
        # "json": JSONLoader,
        "json": TextLoader,
        # "md": UnstructuredMarkdownLoader,
        "md": TextLoader,
    }

    cnt_files = 0
    cnt_docs = 0

    # for area in Memory.Area:
    #     subdir = files.get_abs_path(knowledge_dir, area.value)

    # if not os.path.exists(knowledge_dir):
    #     os.makedirs(knowledge_dir)
    #     continue

    # Fetch all files in the directory with specified extensions
    kn_files = glob.glob(knowledge_dir + "/" + filename_pattern, recursive=True)
    kn_files = [f for f in kn_files if os.path.isfile(f)]

    if kn_files:
        PrintStyle.standard(
            f"Found {len(kn_files)} knowledge files in {knowledge_dir}, processing..."
        )
        if log_item:
            log_item.stream(
                progress=f"\nFound {len(kn_files)} knowledge files in {knowledge_dir}, processing...",
            )

    for file_path in kn_files:
        ext = file_path.split(".")[-1].lower()
        if ext in file_types_loaders:
            checksum = calculate_checksum(file_path)
            file_key = file_path  # os.path.relpath(file_path, knowledge_dir)

            # Load existing data from the index or create a new entry
            file_data = index.get(file_key, {})

            if file_data.get("checksum") == checksum:
                file_data["state"] = "original"
            else:
                file_data["state"] = "changed"

            if file_data["state"] == "changed":
                file_data["checksum"] = checksum
                loader_cls = file_types_loaders[ext]
                loader = loader_cls(
                    file_path,
                    **(
                        text_loader_kwargs
                        if ext in ["txt", "csv", "html", "md"]
                        else {}
                    ),
                )
                file_data["documents"] = loader.load_and_split()
                for doc in file_data["documents"]:
                    doc.metadata = {**doc.metadata, **metadata}
                cnt_files += 1
                cnt_docs += len(file_data["documents"])
                # PrintStyle.standard(f"Imported {len(file_data['documents'])} documents from {file_path}")

            # Update the index
            index[file_key] = file_data  # type: ignore

    # loop index where state is not set and mark it as removed
    for file_key, file_data in index.items():
        if not file_data.get("state", ""):
            index[file_key]["state"] = "removed"

    PrintStyle.standard(f"Processed {cnt_docs} documents from {cnt_files} files.")
    if log_item:
        log_item.stream(
            progress=f"\nProcessed {cnt_docs} documents from {cnt_files} files."
        )
    return index
