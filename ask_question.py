import os
import requests
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import chromadb

load_dotenv()
hf_api_key = os.environ.get("HF_API_KEY")
groq_api_key = os.environ.get("GROQ_API_KEY")

hf_client = InferenceClient(provider="hf-inference", api_key=hf_api_key)

def get_embedding(text):
    result = hf_client.feature_extraction(text, model="sentence-transformers/all-MiniLM-L6-v2")
    return result.tolist()

def retrieve_relevant_chunks(question, n_results=3):
    # Reconnect fresh each call, so we always see the latest ingested document
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="study_buddy_chunks")
    
    question_embedding = get_embedding(question)
    results = collection.query(query_embeddings=[question_embedding], n_results=n_results)
    return results["documents"][0]

def ask_groq_with_context(question, context_chunks):
    context = "\n\n".join(context_chunks)
    
    prompt = f"""You are a patient, encouraging tutor helping a student learn from their textbook.

Context from the textbook:
{context}

Student's question: {question}

Instructions:
1. Answer the question clearly and accurately, using ONLY the context provided. If the context doesn't contain enough information, say so honestly instead of guessing.
2. After your answer, if it makes sense pedagogically, ask ONE short follow-up question that checks the student's understanding or nudges them to think one step further. Keep it conversational, not robotic. If the question was very simple or factual, you can skip the follow-up.

Format your response as:
ANSWER: <your answer>
FOLLOW-UP: <your follow-up question, or "None" if not applicable>
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_api_key}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


def generate_practice_questions(topic, n_questions=1):
    relevant_chunks = retrieve_relevant_chunks(topic, n_results=3)
    context = "\n\n".join(relevant_chunks)

    prompt = f"""You are a tutor creating a practice question for a student, based on their textbook.

Context from the textbook:
{context}

The student wants to practice: "{topic}"

Instructions:
- First, check if the context above actually contains real information related to "{topic}".
- If it does NOT, respond with EXACTLY this format and nothing else:
NOT_COVERED: <one short sentence explaining the topic isn't in this document>
- If it DOES contain relevant information, generate EXACTLY {n_questions} practice question(s) about "{topic}" based ONLY on the context above. Output ONLY the question(s), numbered, nothing else - no preamble, no extra commentary.

Format when covered:
1. ...
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_api_key}"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]


# --- Test code only runs when this file is executed directly, not when imported ---
if __name__ == "__main__":
    question = "What is the difference between HTTP and HTTPS?"
    relevant_chunks = retrieve_relevant_chunks(question)

    print("--- RETRIEVED CONTEXT ---")
    for chunk in relevant_chunks:
        print(chunk[:150] + "...\n")

    answer = ask_groq_with_context(question, relevant_chunks)

    print("--- FINAL ANSWER ---")
    print(answer)

    print("\n\n--- PRACTICE QUESTIONS TEST ---")
    practice_questions = generate_practice_questions("DNS and how domain names work")
    print(practice_questions)