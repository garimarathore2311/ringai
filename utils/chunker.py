# utils/chunker.py

import tiktoken
import nltk
from nltk.tokenize import sent_tokenize

import os

# Ensure custom nltk path is added
nltk.data.path.append(os.path.join(os.getcwd(), "nltk_data"))

# Download punkt only if missing
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

def split_into_chunks(text: str, max_tokens: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits input text into sentence-based chunks, each limited by token count,
    with configurable overlap for better context retention.

    Args:
        text (str): The input full text to split.
        max_tokens (int): Maximum tokens per chunk (default: 500).
        overlap (int): Number of overlapping tokens to retain from the previous chunk (default: 50).

    Returns:
        list[str]: List of text chunks.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    sentences = sent_tokenize(text)

    chunks = []
    current_chunk = []
    current_token_count = 0
    token_cache = [encoding.encode(s) for s in sentences]

    for sentence, tokens in zip(sentences, token_cache):
        token_len = len(tokens)

        # If adding this sentence exceeds limit, finalize current chunk
        if current_token_count + token_len > max_tokens:
            chunks.append(" ".join(current_chunk))

            # Prepare next chunk with overlap
            overlap_chunk = []
            overlap_tokens = 0
            for prev_sent in reversed(current_chunk):
                prev_tokens = encoding.encode(prev_sent)
                if overlap_tokens + len(prev_tokens) > overlap:
                    break
                overlap_chunk.insert(0, prev_sent)
                overlap_tokens += len(prev_tokens)

            current_chunk = overlap_chunk + [sentence]
            current_token_count = sum(len(encoding.encode(s)) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_token_count += token_len

    # Add remaining chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))



    print(f"🧩 Created {len(chunks)} sentence-based chunks (max_tokens={max_tokens}, overlap={overlap})")
    return chunks
