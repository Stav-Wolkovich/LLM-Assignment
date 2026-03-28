import enum
import os
import requests
from dotenv import load_dotenv

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
        "tools": [
            {"type": "web_search"}
        ],
        "reasoning": reasoning,
        "previous_response_id": previous_response_id
    }

def get_api_url(mode):
    if mode == Mode.CHAT:
        return "https://server.iac.ac.il/api/v1/studentapi/chat/completions"
    elif mode == Mode.AGENTIC:
        return "https://server.iac.ac.il/api/v1/studentapi/responses"
    else:
        raise ValueError("Invalid mode")
    

def get_response(mode, data):
    if mode == Mode.CHAT:
        return data.get("choices", [{}])[0].get("message", {}).get("content")
    elif mode == Mode.AGENTIC:
        message = next(item for item in data['output'] if item['type'] == 'message')
        return message['content'][0]['text']
    else:
        raise ValueError("Invalid mode")


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
        

def check_limit(quota, limit_key, used_key, label):
    limit_val = quota.get(limit_key, 0)
    used_val = quota.get(used_key, 0)

    remaining = limit_val - used_val

    if remaining <= 2000:
        print(f"⚠️ Warning: {label} quota is almost exhausted!")
        print(f"   Used: {used_val} / {limit_val} (Remaining: {remaining})\n")


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
    previous_response_id = None

    while True:
        user_input = input("You: ")
        action, mode, reasoning = handle_non_query_inputs(user_input, mode, reasoning)
        if action == "break":
            break
        elif action == "continue":
            continue

        if mode == Mode.CHAT:
            chat_history.append({"role": "user", "content": user_input})

        payload = get_chat_mode_payload(chat_history) if mode == Mode.CHAT else get_agent_mode_payload(user_input, reasoning, previous_response_id)        
        
        response = requests.post(
            get_api_url(mode),
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            resp = get_response(mode, data)
            current_id = data.get('id')

            if (mode == Mode.AGENTIC):
                previous_response_id = current_id
            elif mode == Mode.CHAT:
                chat_history.append({"role": "assistant", "content": resp})

            print(f"ChatGPT-NANO-5: {resp}")

            quota = data.get("iac_quota_status", {})
            # Check all quotas
            check_limit(quota, "limit_daily", "tokens_used_daily", "Daily")
            check_limit(quota, "limit_hourly", "tokens_used_hourly", "Hourly")
            check_limit(quota, "limit_monthly", "tokens_used_monthly", "Monthly")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()