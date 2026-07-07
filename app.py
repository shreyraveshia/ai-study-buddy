import streamlit as st
import os
from ingest import ingest_pdf
from ask_question import retrieve_relevant_chunks, ask_groq_with_context, generate_practice_questions
from grade_answer import grade_answer

st.set_page_config(page_title="Study Buddy", page_icon="📖", layout="centered")

# --- Custom styling: fonts, hero banner, mastery bars ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    color: #2E2B26 !important;
}

.hero {
    padding: 1.75rem 2rem;
    background: linear-gradient(135deg, #F3EBDA 0%, #ECE1C8 100%);
    border-radius: 14px;
    border: 1px solid #E3D5B8;
    margin-bottom: 1.75rem;
}
.hero h1 {
    font-size: 2.1rem;
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.5px;
}
.hero p {
    font-family: 'Inter', sans-serif;
    color: #6B6355;
    margin: 0;
    font-size: 0.98rem;
}

.mastery-row {
    margin-bottom: 0.9rem;
}
.mastery-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.92rem;
    margin-bottom: 0.3rem;
    color: #2E2B26;
}
.mastery-track {
    background: #E9E0CC;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
}
.mastery-fill {
    height: 100%;
    border-radius: 6px;
}

div.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    border-radius: 8px;
}
</style>

<div class="hero">
    <h1>📖 Study Buddy</h1>
    <p>Upload your notes. Ask real questions. Practice until it sticks.</p>
</div>
""", unsafe_allow_html=True)

st.set_page_config(page_title="AI Study Buddy", page_icon="📚")
st.title("📚 AI Study Buddy")

# --- Session state initialization ---
if "document_ready" not in st.session_state:
    st.session_state.document_ready = False

if "progress" not in st.session_state:
    st.session_state.progress = {}

if "document_version" not in st.session_state:
    st.session_state.document_version = 0

if "question_counter" not in st.session_state:
    st.session_state.question_counter = 0

tab1, tab2, tab3 = st.tabs(["📄 Upload", "💬 Ask Questions", "✏️ Practice Mode"])

# --- TAB 1: Upload ---
with tab1:
    st.header("Upload your textbook or notes (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file is not None:
        if st.button("Process this document"):
            temp_path = "uploaded_temp.pdf"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            progress_bar = st.progress(0, text="Starting...")

            def update_progress(current, total):
                progress_bar.progress(current / total, text=f"Embedding chunk {current}/{total}...")

            num_chunks = ingest_pdf(temp_path, progress_callback=update_progress)

            st.session_state.document_ready = True
            st.session_state.progress = {}
            st.session_state.document_version += 1
            st.session_state.question_counter += 1
            st.session_state.pop("current_question", None)
            st.session_state.pop("current_context", None)
            st.session_state.pop("current_topic", None)

            st.success(f"Done! Processed into {num_chunks} chunks. Ready to use in the other tabs.")

# --- TAB 2: Ask Questions ---
with tab2:
    st.header("Ask a question about your document")

    if not st.session_state.document_ready:
        st.info("Upload and process a document first in the Upload tab.")
    else:
        question = st.text_input(
            "Your question:",
            key=f"question_input_{st.session_state.document_version}"
        )
        if st.button("Ask") and question:
            with st.spinner("Thinking..."):
                relevant_chunks = retrieve_relevant_chunks(question)
                answer_text = ask_groq_with_context(question, relevant_chunks)

            if "FOLLOW-UP:" in answer_text:
                answer_part, followup_part = answer_text.split("FOLLOW-UP:")
                answer_part = answer_part.replace("ANSWER:", "").strip()
                followup_part = followup_part.strip()
            else:
                answer_part = answer_text
                followup_part = None

            st.markdown(f"**Answer:** {answer_part}")
            if followup_part and followup_part.lower() != "none":
                st.info(f"🤔 Think about this: {followup_part}")

            with st.expander("See the textbook passages used for this answer"):
                for chunk in relevant_chunks:
                    st.write(chunk)
                    st.divider()

# --- TAB 3: Practice Mode ---
with tab3:
    st.header("Practice questions")

    if not st.session_state.document_ready:
        st.info("Upload and process a document first in the Upload tab.")
    else:
        topic = st.text_input(
            "What topic do you want to practice?",
            key=f"topic_input_{st.session_state.document_version}"
        )

        if st.button("Generate a practice question") and topic:
            with st.spinner("Generating question..."):
                context_chunks = retrieve_relevant_chunks(topic, n_results=3)
                question_text = generate_practice_questions(topic, n_questions=1)

            if question_text.strip().startswith("NOT_COVERED:"):
                reason = question_text.split("NOT_COVERED:")[1].strip()
                st.warning(f"⚠️ This topic doesn't seem to be covered in your document. {reason}")
                st.session_state.pop("current_question", None)
                st.session_state.pop("current_context", None)
                st.session_state.pop("current_topic", None)
            else:
                st.session_state.current_question = question_text
                st.session_state.current_context = context_chunks
                st.session_state.current_topic = topic
                st.session_state.question_counter += 1

        if "current_question" in st.session_state:
            st.markdown(f"**Question:** {st.session_state.current_question}")
            student_answer = st.text_area(
                "Your answer:",
                key=f"answer_box_{st.session_state.question_counter}"
            )

            if st.button("Submit answer") and student_answer:
                with st.spinner("Grading..."):
                    is_correct, feedback = grade_answer(
                        st.session_state.current_question,
                        student_answer,
                        st.session_state.current_context
                    )

                topic_key = st.session_state.current_topic
                if topic_key not in st.session_state.progress:
                    st.session_state.progress[topic_key] = {"correct": 0, "incorrect": 0}
                if is_correct:
                    st.session_state.progress[topic_key]["correct"] += 1
                else:
                    st.session_state.progress[topic_key]["incorrect"] += 1

                if is_correct:
                    st.success(f"✅ Correct! {feedback}")
                else:
                    st.error(f"❌ Not quite. {feedback}")

        st.divider()
        st.subheader("Your progress")
        if st.session_state.progress:
            for t, stats in st.session_state.progress.items():
                total = stats["correct"] + stats["incorrect"]
                accuracy = stats["correct"] / total if total > 0 else 0
                pct = int(accuracy * 100)

                if accuracy >= 0.7:
                    bar_color = "#6B8F71"  # sage green - strong
                elif accuracy >= 0.4:
                    bar_color = "#C89B4A"  # amber - shaky
                else:
                    bar_color = "#B5563F"  # muted brick - weak

                st.markdown(f"""
                <div class="mastery-row">
                    <div class="mastery-label">
                        <span><strong>{t}</strong></span>
                        <span>{stats['correct']}/{total} correct ({pct}%)</span>
                    </div>
                    <div class="mastery-track">
                        <div class="mastery-fill" style="width:{pct}%; background:{bar_color};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            weak = [t for t, s in st.session_state.progress.items()
                    if (s["correct"] + s["incorrect"]) > 0 and s["correct"] / (s["correct"] + s["incorrect"]) < 0.5]
            if weak:
                st.warning(f"📌 Topics to review: {', '.join(weak)}")
        else:
            st.write("No practice attempts yet — generate a question above to get started.")