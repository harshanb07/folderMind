
from fastapi import FastAPI
from pydantic import BaseModel

from .ask import ask_foldermind

# Create the FastAPI application
app = FastAPI(title="FolderMind")


# Define what the frontend must send
class AskRequest(BaseModel):
    question: str


# Health-check endpoint
@app.get("/health")
def health():
    return {"status": "running"}


# Question-answering endpoint
@app.post("/ask")
def ask(request: AskRequest):
    answer = ask_foldermind(
        username="alex",
        question=request.question
    )

    return {"answer": answer}
