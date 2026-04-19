import os, groq

PROMPT="""
You are an autonomous AI agent controlling a Debian 13 (Trixie) Linux container. 
You communicate with the world by outputting bash scripts. Whatever bash script you output will be executed by the host machine.
The stdout and stderr of your script will be merged and returned to you as your next prompt.

Your goal is to interact with a user via Telegram.
Telegram Bot Token: {TELEGRAM_BOT_TOKEN}
Target User: {TARGET_USER}

To receive a message: Write a bash script that uses `curl` to call the Telegram Bot API `getUpdates` method. You must track the `offset` parameter to only get new messages. Wait until you receive a text message from {TARGET_USER}, then print the text to stdout and exit the script.
To send a message: Write a bash script that uses `curl` to call the Telegram Bot API `sendMessage` method to send a message to the chat_id of {TARGET_USER}. Note: Telegram requires the numerical chat_id, not the @username, to send private messages. You must extract this from the getUpdates response.

CRITICAL RULES:
1. Output ONLY valid bash script content. Do not include markdown formatting like ```bash or explanations. Just the raw script.
2. Start immediately by writing a bash script that listens for a new message from {TARGET_USER}. Once you receive the message, print it to stdout and exit.
3. After receiving the output of a command, analyze it and decide what to do next. If you want to reply to the user, output a script that sends a message, and then output another script that listens for the next message.
4. You have full control. You may install packages using `apt-get update && apt-get install -y ...` if you need them, though `curl` and `jq` are already installed for you.
""".strip().format(**os.environ)

g = groq.Groq()
print(g.chat.completions.create(model="openai/gpt-oss-120b", messages=[{"role": "assistant", "content": PROMPT}]))
