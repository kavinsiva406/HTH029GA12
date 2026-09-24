import os, shutil
from fastapi import FastAPI, UploadFile, File #type: ignore
from fastapi.middleware.cors import CORSMiddleware #type: ignore
from dotenv import load_dotenv #type: ignore
load_dotenv()
from database import init_database, seed_database, get_connection
from document_processor import extract_pdf_text, create_chunks
from rag_engine import add_documents
from ai_engine import generate_lesson, ask_coach

app=FastAPI(title="OnboardAI")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
os.makedirs("uploads",exist_ok=True)
init_database(); seed_database()

@app.get("/")
def home(): return {"status":"success","message":"OnboardAI backend is running"}

@app.post("/login")
def login(email:str,password:str):
    c=get_connection(); user=c.execute("SELECT * FROM users WHERE email=? AND password=?",(email,password)).fetchone(); c.close()
    if not user: return {"success":False,"message":"Invalid email or password"}
    return {"success":True,"user":{"id":user["id"],"name":user["name"],"email":user["email"]}}

@app.get("/topics")
def topics():
    c=get_connection(); rows=c.execute("SELECT * FROM topics").fetchall(); c.close(); return [dict(r) for r in rows]

@app.post("/documents/upload")
async def upload_document(file:UploadFile=File(...)):
    if not file.filename.lower().endswith(".pdf"): return {"success":False,"message":"Only PDF files are supported"}
    safe_name=os.path.basename(file.filename); path=os.path.join("uploads",safe_name)
    with open(path,"wb") as buffer: shutil.copyfileobj(file.file,buffer)
    pages=extract_pdf_text(path); chunks=create_chunks(pages); add_documents(chunks,safe_name)
    return {"success":True,"filename":safe_name,"pages":len(pages),"chunks":len(chunks)}

@app.get("/learn/{topic}")
def learn(topic:str): return generate_lesson(topic)

@app.post("/coach")
def coach(data:dict): return ask_coach(data.get("question",""))

@app.post("/quiz/submit")
def quiz_submit(data:dict):
    user_id=data.get("user_id"); topic_id=data.get("topic_id"); score=int(data.get("score",0))
    c=get_connection(); existing=c.execute("SELECT * FROM progress WHERE user_id=? AND topic_id=?",(user_id,topic_id)).fetchone()
    if existing: c.execute("UPDATE progress SET score=?,attempts=attempts+1 WHERE user_id=? AND topic_id=?",(score,user_id,topic_id))
    else: c.execute("INSERT INTO progress(user_id,topic_id,score,attempts) VALUES(?,?,?,1)",(user_id,topic_id,score))
    c.commit(); c.close()
    if score<50: rec="Knowledge gap detected. Review this topic with a simpler explanation and try the quiz again."
    elif score<80: rec="You understand the basics. Practice this topic once more before moving on."
    else: rec="Great job! You are ready for the next topic."
    return {"score":score,"recommendation":rec}

@app.get("/progress/{user_id}")
def progress(user_id:int):
    c=get_connection(); rows=c.execute("SELECT progress.topic_id,topics.title,progress.score,progress.attempts FROM progress JOIN topics ON topics.id=progress.topic_id WHERE progress.user_id=?",(user_id,)).fetchall(); c.close(); return [dict(r) for r in rows]
