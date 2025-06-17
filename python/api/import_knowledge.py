from python.helpers.api import ApiHandler
from flask import Request, Response

from python.helpers.file_browser import FileBrowser
from python.helpers import files, memory
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timezone # Moved import
import tempfile # Moved import


class ImportKnowledge(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        if "files[]" not in request.files:
            raise Exception("No files part")

        ctxid = request.form.get("ctxid", "")
        if not ctxid:
            raise Exception("No context id provided")

        context = self.get_context(ctxid)

        file_list = request.files.getlist("files[]")
        area = request.form.get("area", "main") # Get area from form data, default to main

        if not context.agent0:
            # This check might be redundant if self.get_context already ensures agent0
            return {"status": "error", "message": "Agent not available"}

        memory_layer = await memory.Memory.get_abstraction_layer(context.agent0)

        processed_files_info = []

        for uploaded_file in file_list:
            if uploaded_file and uploaded_file.filename:
                filename = secure_filename(uploaded_file.filename)
                file_content = None
                tmp_file_path = ""
                try:
                    # Use a temporary file to handle upload reliably
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
                        uploaded_file.save(tmp_file) # Save uploaded file object to temp file
                        tmp_file_path = tmp_file.name

                    # Read content from the temporary file
                    # This part assumes text content. For binary (like PDF), direct MAL ingestion of path or bytes might be needed
                    # or use the FILE_LOADERS from knowledge_import.py if complex parsing is needed.
                    # For this API, let's assume we read raw text content or that MAL handles it.
                    # The prompt's example reads content and passes to insert_content.
                    with open(tmp_file_path, "r", encoding="utf-8", errors="ignore") as f_content:
                        file_content = f_content.read()

                except Exception as e:
                    processed_files_info.append({"filename": filename, "status": "error", "message": f"Failed to read uploaded file: {e}"})
                    continue # Move to next file
                finally:
                    if tmp_file_path and os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)

                if not file_content:
                    processed_files_info.append({"filename": filename, "status": "error", "message": "File is empty or could not be read."})
                    continue

                doc_metadata = {
                    "area": area,
                    "filename": filename,
                    "upload_time": datetime.now(timezone.utc).isoformat(),
                    "source_description": "api_upload"
                }

                try:
                    doc_id = await memory_layer.insert_content(
                        content=file_content,
                        content_type="knowledge_document", # Specify content type
                        metadata=doc_metadata
                    )
                    processed_files_info.append({"filename": filename, "status": "success", "document_id": doc_id})
                except Exception as e:
                    # Log the exception e for debugging on the server
                    print(f"Error during MAL insert_content for file {filename}: {e}")
                    processed_files_info.append({"filename": filename, "status": "error", "message": f"Failed to ingest document: {e}"})
            else:
                processed_files_info.append({"filename": "unknown", "status": "error", "message": "Invalid file in request."})

        # Removed: await memory.Memory.reload(context.agent0)
        # Removed: context.log.set_initial_progress() as it's not clear if it's needed after MAL ingestion

        return {
            "message": "Knowledge import process finished.",
            "processed_files": processed_files_info
        }