def run_agent_loop(instructing_prompt, temporary_memory, complete, execute, remember):
    while True:
        completion = complete(instructing_prompt, temporary_memory)
        execution = execute(completion)
        temporary_memory = remember(temporary_memory, completion, execution)

def main():
    def read_instructing_prompt():
        return open("instructing_prompt.txt").read()

    def prefix_lines(message, prefix):
        return prefix + message.replace("\n", "\n" + prefix)

    def make_openrouter_completer():
        import openrouter as openrouter_sdk
        openrouter_client = openrouter_sdk.OpenRouter(api_key=open("openrouter_api_key.txt").read().strip())
        def complete(instructing_prompt, temporary_memory):
            import time
            time.sleep(10)
            completion = openrouter_client.chat.send(
                model="tencent/hy3-preview:free",
                messages=[{"role": "system", "content": instructing_prompt}] + temporary_memory,
            ).choices[0].message.content
            print(prefix_lines(completion, "$ "))
            print()
            return completion
        return complete

    def execute_in_lxc(program):
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
            execution = execution[:10000] + "<output trimmed at 10000 characters>"
        print(prefix_lines(execution, "< "))
        print()
        return execution

    def remember(temporary_memory, completion, execution):
        return temporary_memory[:-48] + [
            {"role": "assistant", "content": completion},
            {"role": "user", "content": execution},
        ]

    instructing_prompt = read_instructing_prompt()
    temporary_memory = []
    complete = make_openrouter_completer()
    execute = execute_in_lxc
    run_agent_loop(instructing_prompt, temporary_memory, complete, execute, remember)

main()
