import streamlit as st
import time
import traceback
import os
from datetime import datetime

# ---------- IMPORT YOUR PIPELINE ----------
from dotenv import load_dotenv
from utils.audio_processor import process_input, get_audio_only
from core.transcriber import transcribe_all
from core.sammarize import summarize, generate_title   # note: filename is sammarize (typo)
from core.extractor import extract_action_items, extract_key_decisions, extract_question
from core.rag_engine import build_rag_chain, ask_question
from main import run_pipeline   # <--- YAHAN IMPORT KARO

load_dotenv()

def get_key(key_name):
    if hasattr(st, 'secrets') and key_name in st.secrets:
        return st.secrets[key_name]
    return os.getenv(key_name)

GROQ_API_KEY = get_key("GROQ_API_KEY")

# 2. Embedding Model sirf ek baar load hoga (cache mein)
@st.cache_resource
def load_embedding_model():
    from chromadb.utils import embedding_functions
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )

embedding_fn = load_embedding_model()
# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CUSTOM CSS (GREEN & WHITE THEME) ----------
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #0a3d2e !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
        [data-testid="stSidebar"] .stButton button {
            background-color: #2ecc71 !important;
            color: white !important;
            border-radius: 20px !important;
            font-weight: bold !important;
            border: none !important;
        }
        [data-testid="stSidebar"] .stButton button:hover {
            background-color: #27ae60 !important;
        }
        .main {
            background-color: #f8fcf9 !important;
        }
        h1, h2, h3 {
            color: #0a3d2e !important;
        }
        .stButton button {
            background-color: #2ecc71 !important;
            color: white !important;
            border-radius: 20px !important;
            font-weight: bold !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
        }
        .stButton button:hover {
            background-color: #27ae60 !important;
            transform: scale(1.02);
            transition: 0.2s;
        }
        .stButton button[data-testid="baseButton-primary"] {
            background-color: #0a3d2e !important;
            color: white !important;
        }
        [data-testid="metric-container"] {
            background-color: white !important;
            border-radius: 15px !important;
            padding: 15px !important;
            box-shadow: 0 4px 12px rgba(46, 204, 113, 0.2) !important;
            border-left: 5px solid #2ecc71 !important;
        }
        [data-testid="metric-container"] label {
            color: #0a3d2e !important;
            font-weight: bold !important;
        }
        [data-testid="metric-container"] .stMetricValue {
            color: #0a3d2e !important;
            font-size: 1.8rem !important;
        }
        .stChatMessage {
            border-radius: 12px !important;
            padding: 10px !important;
            margin: 5px 0 !important;
        }
        .stChatMessage[data-testid="chat-message-user"] {
            background-color: #e8f5e9 !important;
            border-left: 5px solid #2ecc71 !important;
        }
        .stChatMessage[data-testid="chat-message-assistant"] {
            background-color: white !important;
            border-left: 5px solid #0a3d2e !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        }
        .stFileUploader {
            background-color: white !important;
            border: 2px dashed #2ecc71 !important;
            border-radius: 15px !important;
        }
        .stTextInput input {
            border-radius: 20px !important;
            border: 2px solid #2ecc71 !important;
            padding: 10px 20px !important;
        }
        hr {
            border-color: #2ecc71 !important;
            opacity: 0.3 !important;
        }
        .pro-banner {
            background: linear-gradient(135deg, #0a3d2e, #2ecc71);
            padding: 15px;
            border-radius: 15px;
            color: white;
            text-align: center;
        }
        .error-box {
            background-color: #ffebee;
            border-left: 5px solid #c62828;
            padding: 10px;
            border-radius: 10px;
            margin: 10px 0;
            white-space: pre-wrap;
            font-family: monospace;
            overflow-x: auto;
        }
        .footer {
            text-align: center;
            color: #0a3d2e;
            opacity: 0.8;
            font-size: 0.9rem;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("# 🌿 AI Assistant")
    st.markdown("---")
    st.markdown("### 🏠 Home")
    st.markdown("- 📜 History")
    st.markdown("- 📁 Files")
    st.markdown("- 📊 Analytics")
    st.markdown("- ⚙️ Settings")
    st.markdown("- ℹ️ About")

    st.markdown("---")
    st.markdown("### ⭐ Upgrade to Pro")
    st.markdown("Unlock advanced features and unlimited meetings.")
    st.button("🚀 Upgrade Now", use_container_width=True)

    st.markdown("---")
    st.caption("❤️ Developed by Ahtisham Kashmiry")
    st.caption("[GitHub](#) • [LinkedIn](#) • [Email](#)")
    st.caption("AI Meeting Assistant v2.0")

# ---------- MAIN CONTENT ----------
st.title("🎙️ AI Meeting Assistant")
st.markdown(
    """
    **Transcribe • Summarize • Extract Insights • Chat with Meetings**  
    Transform meetings into actionable intelligence.  
    Upload a meeting file or paste a YouTube link and let AI handle the rest.
    """
)

# ---------- INPUT SECTION ----------
st.subheader("📥 Input Your Meeting Source")
source = st.text_input("Paste YouTube URL here...", placeholder="https://youtu.be/... or local file path")

uploaded_file = st.file_uploader("Or upload an audio/video file", type=["mp3", "mp4", "wav", "m4a"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    source = uploaded_file.name
    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully.")

# ---------- AUDIO EXTRACTION ----------
st.subheader("🎵 Audio Extraction")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🎧 Extract", "16kHz WAV")
c2.metric("🤖 No AI", "No API calls")
c3.metric("💰 Free", "100% Free")
c4.metric("⏱️ Done", "~30 sec")

if st.button("📥 Extract Audio Only"):
    if not source:
        st.warning("Please provide a YouTube URL or upload a file first.")
    else:
        with st.spinner("Extracting audio..."):
            try:
                audio_path = get_audio_only(source)
                st.success(f"✅ Audio extracted successfully: {audio_path}")
                # Store path in session state
                st.session_state["audio_path"] = audio_path
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.code(traceback.format_exc(), language="python")

# Display audio player and download button if audio_path exists
if "audio_path" in st.session_state and st.session_state["audio_path"]:
    audio_path = st.session_state["audio_path"]
    st.markdown("#### 🎧 Play Extracted Audio")
    st.audio(audio_path, format="audio/wav")
    # Read file for download
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        st.download_button(
            label="⬇️ Download Audio (WAV)",
            data=audio_bytes,
            file_name=os.path.basename(audio_path),
            mime="audio/wav",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not read audio file: {e}")

# ---------- FULL ANALYSIS ----------
st.subheader("⚡ Full AI Analysis")
st.markdown(
    """
    ✅ Transcription (Whisper AI)  
    ✅ AI Summary (Mistral)  
    ✅ Action Items & Decisions  
    ✅ Open Questions Extraction  
    ✅ RAG Chat with your meeting
    """
)

if st.button("🧠 Start Full Analysis", type="primary"):
    if not source:
        st.warning("Please provide a YouTube URL or upload a file.")
    else:
        with st.spinner("⏳ Full analysis in progress... (may take 5-10 minutes)"):
            try:
                result = run_pipeline(source)
                # Store everything in session state
                st.session_state["result"] = result
                st.session_state["analysis_done"] = True
                st.session_state["start_time"] = time.time()
                st.success("✅ Analysis complete!")
                # Force rerun to display results
                st.rerun()
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                # Show full traceback for debugging
                st.markdown("### 🔍 Detailed Error Traceback:")
                st.code(traceback.format_exc(), language="python")

# ---------- PRO BANNER ----------
st.markdown(
    """
    <div class="pro-banner">
        <h3 style="color:white; margin:0;">🌟 Upgrade to Pro</h3>
        <p style="margin:0;">Unlock advanced features and unlimited meetings.</p>
        <button style="background:white; color:#0a3d2e; border:none; padding:8px 30px; border-radius:20px; font-weight:bold; margin-top:10px; cursor:pointer;">Upgrade Now</button>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# ---------- DISPLAY RESULTS IF ANALYSIS DONE ----------
if "analysis_done" in st.session_state and st.session_state["analysis_done"]:
    result = st.session_state["result"]
    elapsed = time.time() - st.session_state["start_time"]
    minutes, seconds = divmod(int(elapsed), 60)
    processing_time = f"{minutes:02d}:{seconds:02d}"

    # Stats row
    st.markdown("### 📊 OVERVIEW")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Current Mode", "Full Analysis")
    col2.metric("Processing Time", processing_time)
    col3.metric("Total Words", len(result["transcript"].split()))
    col4.metric("Transcript Length", f"{len(result['transcript']):,} chars")
    col5.metric("Status", "✅ Completed")
    col6.metric("Vector DB", "Ready")
    st.caption("📌 Version v2.0")

    # Additional details (expandable)
    with st.expander("📝 View Transcript, Summary, Action Items & Decisions"):
        st.markdown(f"**📌 Title:** {result['title']}")
        st.markdown(f"**📄 Summary:**\n{result['summary']}")
        st.markdown(f"**✅ Action Items:**\n{result['action items']}")
        st.markdown(f"**🔑 Key Decisions:**\n{result['key decisions']}")
        st.markdown(f"**❓ Open Questions:**\n{result['question']}")

    # ---------- CHAT INTERFACE ----------
    st.markdown("### 💬 AI Meeting Assistant (RAG)")
    st.caption("🟢 Online")

    # Initialize chat history if not present (or we can keep existing)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display all chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask anything about your meeting..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate answer using RAG
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_question(result["rag"], prompt)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.code(traceback.format_exc(), language="python")

    st.caption("✨ AI responses are generated based on context from your meeting transcript.")
else:
    st.info("ℹ️ Run the analysis above to see results and start chatting.")

# ---------- FOOTER ----------
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        🌿 Developed by <strong>Ahtisham Kashmiry</strong> • 
        <a href="#" style="color:#0a3d2e;">GitHub</a> • 
        <a href="#" style="color:#0a3d2e;">LinkedIn</a> • 
        <a href="#" style="color:#0a3d2e;">Email</a> • 
        AI Meeting Assistant v2.0
    </div>
    """,
    unsafe_allow_html=True,
)
