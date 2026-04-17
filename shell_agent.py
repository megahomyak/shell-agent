import argparse

def complete_any(completers):
    completion_or_exc = None
    for completer in completers:
        try:
            completion_or_exc = {"completion": completer()}
            break
        except Exception as e:
            completion_or_exc = {"exc": e}
    if "exc" in completion_or_exc:
        raise completion_or_exc["exc"]
    return completion_or_exc["completion"]

def run(initial_prompt, agent_state_file, completers):
    completion = complete_any(completers)


def main():
    parser = argparse.ArgumentParser("shell_agent")
    parser.add_argument("--initial-prompt")
    parser.add_argument("--agent-state")
    parser.add_argument("--ai-config")
    args = parser.parse_args()
    initial_prompt_path = args.initial_prompt
    agent_state_path = args.agent_state
    ai_config_path = args.ai_config
    completers = []
    with open(initial_prompt) as initial_prompt_file, open(agent_state_path) as agent_state_file:
        run(
            initial_prompt=initial_prompt_file.read(),
            agent_state_file=agent_state_file,
            ai_list
        )

main()
