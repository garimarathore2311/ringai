from fastapi import APIRouter, Request
from pydantic import BaseModel
from rag_engine import load_vector_store, answer_question

router = APIRouter()

class ChatQuery(BaseModel):
    question: str

@router.post("/chat/{bot_name}")
async def chat(bot_name: str, query: ChatQuery):
    context_chunks = load_vector_store(bot_name, query.question)
    answer = answer_question(query.question, context_chunks)
    return {"answer": answer}
