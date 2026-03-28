import enum
import os
import requests
import streamlit as st
from dotenv import load_dotenv

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GPT-5 Nano Chat",
    page_icon="🤖",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #0d0f12;
    --surface:   #161920;
    --border:    #252930;
    --accent:    #7efff5;
    --accent2:   #ff6b6b;
    --text:      #e8eaed;
    --muted:     #5a6070;
    --user-bg:   #1e2230;
    --bot-bg:    #13181f;
    --radius:    14px;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'DM Mono', monospace;
    color: var(--text);
}

/* Hide default streamlit chrome */
[data-testid="stHeader"], footer { display: none !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1.5rem !important; }

/* ── Title ── */
.chat-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    letter-spacing: -0.03em;
    color: var(--accent);
    margin-bottom: 0;
}
.chat-subtitle {
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

/* ── Mode selector ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}
[data-testid="stSelectbox"] label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ── Chat messages ── */
.msg-row {
    display: flex;
    gap: 10px;
    margin-bottom: 16px;
    align-items: flex-start;
}
.msg-row.user  { flex-direction: row-reverse; }
.avatar {
    width: 30px; height: 30px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
}
.avatar.user { background: #2a2060; }
.avatar.bot  { background: #0e2a28; border: 1px solid var(--accent); }
.bubble {
    max-width: 82%;
    padding: 12px 16px;
    border-radius: var(--radius);
    font-size: 0.86rem;
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble.user {
    background: var(--user-bg);
    border: 1px solid #2e3550;
    border-top-right-radius: 4px;
}
.bubble.bot {
    background: var(--bot-bg);
    border: 1px solid var(--border);
    border-top-left-radius: 4px;
}
.role-label {
    font-size: 0.62rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
    color: var(--muted);
}
.role-label.user { text-align: right; }

/* ── Thinking indicator ── */
.thinking {
    display: flex; align-items: center; gap: 8px;
    color: var(--accent);
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    padding: 8px 0 4px 40px;
}
.dots span {
    display: inline-block;
    width: 5px; height: 5px;
    border-radius: 50%;
    background: var(--accent);
    margin: 0 2px;
    animation: bounce 1.2s infinite ease-in-out;
}
.dots span:nth-child(2) { animation-delay: 0.2s; }
.dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: translateY(0); opacity: 0.4; }
    40%            { transform: translateY(-6px); opacity: 1; }
}

/* ── Input area ── */
[data-testid="stChatInput"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.85rem !important;
    color: var(--text) !important;
    background: transparent !important;
}
[data-testid="stChatInput"] button {
    background: var(--accent) !important;
    color: #000 !important;
    border-radius: 8px !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 0.6rem 0 1rem 0 !important; }

/* ── Mode badge ── */
.mode-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}
.mode-badge.chat    { background: #1a2040; color: #7eb8ff; border: 1px solid #2a3560; }
.mode-badge.agentic { background: #1a2a1a; color: var(--accent); border: 1px solid #2a4030; }

/* scrollable chat area */
.chat-scroll {
    max-height: 62vh;
    overflow-y: auto;
    padding-right: 4px;
    margin-bottom: 0.5rem;
}
.chat-scroll::-webkit-scrollbar { width: 4px; }
.chat-scroll::-webkit-scrollbar-track { background: transparent; }
.chat-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ── Enums & backend logic ───────────────────────────────────────────────────────
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
        chat_history.append({"role": "user", "content": user_input})
        payload = get_chat_mode_payload(chat_history)
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
        if mode == Mode.CHAT:
            chat_history.append({"role": "assistant", "content": reply})
        return reply, new_id, quota, None
    else:
        return None, previous_response_id, {}, f"Error {response.status_code}: {response.text}"

# ── Session state init ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # {role, content}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "previous_response_id" not in st.session_state:
    st.session_state.previous_response_id = None
if "quota" not in st.session_state:
    st.session_state.quota = {}

# ── Load token ─────────────────────────────────────────────────────────────────
load_dotenv("token.env")
TOKEN = os.getenv("API_TOKEN", "")

# ── Header ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="chat-title">GPT‑5 Nano</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-subtitle">Powered by OpenAI · IAC Student API</div>', unsafe_allow_html=True)
with col2:
    mode_label = st.selectbox(
        "MODE",
        options=["💬 Chat", "🤖 Agentic"],
        key="mode_select",
        label_visibility="visible"
    )

mode = Mode.CHAT if mode_label == "💬 Chat" else Mode.AGENTIC
reasoning = {"effort": "low"}

st.markdown("<hr>", unsafe_allow_html=True)

# ── Quota warning ──────────────────────────────────────────────────────────────
q = st.session_state.quota
if q:
    for label, lim_key, used_key in [
        ("Daily",   "limit_daily",   "tokens_used_daily"),
        ("Hourly",  "limit_hourly",  "tokens_used_hourly"),
        ("Monthly", "limit_monthly", "tokens_used_monthly"),
    ]:
        remaining = q.get(lim_key, 0) - q.get(used_key, 0)
        if remaining <= 2000:
            st.warning(f"⚠️ {label} quota almost exhausted — {remaining} tokens remaining.")

# ── Chat messages ──────────────────────────────────────────────────────────────
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-scroll" id="chat-scroll">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        avatar = "👤" if role == "user" else "🤖"
        label  = "You" if role == "user" else "GPT‑5 Nano"
        st.markdown(f"""
        <div class="msg-row {role}">
            <div>
                <div class="role-label {role}">{label}</div>
                <div class="bubble {role}">{content}</div>
            </div>
            <div class="avatar {role}">{avatar}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Type a message…")

if user_input:
    if not TOKEN:
        st.error("No API token found. Make sure `API_TOKEN` is set in `token.env`.")
    else:
        # Show user message immediately
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Show thinking indicator while waiting
        with st.spinner(""):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("""
            <div class="thinking">
                <div class="dots"><span></span><span></span><span></span></div>
                thinking…
            </div>""", unsafe_allow_html=True)

            reply, new_id, quota, error = send_message(
                user_input,
                mode,
                st.session_state.chat_history,
                reasoning,
                st.session_state.previous_response_id,
                TOKEN
            )
            thinking_placeholder.empty()

        if error:
            st.error(error)
        else:
            st.session_state.previous_response_id = new_id
            st.session_state.quota = quota
            st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()