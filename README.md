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

## Documentation :

- [Base of the docs](https://zanomega.com/open-taranis/) (coding some things before the real docs)

## Roadmap

- [X]   v0.0.1: start
- [X]   v0.0.x: Add and confirm other API providers (in the cloud, not locally)
- [X]   v0.1.x: Functionality verifications in [examples](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/)
- [ ] > v0.2.0: Add features for **logic-only coding** approach
- [ ]   v0.6.x: Add llama.cpp as backend in addition to APIs
- [ ]   v0.7.x: Add reverse proxy + server to create a dedicated full relay/backend (like OpenRouter), framework usable as server and client
- [ ]   v0.8.x: Add PyTorch as backend with `transformers` to deploy a remote server
- [ ]   v0.9.x: Total reduction of dependencies for built-in functions (unless counter-optimizations)
- [ ]   v1.0.0: First complete version in Python without dependencies

## Changelog

- **v0.0.4** : Add **xai** and **groq** provider
- **v0.0.6** : Add **huggingface** provider and args for **clients.veniceai_request**
- **v0.1.0** : Start the **docs**, add **update-checker** and preparing for the continuation of the project...
- **v0.1.1** : Code to deploy a **frontend with gradio** added (no complex logic at the moment, ex: tool_calls)
- **v0.1.2** : Fixed a display bug in the **web_front** and experimentally added **ollama as a backend**
- **v0.1.3** : Fixed the memory reset in the **web_front** and remove **ollama module** for **openai front** (work 100 times better)
- **v0.1.4** : Fixed `web_front` for native use on huggingface, as well as `handle_streaming` which had tool retrieval issues

## Advanced Examples

- [tools call in a JSON database](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/test_json_database.py)
- [tools call in a HR JSON database in multi-rounds](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/test_HR_json_database.py)

## Links

- [PyPI](https://pypi.org/project/open-taranis/)
- [GitHub Repository](https://github.com/SyntaxError4Life/open-taranis)
