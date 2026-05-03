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
        openrouter_model = open("openrouter_model.txt").read().strip()
        def complete(instructing_prompt, temporary_memory):
            response = openrouter_client.chat.send(
                model=openrouter_model,
                messages=[{"role": "system", "content": instructing_prompt}] + temporary_memory,
            ).choices[0].message
            if response.reasoning:
                print(prefix_lines(response.reasoning, "! "))
                print()
            completion = response.content
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
        EXECUTION_MAX_LEN = 10000
        if len(execution) > EXECUTION_MAX_LEN:
            execution = execution[:EXECUTION_MAX_LEN] + f"<output trimmed at {EXECUTION_MAX_LEN} characters>"
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
