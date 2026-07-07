import re
from extract_text import extract_text_from_pdf

def split_into_sentences(text):
    # Split on sentence-ending punctuation followed by a space and a capital letter or newline
    # This is a simple approach - not perfect (e.g. struggles with abbreviations like "Mr.") but solid for our use case
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text, target_size=500, overlap_sentences=1):
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        current_chunk.append(sentence)
        current_length += len(sentence)

        if current_length >= target_size:
            chunks.append(" ".join(current_chunk))
            # Start next chunk with overlap: carry over the last N sentences for context continuity
            current_chunk = current_chunk[-overlap_sentences:] if overlap_sentences else []
            current_length = sum(len(s) for s in current_chunk)

    # Don't forget the last partial chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# --- Test code only runs when this file is executed directly ---
if __name__ == "__main__":
    print("Script started")
    text = extract_text_from_pdf("textbook.pdf")
    chunks = chunk_text(text)

    print(f"Total chunks created: {len(chunks)}\n")

    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk)
        print()