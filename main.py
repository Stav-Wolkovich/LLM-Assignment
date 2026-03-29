import enum
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# ── Page config (Native Streamlit) ─────────────────────────────────────────────
st.set_page_config(page_title="GPT-5 Nano Chat", page_icon="🤖")

# ── Your Original Backend Logic (Preserved) ───────────────────────────────────
class Mode(enum.Enum):
    CHAT = 0
    AGENTIC = 1

def get_chat_mode_payload(chat_history):
    return {
        "messages": chat_history,
        "model": "gpt-5-nano",
        "max_completion_tokens": 2000
    }

def get_agent_mode_payload(user_input, reasoning, previous_response_id):
    return {
        "input": user_input,
        "model": "gpt-5-nano",
        "max_completion_tokens": 2000,
        "tools": [{"type": "web_search"}],
        "reasoning": reasoning,
        "previous_response_id": previous_response_id
    }

def get_api_url(mode):
    if mode == Mode.CHAT:
        return "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
    return "https://server.iac.ac.il/api/v1/studentapi/responses"

def parse_response(mode, data):
    if mode == Mode.CHAT:
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    message = next((item for item in data.get("output", []) if item["type"] == "message"), None)
    if message:
        return message["content"][0]["text"]
    return ""

def send_message(user_input, mode, chat_history, reasoning, previous_response_id, token):
    if mode == Mode.CHAT:
        # Note: We update the API history here specifically for the request
        api_history = chat_history + [{"role": "user", "content": user_input}]
        payload = get_chat_mode_payload(api_history)
    else:
        payload = get_agent_mode_payload(user_input, reasoning, previous_response_id)

    response = requests.post(
        get_api_url(mode),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        reply = parse_response(mode, data)
        new_id = data.get("id") if mode == Mode.AGENTIC else previous_response_id
        quota = data.get("iac_quota_status", {})
        return reply, new_id, quota, None
    else:
        return None, previous_response_id, {}, f"Error {response.status_code}: {response.text}"

# ── Session State ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []         # UI Display history
if "prev_id" not in st.session_state:
    st.session_state.prev_id = None
if "quota" not in st.session_state:
    st.session_state.quota = {}

# ── Sidebar & Environment ──────────────────────────────────────────────────────
load_dotenv("token.env")
TOKEN = os.getenv("API_TOKEN", "")

with st.sidebar:
    st.title("Settings")
    mode_label = st.selectbox("Select Mode", ["💬 Chat", "🤖 Agentic"])
    current_mode = Mode.CHAT if mode_label == "💬 Chat" else Mode.AGENTIC
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.prev_id = None
        st.rerun()

# ── Main Chat UI ──────────────────────────────────────────────────────────────
st.title("🤖 GPT-5 Nano")

# 1. Display Chat History using native bubbles
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 2. Chat Input
if prompt := st.chat_input("Type a message..."):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Generate Response
    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=False):
            reply, new_id, quota, error = send_message(
                prompt,
                current_mode,
                st.session_state.messages[:-1], # Send history except the current prompt
                {"effort": "low"},
                st.session_state.prev_id,
                TOKEN
            )

        if error:
            st.error(error)
        else:
            st.markdown(reply)
            # Update history and IDs
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.prev_id = new_id
            st.session_state.quota = quota
            
    # Optional: Display quota warnings if needed
    if st.session_state.quota:
        remaining = st.session_state.quota.get("limit_daily", 0) - st.session_state.quota.get("tokens_used_daily", 0)
        if remaining < 2000:
            st.toast(f"Low Quota: {remaining} tokens left", icon="⚠️")