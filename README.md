# open-taranis

Python framework for AI agents logic-only coding with streaming, tool calls, and multi-LLM provider support.

Only the **"fairly stable"** versions are published on PyPi, but to get the latest experimental versions, clone this repository and install it !

## Installation

```bash
pip install open-taranis --upgrade
```
For package on **PyPi**


**or**
```bash
git clone https://github.com/SyntaxError4Life/open-taranis && cd open-taranis/ && pip install .
```
For last version

## Quick Start

<details><summary><b>Simplest</b></summary>

```python
import open_taranis as T

client = T.Clients.openrouter # API_KEY in env_var

request = T.Request(
    tools=None, tool_choice="auto",
    temperature=0.4,
    # and others....
)

print("assistant : ",end="")
for token, is_thinking, tools, tool_bool, meta in T.handle_streaming(
    request=request,
    client=client,
    model="nvidia/nemotron-3-nano-30b-a3b:free",
    messages=[T.create.user_prompt("Tell me about yourself")],
    API_KEY=None
) : 
    # You can add `if not is_thinking :` to see only the reals tokens
    print(token, end="", flush=True)

print(f"\n\n{meta}")
```
</details> 

<details><summary><b>Make a simple agent with a context windows on the 6 last turns</b></summary>

```python
import open_taranis as T

class Agent(T.agent_base):
    def __init__(self):
        super().__init__(yield_thinking=False) # If you want to return the reasoning

        self.client = T.Clients.openrouter
        self._system_prompt = [T.create.system_prompt(
            "You're an agent nammed **Taranis** !"
        )]
        self.request_profil = T.Request() # Useful for highly customized clients like Venice.ai


    def create_stream(self, history):
        return T.handle_streaming(
            self.request_profil,

            self.client,
            model="nvidia/nemotron-3-nano-30b-a3b:free",
            messages= self._system_prompt + history # Most important !
        )
    
    def manage_token_yield(self, token, is_thinking = None, meta = None, tool_calls = None):
        return token, meta # You can customize what the agent returns
    
    def manage_messages(self):
        self.messages = self.messages[-12:] # Each turn have 1 user and 1 assistant

My_agent = Agent()

while True :
    prompt = T.create.user_prompt(input("user : "))

    print("\n\nagent : ", end="")

    for t, meta in My_agent(prompt):
        print(t, end="", flush=True)
    
    print(f"\n\n{meta}\n","="*60,"\n")
```
</details>

<details><summary><b>To create a simple display using gradio as backend</b></summary>

```python
import open_taranis as T
import open_taranis.web_front as W
import gradio as gr

class Gradio_agent(T.agent_base):
    def __init__(self):
        super().__init__()

        self._system_prompt = [T.create_system_prompt("You are a agent nammed **Taranis**")]
    
    def manage_token_yield(self, token, is_thinking):
        return token, is_thinking
    
    def create_stream(self):
        return T.clients.openrouter_request(
            client=T.clients.openrouter(),
            messages=self._system_prompt+self.messages,
            model="nvidia/nemotron-3-nano-30b-a3b:free"
        )

gr.ChatInterface(
    fn=W.create_fn_gradio(Gradio_agent()),
    title="Open-taranis Agent"
).launch()
```
Here we use a temporary history provided with each request via `Agent(user_prompt=...., temporary_history=messages)`, so it is natively supported for concurrency (no persistent memory in the object).

</details>  

---

## Use the commands :

- `taranis help` : in the name...
- `taranis update` : upgrade the framework

## Documentation :

- [Base of the docs](https://zanomega.com/open-taranis/)

Available in [French](https://zanomega.com/open-taranis/fr/)
**Soon**

## Roadmap

- [X] v0.0.1: start
- [X] v0.0.x: Add and confirm other API providers (in the cloud, not locally)
- [X] v0.1.x: Functionality verifications in [examples](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/)
- [X] v0.2.x: Add features for **logic-only coding** approach, start with `agent_base`
- [X] v0.3.x: **Complete** rewrite + Add proper **documentation** and improved deployments
- [ ] v0.4.x: Improving support for **local AI deployment**
- The rest will follow soon.

## Changelog

<details><summary> <b>v0.0.x : The start</b> </summary>

- **v0.0.4** : Add **xai** and **groq** provider
- **v0.0.6** : Add **huggingface** provider and args for **clients.veniceai_request**
</details>   

<details><summary><b>v0.1.x : Gradio, commands and TUI</b></summary>
  
- **v0.1.0** : Start the **docs**, add **update-checker** and preparing for the continuation of the project...
- **v0.1.1** : Code to deploy a **frontend with gradio** added (no complex logic at the moment, ex: tool_calls)
- **v0.1.2** : Fixed a display bug in the **web_front** and experimentally added **ollama as a backend**
- **v0.1.3** : Fixed the memory reset in the **web_front** and remove **ollama module** for **openai front** (work 100 times better)
- **v0.1.4** : Fixed `web_front` for native use on huggingface, as well as `handle_streaming` which had tool retrieval issues
- **v0.1.7** : Added a **TUI** and **commands**, detection of **env variables** (API keys) and tools in the framework
</details>   

<details><summary><b>v0.2.x : Agents</b></summary>

- **v0.2.0** : Adding `agent_base`
- **v0.2.1** : Updated `agent_base` and added a more concrete example of agents
- **v0.2.2** : Upgraded all the code to add [**Kimi Code**](https://www.kimi.com/code) as client and reduce code (**Not official !**)
- **v0.2.3** : Updated `agent_base`, add some functions and add a **cool** agent
- **v0.2.4** : Improved CoT techniques and updated `web_front.py`, deploy an agent to the browser in a few lines
</details>   

<details><summary><b>v0.3.x : The restart</b></summary>

- **v0.3.0** : **Rewrite all** the code from scratch (without AI) to **improve everything**
- **v0.3.1** : The **TUI project** with **integrated agent** has been removed to focus on the **framework (useful code)**.
- **v0.3.2 (future)** : Add features for **coding [MCP](https://wikipedia.org/wiki/Model_Context_Protocol) servers and clients**
</details>   


## Advanced Examples

- [simple search agent with Brave API](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/brave_research.py)
- [full auto search agent with Brave API](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/brave_research_loop.py)
- [agent with compressible memory (recommended with Kimi)](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/infinite_agent_v1.py)

## Links

- [PyPI](https://pypi.org/project/open-taranis/)
- [GitHub Repository](https://github.com/SyntaxError4Life/open-taranis)