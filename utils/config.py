import os
import streamlit as st
from dotenv import load_dotenv

# 🔥 Local system ke liye (.env se load)
load_dotenv()

# 🔥 Cloud ke liye (st.secrets se load)
def get_api_key(key_name):
    # Pehle st.secrets mein check karo (Cloud)
    if hasattr(st, 'secrets') and key_name in st.secrets:
        return st.secrets[key_name]
    # Agar nahi mila toh .env se le lo (Local)
    return os.getenv(key_name)

# Ab API keys aise use karo:
GROQ_API_KEY = get_api_key(" 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")
MISTRAL_API_KEY = get_api_key("Kub6NIJBAsecIMTs0RMrTaxoitdUS7QM")  # agar ho toh
