import fitz

def extract_pdf_text(file_path):
    document = fitz.open(file_path)
    pages=[]
    for page_number,page in enumerate(document):
        text=page.get_text()
        if text.strip(): pages.append({"page":page_number+1,"text":text})
    document.close(); return pages

def create_chunks(pages, chunk_size=1200):
    chunks=[]
    for page in pages:
        text=page["text"]
        for start in range(0,len(text),chunk_size):
            chunk=text[start:start+chunk_size].strip()
            if chunk: chunks.append({"text":chunk,"page":page["page"]})
    return chunks
