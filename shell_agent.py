import json, subprocess, os, time, re
from groq import Groq, APIStatusError
from json.decoder import JSONDecodeError

def run_agent_loop(starting_prompt, history, complete, execute):
    while True:
        completion = ""
        with complete(starting_prompt, history) as chunks:
            print("$ ", end="", flush=True)
            for chunk in chunks:
                completion += chunk
                print(chunk.replace("\n", "\n$ "), end="", flush=True)
            print()
        print("$ " + completion.replace("\n", "\n$ ") + "\n")
        execution = execute(completion)
        print("< " + execution.replace("\n", "\n< ") + "\n")
        history.append({"completion": completion, "execution": execution})

STARTING_PROMPT = """
You are an AI assistant whose every message is directly passed to a new Bash session, one session per message.

Your goal is, using the Bash shell you are given, to start listening on a Telegram bot with the token {telegram_token}, and do whatever is ordered from you

Your messages are passed directly to Bash, so if you want to think, you have to think inside of Bash comments. Your messages should be Bash scripts executable as is

You are writing plain text, not Markdown, so do NOT add code fences (```) around your code
""".strip()

def run():
    starting_prompt = STARTING_PROMPT.format(**json.load(open("prompt_config.json")))
    history = []
    groq = Groq()
    def complete(starting_prompt, history):
        messages = [
            {
                "role": "system",
                "content": starting_prompt
            },
        ]
        for turn in history:
            messages.append({
                "role": "assistant",
                "content": turn["completion"],
            })
            messages.append({
                "role": "user",
                "content": turn["execution"],
            })
        try:
            completion = groq.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
            )
        except APIStatusError as e:
            if e.status_code == 413: # Context too long
                print(e)
                history[:] = history[1:]
                return complete(starting_prompt, history)
            elif e.status_code == 429: # Rate limited
                print(e)
                time.sleep(10)
                return complete(starting_prompt, history)
            else:
                raise e
        return completion.choices[0].message.content
    def execute(completion):
        return subprocess.run([
            "docker",
            "exec",
            "shell-agent",
            "bash",
            "-c",
            completion,
        ], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout.decode()
    run_agent_loop(starting_prompt, history, complete, execute)

run()
