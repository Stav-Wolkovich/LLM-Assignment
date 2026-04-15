# LLM-Assignment

# GPT‑5 Nano Chat & Agentic Interface
A Streamlit‑based interactive client for communicating with the GPT‑5 Nano model via the IAC Student API.
The application supports both standard chat and agentic reasoning mode with optional web‑search tools.

# Overview
This project provides a lightweight, browser‑based interface for interacting with the GPT‑5 Nano model.
It includes:
- Chat Mode — traditional conversational interaction.
- Agentic Mode — enhanced reasoning with access to a web‑search tool.
- Persistent session state for message history and agentic response tracking.
- Quota monitoring with visual warnings.
- Secure token loading via environment variables.
The interface is built entirely with Streamlit, offering a clean and responsive chat experience.

# Features
- Chat Mode:
  -  Sends the full conversation history to the API and receives a standard model response.

- Agentic Mode:
  - Enables structured reasoning and tool usage (e.g., web search).
  - Each response is linked to a previous_response_id to maintain agentic continuity.

# Additional Capabilities
- Sidebar mode switching
- Clear‑chat functionality
- Token quota display
- Streamlit chat bubbles for a native chat UI

# Project Structure

<img width="696" height="186" alt="image" src="https://github.com/user-attachments/assets/5ef279dc-481a-4470-8428-52c72150829c" />


# Installation
## 1. Create a virtual environment (recommended)

python -m venv venv

source venv/bin/activate   # macOS / Linux

venv\Scripts\activate      # Windows

## 2. Install dependencies
Ensure your requirements.txt includes:

certifi==2026.2.25

charset-normalizer==3.4.6

idna==3.11

python-dotenv==1.2.2

requests==2.32.5

urllib3==2.6.3

streamlit==1.55.0

Install:

pip install -r requirements.txt

## 3. Configure API token
Create a file named token.env in the project root:

API_TOKEN=your_api_token_here

## 4. Run the application with streamlit

streamlit run main.py

# How It Works
## Chat Requests
The application sends a payload containing the full message history:

{
  "messages": [...],
  "model": "gpt-5-nano",
  "max_completion_tokens": 2000
}

## Agentic Requests
Agentic mode includes reasoning metadata and tool definitions:

json
{
  "input": "...",
  "model": "gpt-5-nano",
  "tools": [{"type": "web_search"}],
  "reasoning": {"effort": "low"},
  "previous_response_id": "..."
}

# Response Parsing
The application extracts the assistant message from the API response and updates:
- Chat history
- Agentic response ID
- Quota usage

# Environment & Security Notes
- The API token must remain private and should not be committed to version control.
- The application loads environment variables using python-dotenv.
- Agentic mode relies on maintaining previous_response_id; clearing the chat resets it.

# License
This project is provided for educational and research purposes.
Ensure compliance with the IAC Student API usage policies.
