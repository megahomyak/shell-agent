import subprocess, json, openrouter as openrouter_sdk, sys

def run_agent(prompt, history, complete, execute, remember, iter_count):
    while iter_count > 0:
        completion = complete(prompt, history)
        execution = execute(completion)
        remember(history, completion, execution)
        iter_count -= 1

def main():
    with open("prompt.txt") as f: prompt = f.read()
    try:
        with open("history.json") as f: history = json.load(f)
    except FileNotFoundError: history = []
    with open("openrouter_api_key.txt") as f:
        openrouter_client = openrouter_sdk.OpenRouter(api_key=f.read().strip())
    def complete(prompt, history):
        completion = openrouter_client.chat.send(
            model="openrouter/free",
            messages=[{"role": "system", "content": prompt}] + history[:-10],
        ).choices[0].message.content
        if len(completion) > 1000:
            completion = completion[:1000] + "<output trimmed at 1000 characters>"
        print("$ " + completion.replace("\n", "\n$ ") + "\n")
        return completion
    def execute(completion):
        execution = subprocess.run([
            "lxc-attach",
            "shell-agent",
            "--",
            "bash",
            "-c",
            completion,
        ], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout.decode()
        print("< " + execution.replace("\n", "\n< ") + "\n")
        return execution
    def remember(history, completion, execution):
        history.extend([
            {"role": "assistant", "content": completion},
            {"role": "user", "content": execution},
        ])
        with open("history.json", "w") as f: json.dump(history, f, indent=0)
    if len(sys.argv) > 1:
        iter_count = int(sys.argv[1])
    else:
        iter_count = float("inf")
    run_agent(prompt, history, complete, execute, remember, iter_count)

main()
