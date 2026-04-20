import subprocess, json, groq as groq_sdk

def run_agent(prompt, history, complete, execute, remember):
    while True:
        completion = complete(prompt, history)
        execution = execute(completion)
        remember(history, completion, execution)

def main():
    with open("prompt.txt") as f: prompt = f.read()
    try:
        with open("history.json") as f: history = json.load(f)
    except FileNotFoundError: history = []
    groq = groq_sdk.Groq()
    def complete(prompt, history):
        while True:
            try:
                completion = groq.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "system", "content": prompt}] + history,
                ).choices[0].message.content
            except groq_sdk.APIStatusError as e:
                unexpected = False
                if e.response.reason_phrase == "Payload Too Large":
                    history[:] = history[2:]
                else:
                    unexpected = True
                if unexpected:
                    raise e
                else:
                    print("ERROR:\n" + str(e) + "\n")
            else:
                print("COMPLETION:\n" + completion + "\n")
                return completion
    def execute(completion):
        execution = subprocess.run([
            "docker",
            "exec",
            "shell-agent",
            "bash",
            "-c",
            completion,
        ], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout.decode()
        print("EXECUTION:\n" + execution + "\n")
        return execution
    def remember(history, completion, execution):
        history.extend([
            {"role": "assistant", "content": completion},
            {"role": "user", "content": execution},
        ])
        with open("history.json", "w") as f: json.dump(history, f, indent=0)
    run_agent(prompt, history, complete, execute, remember)

main()
