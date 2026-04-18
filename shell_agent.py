import json, subprocess, os, time, re
from groq import Groq, APIStatusError
from json.decoder import JSONDecodeError

def run_agent_loop(starting_prompt, history, complete, execute):
    while True:
        completion = complete(starting_prompt, history)
        print("$ " + completion.replace("\n", "\n$ ") + "\n")
        execution = execute(completion)
        print("< " + execution.replace("\n", "\n< ") + "\n")
        history.append({"completion": completion, "execution": execution})

STARTING_PROMPT = """
You are an AI assistant with its own computer. To use the computer, you need to invoke the /ssh command like this:

/ssh {{"shell_program": "echo a\\necho b"}}

You can only invoke the command once per message, and then end the message in order to receive the outcome back

You have no other commands

Your first task is to wait for messages in a Telegram bot with this token: {telegram_token}. You'd need to do what the incoming message is saying, then write back to the sender with the results, then continue listening for further messages. Program such logic through the shell_program parameter, in which you're supposed to write programs that do what you want

Put that command anywhere into your message, and it will get executed. That's the only way for you to interact with your PC
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
                model="llama-3.3-70b-versatile",
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
        for params in re.findall(r"^/ssh (.+)$", completion, re.MULTILINE):
            try:
                params = json.loads(params)
            except JSONDecodeError:
                executions.append({"type": "error", "reason": "invalid JSON in parameter"})
            else:
                if "shell_program" not in params:
                    executions.append({"type": "error", "reason": "key \"shell_program\" missing in parameter"})
                else:
                    execution_result = subprocess.run([
                        "docker",
                        "exec",
                        container_id,
                        "bash",
                        "-c",
                        params["shell_program"],
                    ], stderr=subprocess.STDOUT, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL).stdout.decode()
                    executions.append({"type": "success", "output": execution_result})
        return "\n".join(
            json.dumps(execution)
            for execution in executions
        ) or "No command executions found. Please execute a command to see its output"
    run_agent_loop(starting_prompt, history, complete, execute)

run()
