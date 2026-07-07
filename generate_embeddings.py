import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
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
    return result

# Get our chunks
text = extract_text_from_pdf("textbook.pdf")
chunks = chunk_text(text)

# Embed ALL chunks
all_embeddings = []

for i, chunk in enumerate(chunks):
    print(f"Embedding chunk {i+1}/{len(chunks)}...")
    emb = get_embedding(chunk)
    all_embeddings.append(emb)

print(f"\nDone! Generated {len(all_embeddings)} embeddings.")
print(f"Each embedding has {len(all_embeddings[0])} numbers.")