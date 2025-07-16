# utils/chunker.py

import tiktoken
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def split_into_chunks(text, max_tokens=500, overlap=50):
    """
    Sentence-aware token-limited chunking with overlap.

    Args:
        text (str): The full input text.
        max_tokens (int): Max token count per chunk.
        overlap (int): Approximate number of tokens to retain from the end of the previous chunk.
    
    Returns:
        List[str]: A list of well-formed text chunks.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    sentences = sent_tokenize(text)

    chunks = []
    current_chunk = []
    total_tokens = 0

    for sentence in sentences:
        sent_tokens = encoding.encode(sentence)
        token_len = len(sent_tokens)

        if total_tokens + token_len > max_tokens:
            # Save current chunk
            chunks.append(" ".join(current_chunk))

            # Add overlap
            overlap_tokens = 0
            overlap_chunk = []
            for prev_sent in reversed(current_chunk):
                prev_token_len = len(encoding.encode(prev_sent))
                if overlap_tokens + prev_token_len > overlap:
                    break
                overlap_chunk.insert(0, prev_sent)
                overlap_tokens += prev_token_len

            # Start new chunk
            current_chunk = overlap_chunk + [sentence]
            total_tokens = sum(len(encoding.encode(s)) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            total_tokens += token_len

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    print(f"🧩 Created {len(chunks)} sentence-based chunks (max_tokens={max_tokens}, overlap={overlap})")
    return chunks
