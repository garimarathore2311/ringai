import os
import faiss
import json
import numpy as np
from openai import OpenAI
from utils.chunker import split_into_chunks
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_DIR = "vectorstores"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# === Generate embedding for input text ===
def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# === Format prompt clearly ===
def format_prompt(question: str, context: str) -> str:
    return f"""
You are a helpful assistant trained to answer questions using only the context provided below. Do not make up answers. If the answer is not in the context, just say: "Sorry, I couldn't find that in the provided information."

Be clear, conversational, and helpful in your tone.

Context:
{context}

Question: {question}
Answer:"""

# === Answer the question using context chunks ===
def answer_question(query: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)
    prompt = format_prompt(query, context)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant who only answers using the context provided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # more natural tone
        )
        answer = response.choices[0].message.content.strip()
        if not answer or answer.lower() in ["undefined", "none"]:
            return "Sorry, I couldn't find that in the provided information."
        return answer

    except Exception as e:
        print("❌ [ERROR in answer_question]:", e)
        return "Something went wrong while generating the answer."

# === Build the FAISS vector store from raw text ===
def build_vector_store(bot_name: str):
    raw_path = f"uploads/{bot_name}_raw.txt"
    if not os.path.exists(raw_path):
        raise FileNotFoundError("No raw text file found.")

    with open(raw_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    chunks = split_into_chunks(full_text)
    embeddings = []
    metadata = []

    for i, chunk in enumerate(chunks):
        emb = embed_text(chunk)
        embeddings.append(emb)
        metadata.append({"id": i, "text": chunk})

    # Save FAISS index
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))

    faiss.write_index(index, f"{VECTOR_STORE_DIR}/{bot_name}.index")

    # Save metadata
    with open(f"{VECTOR_STORE_DIR}/{bot_name}_meta.json", "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=2)

    print(f"✅ Vector store built for {bot_name}")

# === Load the vector store and return top-k chunks ===
def load_vector_store(bot_name: str, query: str, top_k: int = 3) -> list[str]:
    index_path = f"{VECTOR_STORE_DIR}/{bot_name}.index"
    meta_path = f"{VECTOR_STORE_DIR}/{bot_name}_meta.json"

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Vector store not found. Please build it first.")

    index = faiss.read_index(index_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query_vec = embed_text(query)
    D, I = index.search(np.array([query_vec]).astype('float32'), top_k)

    top_chunks = [metadata[i]["text"] for i in I[0]]
    return top_chunks

# === Main entry point to query the bot ===
def query_bot(bot_name: str, question: str) -> str:
    context_chunks = load_vector_store(bot_name, question)
    return answer_question(question, context_chunks)
