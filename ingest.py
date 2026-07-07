from huggingface_hub import InferenceClient
import chromadb
import os
from dotenv import load_dotenv
from chunk_text import chunk_text
from extract_text import extract_text_from_pdf

load_dotenv()
hf_api_key = os.environ.get("HF_API_KEY")

hf_client = InferenceClient(provider="hf-inference", api_key=hf_api_key)

def get_embedding(text):
    result = hf_client.feature_extraction(text, model="sentence-transformers/all-MiniLM-L6-v2")
    return result.tolist()

def ingest_pdf(pdf_path, progress_callback=None):
    """
    Extracts, chunks, embeds, and stores a PDF into ChromaDB.
    Clears any previously stored document first, so each upload starts fresh.
    progress_callback: optional function(current, total) to report progress to a UI.
    """
    # Fresh database each time - start clean per upload
    chroma_client = chromadb.PersistentClient(path="./chroma_db")

    # Delete old collection if it exists, so we don't mix documents
    try:
        chroma_client.delete_collection(name="study_buddy_chunks")
    except Exception:
        pass  # collection didn't exist yet - that's fine

    collection = chroma_client.get_or_create_collection(name="study_buddy_chunks")

    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk]
        )
        if progress_callback:
            progress_callback(i + 1, len(chunks))

    return len(chunks)