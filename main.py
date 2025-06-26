import streamlit as st
import time
import os
import json
from datetime import datetime
import fitz  # PyMuPDF
import pandas as pd
from groq import Groq, GroqError
import re

# --- Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "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"
CHAT_HISTORY_DIR = "chat_history"
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

AVAILABLE_MODELS = ["llama3-8b-8192", "llama3-70b-8192", "deepseek-r1-distill-llama-70b"]  # Add more if available

# --- Initialize Groq Client ---
try:
    client = Groq(api_key=GROQ_API_KEY)
except GroqError as e:
    st.error(f"API Key Error: {e}")
    st.stop()

# --- Streamlit Config ---
st.set_page_config(page_title="ChatSutra", layout="wide")
st.title("🧠 ChatSutra")

# --- Session States ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
if "chat_enabled" not in st.session_state:
    st.session_state.chat_enabled = True
if "selected_model" not in st.session_state:
    st.session_state.selected_model = AVAILABLE_MODELS[0]

# --- Helper Functions ---
def list_chat_histories():
    return sorted(os.listdir(CHAT_HISTORY_DIR), reverse=True)

def sanitize_filename(name):
    """Remove or replace unsafe filename characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)[:50]  # Limit filename length

def save_chat(name=None):
    if not name:
        # Use first user message as filename
        user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
        if user_messages:
            first_input = user_messages[0]["content"].strip().split("\n")[0]
            name = sanitize_filename(first_input) + ".json"
        else:
            name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    filepath = os.path.join(CHAT_HISTORY_DIR, name)
    with open(filepath, "w") as f:
        json.dump(st.session_state.messages, f)
    return name

def load_chat(name):
    filepath = os.path.join(CHAT_HISTORY_DIR, name)
    with open(filepath, "r") as f:
        st.session_state.messages = json.load(f)

def delete_chat(name):
    filepath = os.path.join(CHAT_HISTORY_DIR, name)
    os.remove(filepath)

def extract_file_content(file):
    if file.type == "application/pdf":
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            text = "\n".join([page.get_text() for page in doc])
    elif file.type == "text/plain":
        text = file.read().decode("utf-8")
    elif file.type == "text/csv":
        df = pd.read_csv(file)
        text = df.to_string(index=False)
    else:
        text = "Unsupported file type."
    return text[:2000]  # Limit content

def get_groq_response(messages, model, retries=3, delay=3):
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return completion.choices[0].message.content
        except GroqError as e:
            if "503" in str(e) or "Service Unavailable" in str(e):
                st.warning(f"Groq service unavailable, retrying... ({attempt + 1}/{retries})")
                time.sleep(delay)
            else:
                raise e
    st.error("Groq API is currently unavailable. Please try again later.")
    return None

def format_chat_for_download():
    lines = []
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        role = "You" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}\n")
    return "\n".join(lines)

# --- Sidebar Controls ---
st.sidebar.title("⚙️ Options")

# Model Selector
st.sidebar.subheader("🤖 Model Selection")
st.session_state.selected_model = st.sidebar.selectbox("Choose Model", AVAILABLE_MODELS)

# Chat Management
if st.sidebar.button("🆕 New Conversation"):
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    st.success("Started a new conversation.")

if st.sidebar.button("❌ End Chat"):
    st.session_state.chat_enabled = False
    st.info("Chat ended.")

if st.sidebar.button("✅ Resume Chat"):
    st.session_state.chat_enabled = True
    st.success("Chat resumed.")

# File Upload for Context
st.sidebar.subheader("📁 Upload Context File")
uploaded_file = st.sidebar.file_uploader("PDF, CSV, or TXT", type=["pdf", "csv", "txt"])
if uploaded_file:
    context_text = extract_file_content(uploaded_file)
    st.session_state.messages.append({
        "role": "system",
        "content": f"Use this context for all future responses:\n\n{context_text}"
    })
    st.success("Context from file added.")

# Chat History Management
st.sidebar.subheader("💬 Chat History")
history_files = list_chat_histories()
if history_files:
    selected_history = st.sidebar.selectbox("Load Previous Chat", history_files)
    if st.sidebar.button("📂 Load Chat"):
        load_chat(selected_history)
        st.rerun()
    if st.sidebar.button("🗑️ Delete Chat"):
        delete_chat(selected_history)
        st.sidebar.success("Deleted chat.")
        st.rerun()
else:
    st.sidebar.write("No saved chats found.")

if st.sidebar.button("💾 Save Current Chat"):
    filename = save_chat()
    st.sidebar.success(f"Saved as {filename}")

if st.sidebar.button("⬇️ Export Chat (.txt)"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content = format_chat_for_download()
    st.sidebar.download_button("📥 Download", content, file_name=f"groq_chat_{timestamp}.txt")

# --- Main Chat Area ---
if st.session_state.chat_enabled:
    user_input = st.chat_input("Type your message here...")
else:
    user_input = None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("Thinking..."):
        response = get_groq_response(st.session_state.messages, st.session_state.selected_model)
        if response:
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- Display Chat ---
for msg in st.session_state.messages:
    role = msg["role"]
    if role == "user":
        st.chat_message("user").write(msg["content"])
    elif role == "assistant":
        st.chat_message("assistant").write(msg["content"])

import re

def sanitize_filename(name):
    """Remove or replace unsafe filename characters."""
    return re.sub(r'[\\/*?:"<>|]', "_", name)[:50]  # Limit length for safety

def save_chat(name=None):
    if not name:
        # Use first user message as filename
        user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
        if user_messages:
            first_input = user_messages[0]["content"].strip().split("\n")[0]
            name = sanitize_filename(first_input) + ".json"
        else:
            name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    filepath = os.path.join(CHAT_HISTORY_DIR, name)
    with open(filepath, "w") as f:
        json.dump(st.session_state.messages, f)
    return name
