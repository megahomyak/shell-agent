import groq as groq_sdk
import readline

PROMPT = f"""
Please help me fix my shell-only assistant. I take an LLM, give it the "initial prompt" ("prompt.txt" below) and just pipe all of the LLM's output to Bash (via `bash -c "$LLM_INPUT"`), and the stdout+stderr from Bash I send back to the LLM, and it loops like that - that's my "AI agent". I will not change the agent's architecture and will not switch to tool use because I want my agent to be truly minimalistic. I understand that my approach is unusual and may be somewhat limiting, but I want to achieve good, intelligent behavior through giving it a good enough initial prompt. Bash is on a VM so it's fine to allow the LLM to run whatever it wants. However, the LLM behaves strangely. Analyze the given history, find what the issues were because of which the LLM couldn't understand my desires well enough, and respond with a new, fixed prompt.txt (your entire response should just be the new contents of prompt.txt)

history.json:
{open("history.json").read()}

prompt.txt:
\"""
{open("prompt.txt").read()}
\"""

Please respond in a format that will be readable as plain text. Please, do NOT rely on formatting techniques that rely on text elements relating to each other vertically

{input("Your complaint here: ")}
""".strip()

groq = groq_sdk.Groq()
completion = groq.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": PROMPT}],
    max_completion_tokens=None,
).choices[0].message.content
print(completion)
