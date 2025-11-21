from domain.documents.llm_client import generate_answer

def generate_session_title(messages: list[str]) -> str:
    """
    Generates a short title using the LLM based on the chat messages.
    """
    conversation_text = "\n".join(messages)

    prompt = f"""
    Buatkan judul yang sangat singkat (maksimal 6 kata) untuk percakapan berikut.
    Judul harus ringkas, tidak dramatis, dan langsung menunjukkan topik percakapan.

    Percakapan:
    {conversation_text}

    Output hanya judulnya saja, tanpa tanda kutip.
    """

    try:
        title = generate_answer(prompt)
        return title.strip()
    except Exception:
        # fallback supaya tidak error
        return messages[0][:60]
