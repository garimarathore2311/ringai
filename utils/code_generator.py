# utils/code_generator.py
def generate_embed_code(client_id: str) -> str:
    return f'<script src="https://yourdomain.com/static/chatbot.js?client_id={client_id}"></script>'
