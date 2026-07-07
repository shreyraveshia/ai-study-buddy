from ask_question import retrieve_relevant_chunks, generate_practice_questions
from grade_answer import grade_answer
from progress_tracker import record_attempt, get_weak_topics

def run_practice_session(topic):
    print(f"\n=== Practice Session: {topic} ===\n")

    # Step 1: Get relevant context once, reuse it for question generation AND grading
    context_chunks = retrieve_relevant_chunks(topic, n_results=3)

    # Step 2: Generate ONE practice question (simplify from 3 to 1 for a clean single-question flow)
    questions_text = generate_practice_questions(topic, n_questions=1)
    print("Practice question generated:")
    print(questions_text)

    # Step 3: Get the student's answer
    student_answer = input("\nYour answer: ")

    # Step 4: Grade it
    is_correct, feedback = grade_answer(questions_text, student_answer, context_chunks)

    print(f"\nVerdict: {'Correct!' if is_correct else 'Not quite.'}")
    print(f"Feedback: {feedback}")

    # Step 5: Record progress
    record_attempt(topic, is_correct)

    # Step 6: Show current weak topics
    weak = get_weak_topics()
    if weak:
        print(f"\nTopics you might want to review: {', '.join(weak)}")


# --- Run a real session ---
if __name__ == "__main__":
    run_practice_session("DNS and how domain names work")