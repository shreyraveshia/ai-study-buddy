import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import chromadb
from chunk_text import chunk_text
from extract_text import extract_text_from_pdf

load_dotenv()
hf_api_key = os.environ.get("HF_API_KEY")

client = InferenceClient(
    provider="hf-inference",
    api_key=hf_api_key
)

def get_embedding(text):
    result = client.feature_extraction(
        text,
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    return result.tolist()  # ChromaDB wants a plain list, not a numpy array

# --- Step A: Set up ChromaDB (a local, persistent vector database) ---
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # saves to disk in this folder
collection = chroma_client.get_or_create_collection(name="study_buddy_chunks")

# --- Step B: Get our chunks and store them (only do this once, not every run) ---
text = extract_text_from_pdf("textbook.pdf")
chunks = chunk_text(text)

print("Embedding and storing chunks...")
for i, chunk in enumerate(chunks):
    embedding = get_embedding(chunk)
    collection.add(
        ids=[f"chunk_{i}"],           # unique ID for each chunk
        embeddings=[embedding],        # the vector
        documents=[chunk]              # the original text (so we can retrieve it later)
    )
    print(f"Stored chunk {i+1}/{len(chunks)}")

print("\nAll chunks stored in ChromaDB!")

# --- Step C: Test retrieval - ask a question, find the most relevant chunk(s) ---
question = "What is the difference between HTTP and HTTPS?"
question_embedding = get_embedding(question)

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=2  # get the top 2 most relevant chunks
)

print(f"\n--- QUESTION: {question} ---")
print("\n--- MOST RELEVANT CHUNKS FOUND ---")
for i, doc in enumerate(results["documents"][0]):
    print(f"\nMatch {i+1}:")
    print(doc)