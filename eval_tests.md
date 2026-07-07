# Study Buddy - Evaluation Test Set
Document used: networking_basics.pdf

## Retrieval + Grounded Q&A
| # | Question | Expected behavior | Status |
|---|----------|-------------------|--------|
| 1 | What is the difference between HTTP and HTTPS? | Retrieves Ch.5, accurate grounded answer | ✅ Pass |
| 2 | What does 192.168.1.1 represent, how many devices can IPv4 support? | Retrieves Ch.3, correct facts (4.3 billion) | ✅ Pass |
| 3 | What does a firewall do? | Retrieves Ch.6 | ✅ Pass |
| 4 | What is machine learning and how do neural networks work? | Off-topic - model should refuse, not hallucinate | ✅ Pass |

## Practice Question Generation
| # | Topic | Expected behavior | Status |
|---|-------|--------------------|--------|
| 5 | DNS and how domain names work | Generates 1 relevant question, no preamble | ✅ Pass |
| 6 | quantum computing | Off-topic - returns NOT_COVERED signal, UI shows warning | ✅ Pass |

## AI Grading
| # | Scenario | Expected behavior | Status |
|---|----------|--------------------|--------|
| 7 | Correct, well-phrased answer | Marked CORRECT | ✅ Pass |
| 8 | Wrong/irrelevant answer (e.g. "Virat Kohli") | Marked INCORRECT, feedback names the gap | ✅ Pass |

## Session/State Isolation
| # | Scenario | Expected behavior | Status |
|---|----------|--------------------|--------|
| 9 | Upload new PDF mid-session | Progress resets, old question/answer cleared, inputs cleared | ✅ Pass |
| 10 | Generate new practice question | Old answer text cleared automatically | ✅ Pass |
| 11 | Submit blank answer | Silently does nothing, no crash | ✅ Pass |

## Known limitations (documented, not "bugs")
- Sentence-splitting regex can misfire on abbreviations (e.g. "Mr.", "Dr.") - acceptable tradeoff for this project's scope; a production system would use a proper NLP sentence tokenizer (e.g. nltk).
- Small/fast Groq model (llama-3.1-8b-instant) occasionally introduces minor unrequested details when generating practice questions (mild hallucination), even with grounding instructions - observed once during testing.
- Progress tracking is session-scoped only (resets on page reload) - a deliberate tradeoff since there's no user authentication; a future version would add accounts + a real database for persistent, per-user history.
- Not yet tested at scale with a very long (30+ page) document - ingestion time and rate limits with Hugging Face/Groq free tiers are unverified beyond ~20 chunks.