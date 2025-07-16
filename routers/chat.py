from fastapi import APIRouter
from pydantic import BaseModel
from rag_engine import query_bot, load_vector_store, answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    bot_name: str
    question: str

class ChatQuery(BaseModel):
    question: str

# Generic chat endpoint using query_bot
@router.post("/chat")
async def chat_with_bot(data: ChatRequest):
    """
    POST /chat
    {
        "bot_name": "garima",
        "question": "What is your return policy?"
    }
    """
    answer = query_bot(data.bot_name, data.question)
    return {"response": answer}  # ✅ Unified response key

# Optional advanced endpoint (loads and answers in separate steps)
@router.post("/chat/{bot_name}")
async def chat(bot_name: str, query: ChatQuery):
    """
    POST /chat/{bot_name}
    {
        "question": "What is your pricing?"
    }
    """
    context_chunks = load_vector_store(bot_name, query.question)
    answer = answer_question(query.question, context_chunks)
    return {"response": answer}  # ✅ Unified response key
