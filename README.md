# shell\_agent

"shell agent" is the simplest AI agent there can be

the most unstable one as well

build on passing LLM's outputs to Bash and Bash's outputs back to the LLM, and it all starts with a system prompt to get the LLM going

## concepts

* autonomy: the main loop never stops. also since this is so barebones, you'll need a smart enough llm, or at least something with pretty good reasoning, something that won't keep making mistakes in a loop burning your money and not understanding what's going on. ow
* temporary memory: the LLM's "context window" is like its temporary memory. only for tasks that are very "in the moment", everything else should go to permanent memory
* permanent memory: `MEMORY.md` for the LLM. all the stuff that's important goes there
* thinking: every Bash script should be thought through. thinking is not part of the general architecture because the LLM should think about its outputs by itself, and then the thinking is omitted. when humans write bash, they don't think in writing, they think *before* writing, so you should make the llm think *yourself* if it needs that. also, the format is very unusual, and usually llms respond with Markdown, so you may need one extra step telling it to respond with a Bash script. LLMs don't think, humans do, so let's emulate humans
* pausing: the llm will decide when to pause by itself. it can just run a script like `sleep 30m` and get sleeping for 30 minutes. if that's an issue for you, you may add timeouts to Bash execution

## what to instruct to the llm

* tell it it's writing Bash and only Bash; some other formats may accidentally work as Bash, but make the model know it should output *only* Bash. does not apply to thinking, thinking should be whatever it wants to do more
* emphasize to the LLM that it has its own computer that it can use however it wants, and that it's only writing Bash to control the computer, it should only write Bash for its own reasons, that Bash will never be seen by anyone but the computer and the LLM. the LLM should use the computer as a tool, not for show
* maybe it's worth saying that the "user's" outputs (as they are in the model API) are not actually the user but just the computer's execution of the script that the LLM provides. just so it won't think someone can actually see the stuff it writes
* tell it it's **very** forgetful so it should edit its memory file - `~/MEMORY.md` - as its memory and always be sure that it can see at least one full read of `~/MEMORY.md` in its chat history (or context, or dialogue, or however you wanna call it), and if it can't, it means it has forgotten its `~/MEMORY.md` and should display its contents to itself. it should use that file religiously if its context window is tiny
* if you're worried about it burning too many tokens, you may ask it to sleep for events that it needs
* since LLMs love outputting huge programs, you may want to either tell it to output tiny programs and go step by step collecting outputs, or write huge tools once and then just call them. or both
* if you want to talk to it, you'd need some communication channel. you can give it e.g. Telegram bot creds in the instructing prompt, it will contact you there on its own, no need for extra scaffolding
* the LLM should probably return control to it ASAP. so e.g. listening on Telegram until a message arrives, the message gets printed back to the LLM, and control returns to the LLM. it should really never block itself

## how to run the current agent

`shell_agent.sh` is too experimental, so i'm gonna be talking about `shell_agent.py`

### prerequisites

* `instructing_prompt.txt`
* `openrouter_api_key.txt`
* a running LXC container with the name `shell-agent`

#### how to create and run that LXC container

```bash
lxc-create shell-agent -t download -- -d debian -r trixie -a amd64
lxc-start shell-agent
```

### running

* install `poetry`
* `poetry install --no-root` - installs dependencies
* `poetry run python shell_agent.py`

and there you go, here's your little creature in a computer
