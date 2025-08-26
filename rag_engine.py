import os
import faiss
import json
import numpy as np
from openai import AzureOpenAI
from utils.chunker import split_into_chunks
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
)

VECTOR_STORE_DIR = "vectorstores"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# === Generate embedding for input text ===
def embed_text(text: str) -> list[float]:
    response = client.embeddings.create(
        input=[text],
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Use deployment name, not model name
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
            temperature=0.7
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
    raw_path = f"uploads/{bot_name}/raw_text.txt"
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No raw text file found at {raw_path}")

    with open(raw_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    print(f"Total characters in raw text: {len(full_text)}")  # Debug
    chunks = split_into_chunks(full_text)
    print(f"Chunks generated: {len(chunks)}")  # Debug

    if not chunks:
        raise ValueError("No text chunks generated. Check your raw text file and chunking logic.")

    embeddings = []
    metadata = []

    for i, chunk in enumerate(chunks):
        emb = embed_text(chunk)
        embeddings.append(emb)
        metadata.append({"id": i, "text": chunk})

    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))

    index_path = f"{VECTOR_STORE_DIR}/{bot_name}.index"
    meta_path = f"{VECTOR_STORE_DIR}/{bot_name}_meta.json"

    faiss.write_index(index, index_path)
    with open(meta_path, "w", encoding="utf-8") as meta_file:
        json.dump(metadata, meta_file, indent=2)

    print(f"🧠 Vector index saved at: {index_path}")
    print(f"📑 Metadata saved at: {meta_path}")

# === Load the vector store and return top-k chunks ===
def load_vector_store(bot_name: str, query: str, top_k: int = 3) -> list[str]:
    index_path = f"{VECTOR_STORE_DIR}/{bot_name}.index"
    meta_path = f"{VECTOR_STORE_DIR}/{bot_name}_meta.json"

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise FileNotFoundError("❌ Vector store not found. Please build it first.")

    print(f"🔍 Loading vector store for bot: {bot_name}")
    index = faiss.read_index(index_path)

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    query_vec = embed_text(query)
    D, I = index.search(np.array([query_vec]).astype('float32'), top_k)

    top_chunks = [metadata[i]["text"] for i in I[0]]
    print(f"🎯 Top {top_k} chunks retrieved for query: \"{query}\"")
    return top_chunks

# === Main entry point to query the bot ===
def query_bot(bot_name: str, question: str) -> str:
    print(f"💬 Querying bot: {bot_name} | Question: {question}")
    context_chunks = load_vector_store(bot_name, question)
    return answer_question(question, context_chunks)
