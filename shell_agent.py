def run_agent_loop(instructing_prompt, history, complete, execute, remember):
    while True:
        completion = complete(instructing_prompt, history)
        execution = execute(completion)
        history = remember(history, completion, execution)

def main():
    def read_instructing_prompt():
        return open("prompt.txt").read()

    def find_history():
        import json
        try:
            return json.load(open("history.json"))
        except FileNotFoundError:
            return []

    def prefix_lines(message, prefix):
        return prefix + completion.replace("\n", "\n" + prefix)

    def make_completer():
        import openrouter as openrouter_sdk
        openrouter_client = openrouter_sdk.OpenRouter(api_key=open("openrouter_api_key.txt").read().strip())
        def complete():
            completion = openrouter_client.chat.send(
                model="tencent/hy3-preview:free",
                messages=[{"role": "system", "content": prompt}] + history[:-50],
            ).choices[0].message.content
            print(prefix_lines(completion, "$ "))
            print()
            return completion
        return complete

    def execute(program):
        import subprocess
        execution = subprocess.run([
            "lxc-attach",
            "shell-agent",
            "--",
            "bash",
            "-c",
            program,
        ], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout.decode()
        if len(execution) > 1000:
            execution = execution[:1000] + "<output trimmed at 1000 characters>"
        print(prefix_lines(execution, "< "))
        print()
        return execution

    def remember(history, completion, execution):
        import json
        with open("history.json", "w") as f:
            json.dump(f, history)
        return history[:-48] + [
            {"role": "assistant", "content": completion},
            {"role": "user", "content": execution},
        ]

    instructing_prompt = read_instructing_prompt()
    history = find_history()
    complete = make_completer()
    run_agent_loop(instructing_prompt, history, complete, execute, remember)

main()
