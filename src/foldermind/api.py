
from fastapi import FastAPI
from pydantic import BaseModel #library that validates data

from .ask import ask_foldermind
from pathlib import Path
from fastapi.responses import FileResponse

# Create the FastAPI application
app = FastAPI(title="FolderMind")
PROJECT_ROOT = Path(__file__).resolve().parents[2]


@app.get("/")
def frontend():
    return FileResponse(PROJECT_ROOT / "static" / "index.html")


# Define what the frontend must send
class AskRequest(BaseModel):
    question: str


# Health-check endpoint
@app.get("/health") #when someone makes an http get request to /health, execute the function below
def health():
    return {"status": "running"}


# Question-answering endpoint
@app.post("/ask") #when someone sends http POST to /ask, run below
def ask(request: AskRequest):
    answer = ask_foldermind(
        username="alex",
        question=request.question
    )

    return {"answer": answer}
