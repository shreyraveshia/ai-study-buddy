# pyrefly: ignore [missing-import]
import pdfplumber

def extract_text_from_pdf(pdf_path):
    all_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:  # some pages might be blank or have extraction issues
                all_text += page_text + "\n"
            else:
                print(f"Warning: no text found on page {i+1}")
    
    return all_text

# Test it
text = extract_text_from_pdf("textbook.pdf")
print("\n--- FIRST 1000 CHARACTERS ---\n")
print(text[:1000])
print(f"\n--- TOTAL CHARACTERS EXTRACTED: {len(text)} ---")