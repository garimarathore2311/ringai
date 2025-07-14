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

    # Save metadata separately
    with open(f"{VECTOR_STORE_DIR}/{bot_name}_meta.json", "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=2)

    print(f"✅ Vector store built for {bot_name}")
