# 📖 Study Buddy — AI-Powered Tutor for Your Own Notes

**[Live demo →](https://ai-study-buddy-dbkvv39yujsqdp2kfr6vt4.streamlit.app/)**

Upload any PDF (textbook, lecture notes, technical docs) and get a tutor that answers questions grounded in *that specific document*, generates practice questions, grades your answers, and tracks which topics you're weak on — all running on free-tier APIs, no local model downloads required.

## Why this exists

Generic AI chatbots answer from their general training, not from your specific material — which means they can't tell you exactly what *your* professor, *your* textbook, or *your* company's documentation actually says. Study Buddy solves this with Retrieval-Augmented Generation (RAG): it reads your document, and every answer it gives is explicitly grounded in the retrieved passages, with a built-in refusal when a question falls outside what the document covers.

## What it does

- **Upload** any text-based PDF and it's automatically chunked, embedded, and indexed
- **Ask questions** and get answers grounded in the document, with a follow-up question that nudges deeper understanding (Socratic-style tutoring, not just Q&A)
- **Generate practice questions** on any topic — and it honestly tells you if that topic isn't covered in your document, rather than making something up
- **Get AI-graded feedback** on your practice answers, with specific, constructive feedback
- **Track topic mastery** with a visual progress bar per topic, color-coded by how well you're doing

## Architecture

```
PDF Upload
   │
   ▼
Text Extraction (pdfplumber)
   │
   ▼
Sentence-Aware Chunking (custom, regex-based sentence splitting + size-based grouping)
   │
   ▼
Embeddings (Hugging Face Inference API — sentence-transformers/all-MiniLM-L6-v2)
   │
   ▼
Vector Storage (ChromaDB, local persistent store)
   │
   ▼
Query → Semantic Search → Top-K relevant chunks
   │
   ▼
Grounded Generation (Groq API — Llama 3.1 8B) with structured prompting:
   - Answer + Socratic follow-up
   - Practice question generation (with explicit "not covered" signal)
   - Answer grading (verdict + feedback)
   │
   ▼
Streamlit UI (session-scoped state, no persistent user data)
```

## Tech stack

| Piece | Choice | Why |
|---|---|---|
| LLM | Groq (Llama 3.1 8B Instant) | Free tier, very fast inference |
| Embeddings | Hugging Face Inference API (MiniLM-L6-v2) | Free, no local download needed |
| Vector DB | ChromaDB | Free, local, zero setup |
| PDF parsing | pdfplumber | Clean text extraction |
| UI | Streamlit | Fast to build, free Community Cloud hosting |

**Zero paid APIs anywhere in this stack** — the whole project runs on free tiers by design.

## What I learned building this

- **RAG fundamentals**: chunking, embeddings, vector similarity search, and why grounding a prompt with retrieved context is different from just "asking an AI a question"
- **Chunking strategy directly affects retrieval quality** — naive character-count chunking produced mid-sentence cuts that measurably hurt retrieval; switching to sentence-aware chunking fixed this, and seeing that difference concretely was one of the most useful lessons of the whole project
- **Retrieval and grounding are separate concerns** — a vector database will always return its "closest" match even when nothing is truly relevant; whether the system then *uses* that correctly (or honestly says "I don't know") is a separate, deliberately-tested prompt-engineering problem
- **Structured output parsing** (`ANSWER:`/`FOLLOW-UP:`, `VERDICT:`/`FEEDBACK:`, `NOT_COVERED:`) makes AI responses reliably usable in code — free-form text is hard to build UI logic around
- **Session state management in Streamlit** — and the real product implications of *not* designing for multi-user isolation from the start (progress mixing between documents/users was a real bug I hit and fixed)
- **AI graders can be tested for leniency** — verifying the grader actually fails a wrong answer (not just rubber-stamping everything "correct") was an important, non-obvious test

## Known limitations

- **Sentence-splitting is regex-based**, not a full NLP tokenizer — it can misfire on abbreviations (e.g., "Dr.", "Mr."). A production version would use a library like `nltk` for this.
- **Small/fast model occasionally introduces minor unrequested details** when generating practice questions, even with grounding instructions — observed during testing. Larger models would likely reduce this.
- **Progress tracking is session-scoped**, not persistent across visits — a deliberate tradeoff since there's no user authentication. A future version would add accounts and a real database for durable, per-user history.
- **Free-tier rate limits** on Hugging Face and Groq mean ingestion time scales with document length one API call per chunk; a production version would batch embedding requests.

## Running it locally

```bash
git clone https://github.com/shreyraveshia/ai-study-buddy.git
cd ai-study-buddy
python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file with:
```
GROQ_API_KEY=your_key_here
HF_API_KEY=your_key_here
```

Then run:
```bash
streamlit run app.py
```

Both API keys are free — [Groq Console](https://console.groq.com) and [Hugging Face](https://huggingface.co/settings/tokens).
