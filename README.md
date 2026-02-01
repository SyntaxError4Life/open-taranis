# open-taranis

Python framework for AI agents logic-only coding with streaming, tool calls, and multi-LLM provider support.

## Installation

```bash
pip install open-taranis --upgrade
```

## Quick Start

```python
import open_taranis as T

client = T.clients.openrouter("api_key")

messages = [
    T.create_user_prompt("Tell me about yourself")
]

stream = T.clients.openrouter_request(
    client=client,
    messages=messages,
    model="mistralai/mistral-7b-instruct:free", 
)

print("assistant : ",end="")
for token, tool, tool_bool in T.handle_streaming(stream) : 
    if token :
        print(token, end="")
```

To create a simple display using gradio as backend :
```python
import open_taranis as T
import open_taranis.web_front as W
import gradio as gr

gr.ChatInterface(
    fn=W.chat_fn_gradio(
    client=T.clients.openrouter(API_KEY),
    request=T.clients.openrouter_request,
    model="mistralai/mistral-7b-instruct:free",
    _system_prompt="You are an agent named **Taranis**"
).create_fn(),
    title="web front"
).launch()
```

---

## Use the commands :

- `taranis help` : in the name...
- `taranis update` : upgrade the framework
- `taranis open` : open the TUI

### The TUI :
![TUI](img/TUI.png)

- `/help` to start

## Documentation :

- [Base of the docs](https://zanomega.com/open-taranis/) (coding some things before the real docs)

## Roadmap

- [X]   v0.0.1: start
- [X]   v0.0.x: Add and confirm other API providers (in the cloud, not locally)
- [X]   v0.1.x: Functionality verifications in [examples](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/)
- [ ] > v0.2.0: Add features for **logic-only coding** approach
- The rest will follow soon.

## Changelog

- **v0.0.4** : Add **xai** and **groq** provider
- **v0.0.6** : Add **huggingface** provider and args for **clients.veniceai_request**
- **v0.1.0** : Start the **docs**, add **update-checker** and preparing for the continuation of the project...
- **v0.1.1** : Code to deploy a **frontend with gradio** added (no complex logic at the moment, ex: tool_calls)
- **v0.1.2** : Fixed a display bug in the **web_front** and experimentally added **ollama as a backend**
- **v0.1.3** : Fixed the memory reset in the **web_front** and remove **ollama module** for **openai front** (work 100 times better)
- **v0.1.4** : Fixed `web_front` for native use on huggingface, as well as `handle_streaming` which had tool retrieval issues
- **v0.1.7** : Added a **TUI** and **commands**, detection of **env variables** (API keys) and tools in the framework

## Advanced Examples

- [tools call in a JSON database](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/test_json_database.py)
- [tools call in a HR JSON database in multi-rounds](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/test_HR_json_database.py)
- [simple search agent with Brave API](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/brave_research.py)

## Links

- [PyPI](https://pypi.org/project/open-taranis/)
- [GitHub Repository](https://github.com/SyntaxError4Life/open-taranis)