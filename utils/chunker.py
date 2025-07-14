# utils/chunker.py

import tiktoken

def split_into_chunks(text, max_tokens=500):
    encoding = tiktoken.get_encoding("cl100k_base")
    words = text.split()
    chunks = []
    current_chunk = []

    total_tokens = 0

    for word in words:
        token_count = len(encoding.encode(word))
        if total_tokens + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            total_tokens = token_count
        else:
            current_chunk.append(word)
            total_tokens += token_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
