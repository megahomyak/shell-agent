import json, subprocess, os, time
from groq import Groq, APIStatusError

def run_agent_loop(starting_prompt, history, complete, execute):
    while True:
        completion = complete(starting_prompt, history)
        print("$ " + completion.replace("\n", "\n$ ") + "\n")
        execution = execute(completion)
        print("< " + execution.replace("\n", "\n< ") + "\n")
        history.append({"completion": completion, "execution": execution})

STARTING_PROMPT = """

""".strip()

def run():
    starting_prompt = STARTING_PROMPT.format(**json.load(open("prompt_config.json")))
    history = []
    groq = Groq()
    container_id = os.environ["CONTAINER_ID"]
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
                model="llama-3.1-8b-instant",
                messages=messages,
            )
        except APIStatusError as e:
            if e.status_code == 413: # Context too long
                history[:] = history[1:]
                return complete(starting_prompt, history)
            elif e.status_code == 429: # Rate limited
                time.sleep(10)
                return complete(starting_prompt, history)
            else:
                raise e
        return completion.choices[0].message.content
    def execute(completion):
        executions = []
        for params in re.findall(r"^/ssh")
        return subprocess.run([
            "docker",
            "exec",
            container_id,
            "bash",
            "-c",
            completion,
        ], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout.decode()
    run_agent_loop(starting_prompt, history, complete, execute)

run()
