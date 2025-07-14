# rag_engine.py

import os
import faiss
import json
import numpy as np
from openai import OpenAI
from utils.chunker import split_into_chunks
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VECTOR_STORE_DIR = "vectorstores"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

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

# === Load + Query Vector Store ===
def load_vector_store(bot_name: str, query: str, top_k: int = 3) -> list[str]:
    index_path = f"{VECTOR_STORE_DIR}/{bot_name}.index"
    meta_path = f"{VECTOR_STORE_DIR}/{bot_name}_meta.json"

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("Vector store not found. Please build it first.")

    # Load FAISS index
    index = faiss.read_index(index_path)

    # Load metadata
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Embed query
    query_vec = embed_text(query)
    D, I = index.search(np.array([query_vec]).astype('float32'), top_k)

    # Get top chunks
    top_chunks = [metadata[i]["text"] for i in I[0]]
    return top_chunks

# === Answer Generation ===
def answer_question(query: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a helpful assistant. Use the following context to answer the question.

Context:
{context}

Question: {query}
Answer:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()
