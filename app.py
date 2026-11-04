"""Lab 2: an AI tutor chatbot with Streamlit and the Gemini API.

Run:  streamlit run app.py
"""
import os

import streamlit as st
from google import genai
from google.genai import types

MODEL = "gemini-3.1-flash-lite"  # alias for Google's newest Flash model; see the model list in AI Studio

st.set_page_config(page_title="AI Tutor", page_icon="🤖")
st.title("🤖 AI Tutor")
st.caption(f"A Streamlit chatbot powered by Gemini ({MODEL})")

# ---- Sidebar: settings ----
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Gemini API key", type="password",
                            value=os.environ.get("GEMINI_API_KEY", ""),
                            help="Create a free key at aistudio.google.com > Get API key")
    system_prompt = st.text_area("System prompt",
                                 "You are a friendly AI tutor for freshers. "
                                 "Explain simply, use short examples, and say when you are not sure.")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    if st.button("Start a new chat"):
        for k in ("client", "chat", "messages"):
            st.session_state.pop(k, None)
    st.caption("Changed the system prompt or temperature? Start a new chat to apply it.")

if not api_key:
    st.info("Paste your Gemini API key in the sidebar to start chatting.")
    st.stop()

# ---- Create the chat session once and keep it between reruns ----
if "chat" not in st.session_state:
    st.session_state.client = genai.Client(api_key=api_key)
    st.session_state.chat = st.session_state.client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=system_prompt, temperature=temperature),
    )
    st.session_state.messages = []

# ---- Show the conversation so far ----
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---- Handle a new message ----
if prompt := st.chat_input("Ask me anything about AI and ML viru"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            stream = st.session_state.chat.send_message_stream(prompt)
            reply = st.write_stream(chunk.text or "" for chunk in stream)
        except Exception as e:  # wrong key, quota exceeded, network error...
            reply = f"Sorry, the Gemini API returned an error: {e}"
            st.error(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
