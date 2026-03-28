import enum
import os
import requests
from dotenv import load_dotenv

class Mode(enum.Enum):
    CHAT = 0
    AGENTIC = 1

def get_payload(mode, chat_history, reasoning):
    if mode == Mode.CHAT:
        return {
            "messages": chat_history,
            "model": "gpt-5-nano",
            "max_completion_tokens": 2000
        }
    elif mode == Mode.AGENTIC:
        return {
            "messages": chat_history,
            "model": "gpt-5-nano",
            "max_completion_tokens": 2000,
            "tools": [
                {"type": "web_search"}
            ],
            "reasoning": reasoning
        }

def handle_non_query_inputs(user_input, mode, reasoning):
        if user_input in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            return "break", mode, reasoning
        elif user_input == "agentic mode":
            print("Switched to Agentic Mode. The bot will now perform actions based on your commands.")
            return "continue", Mode.AGENTIC, reasoning
        elif user_input == "chat mode":
            print("Switched to Chat Mode. The bot will now respond to your messages.")
            return "continue", Mode.CHAT, reasoning
        elif user_input.startswith("effort:"):
            value = user_input.split(":", 1)[1]
            reasoning["effort"] = value
            return "continue", mode, reasoning
        else:
            return "none", mode, reasoning

def main():
    print("Welcome to my Web Chat, based on ChatGPT-NANO-5")
    
    load_dotenv("token.env")
    TOKEN = os.getenv("API_TOKEN")
    if not TOKEN:
        print("API token not found. Please set it in the token.env file.")
        return
    
    mode = Mode.CHAT
    chat_history = []
    reasoning = {"effort": "low"}

    while True:
        user_input = input("You: ")
        action, mode, reasoning = handle_non_query_inputs(user_input, mode, reasoning)
        if action == "break":
            break
        elif action == "continue":
            continue

        chat_history.append({"role": "user", "content": user_input})

        payload=get_payload(mode, chat_history, reasoning)
        
        response = requests.post(
            "https://server.iac.ac.il/api/v1/studentapi/chat/completions",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data['choices'][0]['message']
            bot_reply = message.get('content') or message.get('reasoning') or ''
            chat_history.append({"role": "assistant", "content": bot_reply})
            print(f"ChatGPT-NANO-5: {bot_reply}")

        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()