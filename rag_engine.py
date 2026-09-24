import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="company_documents")

def add_documents(chunks, filename):
    for index, chunk in enumerate(chunks):
        document_id=f"{filename}_{index}"
        try:
            collection.add(ids=[document_id], documents=[chunk["text"]],
                           metadatas=[{"filename":filename,"page":chunk["page"]}])
        except Exception as exc:
            print(f"Skipping {document_id}: {exc}")

def search_documents(query, limit=5):
    if not query.strip(): return []
    result=collection.query(query_texts=[query], n_results=limit)
    documents=result.get("documents",[[]])[0]
    metadatas=result.get("metadatas",[[]])[0]
    return [{"text":d,"document":m.get("filename","Unknown"),"page":m.get("page",0)} for d,m in zip(documents,metadatas)]
