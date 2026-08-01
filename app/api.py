from fastapi import FastAPI
from pydantic import BaseModel
from app.graph import ask
from app.schemas import AgentResponse

app = FastAPI(title="Reservation Intelligence Data & AI Platform", version="0.1.0")

class AskRequest(BaseModel):
    question: str

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/ask", response_model=AgentResponse)
def ask_endpoint(request: AskRequest) -> AgentResponse:
    return ask(request.question)
