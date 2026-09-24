import os
from openai import OpenAI
from rag_engine import search_documents

api_key=os.getenv("OPENAI_API_KEY")
client=OpenAI(api_key=api_key) if api_key and api_key != "YOUR_OPENAI_API_KEY" else None
MODEL=os.getenv("OPENAI_MODEL","gpt-5")

def _ask(prompt):
    if not client:
        return "AI is not configured yet. Add your OPENAI_API_KEY to backend/.env and restart the backend."
    response=client.responses.create(model=MODEL,input=prompt)
    return response.output_text

def generate_lesson(topic):
    sources=search_documents(topic)
    context="\n\n".join(s["text"] for s in sources) or "No internal document information was found."
    prompt=f"""You are an employee onboarding coach.\nTopic: {topic}\nInternal company information:\n{context}\nCreate a simple onboarding lesson with: 1. Simple explanation 2. Three important points 3. One practical workplace example 4. One short recap. Use only the provided company information. Do not invent company-specific rules."""
    return {"answer":_ask(prompt),"sources":sources}

def ask_coach(question):
    sources=search_documents(question)
    context="\n\n".join(s["text"] for s in sources) or "No relevant internal document was found."
    prompt=f"""You are an internal employee onboarding assistant.\nEmployee question: {question}\nRelevant company information:\n{context}\nAnswer clearly and briefly. Use only the provided information. If unavailable, say it is not available in the provided company documents."""
    return {"answer":_ask(prompt),"sources":sources}
