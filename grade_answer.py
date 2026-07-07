import os
import requests
from dotenv import load_dotenv

import streamlit as st

load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
hf_api_key = os.environ.get("HF_API_KEY") or st.secrets.get("HF_API_KEY")


def grade_answer(question, student_answer, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""You are grading a student's answer to a practice question, based on their textbook.

Context from the textbook:
{context}

Question asked: {question}

Student's answer: {student_answer}

Instructions:
Judge whether the student's answer is substantially correct based on the context above. Minor wording differences are fine - focus on whether the core understanding is right. Be encouraging but honest.

Format your response EXACTLY like this:
VERDICT: CORRECT or INCORRECT
FEEDBACK: <one or two sentences of feedback, explaining what was right or what was missed>
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
    result_text = data["choices"][0]["message"]["content"]

    # Parse the structured response into usable pieces
    is_correct = "VERDICT: CORRECT" in result_text
    feedback = result_text.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in result_text else result_text

    return is_correct, feedback


# --- Test it ---
if __name__ == "__main__":
    context = ["DNS acts as a kind of phone book for the internet, translating human-readable domain names such as example.com into the numerical IP address that computers actually use to locate each other."]
    
    question = "What is the primary function of DNS?"
    
    # Test a correct-ish answer
    student_answer_1 = "DNS turns website names like google.com into IP addresses computers can use."
    correct1, feedback1 = grade_answer(question, student_answer_1, context)
    print(f"Answer 1 -> Correct: {correct1}")
    print(f"Feedback: {feedback1}\n")
    
    # Test a wrong answer
    student_answer_2 = "DNS is used to encrypt internet traffic for security."
    correct2, feedback2 = grade_answer(question, student_answer_2, context)
    print(f"Answer 2 -> Correct: {correct2}")
    print(f"Feedback: {feedback2}")