import os
import time
import uuid
from typing import Dict, Any
from PyPDF2 import PdfReader
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings 
from taskfiles.firebase import db
from datetime import datetime




embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": False},
)

def initialize_vectors_function(file_data: bytes, filename: str, web_url: str) -> Dict[str, Any]:
    try:
        print("Initializing vector store DB...")
        st = time.time()

        unique_id = str(uuid.uuid4())
        folder_path = f"./store/{unique_id}"
        os.makedirs(folder_path, exist_ok=True)

        file_extension = filename.split(".")[-1].lower()
        if file_extension not in ["txt", "pdf"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only .txt and .pdf are supported.")

        file_path = f"{folder_path}/uploaded_file.{file_extension}"
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)

        if file_extension == "txt":
            with open(file_path, "r") as f:
                txt_data = f.read()

        elif file_extension == "pdf":
            reader = PdfReader(file_path)
            txt_data = "\n\n".join(page.extract_text() for page in reader.pages)

        else:
            raise HTTPException(status_code=400, detail="File processing not implemented for this format.")

        chunks = txt_data.split("\n\n")
        final_documents = [Document(page_content=chunk) for chunk in chunks]

        vectors = FAISS.from_documents(final_documents, embeddings)
        vectors.save_local(folder_path=folder_path, index_name="index")

        timestamp = datetime.utcnow().strftime("%d %B %Y at %H:%M:%S UTC")

        data = {
            "file_id": filename,
            "id": unique_id,
            "timestamp": timestamp,
            "url": web_url  
        }
        db.collection("user_data").document(unique_id).set(data)

        elapsed_time = time.time() - st
        print({'time': elapsed_time})
        print("Vector store DB is set up and ready!")
        return {
            "status": "success",
            "message": "Vector store DB initialized.",
            "time_taken": elapsed_time,
            "id": unique_id
        }

    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Temporary file {file_path} removed.")
