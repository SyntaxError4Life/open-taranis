# open-taranis

Minimalist Python framework for AI agents logic-only coding with streaming, tool calls, and multi-LLM provider support.

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
    model="qwen/qwen3-4b:free", 
)

print("assistant : ",end="")
for token, tool, tool_bool in T.handle_streaming(stream) : 
    if token :
        print(token, end="")
```

## Documentation :

```
.
├── __version__ = "0.0.3_genesis"
│
├── clients
│   ├── veniceai(api_key: str) -> openai.OpenAI
│   ├── deepseek(api_key: str) -> openai.OpenAI
│   ├── openrouter(api_key: str) -> openai.OpenAI
│   │
│   ├── veniceai_request(client:openai.OpenAI, messages:list[dict], model:str, temperature:float, 
│   │   max_tokens:int, tools: list[dict], include_venice_system_prompt:bool=False, **kwargs) -> openai.Stream
│   ├── generic_request(client:openai.OpenAI, messages:list[dict], model:str, temperature:float,
│   │   max_tokens:int, tools:list[dict], **kwargs) -> openai.Stream
│   └── openrouter_request(client:openai.OpenAI, messages:list[dict], model:str, temperature:float,
│       max_tokens:int, tools:list[dict], **kwargs) -> openai.Stream
│
├── handle_streaming(stream: openai.Stream) -> generator(token: str or None, tool: list, tool_bool: bool)
├── handle_tool_call(tool_call: dict) -> tuple[str, str, dict, str]
│
├── create_assistant_response(content: str, tool_calls: list[dict]=None) -> dict
├── create_function_response(id: str, result: str, name: str) -> dict
├── create_system_prompt(content: str) -> dict[str, str]
└── create_user_prompt(content: str) -> dict[str, str]
```

## Roadmap

- [X]   v0.0.1: start
- [ ]   v0.0.x: Add and confirm other API providers
- [ ]   v0.1.x: Functionality verifications
- [ ] > v0.2.0: Add features for **logic-only coding** approach
- [ ]   v0.6.x: Add llama.cpp as backend in addition to APIs
- [ ]   v0.7.x: Add reverse proxy + server to create a dedicated full relay/backend (like OpenRouter), framework usable as server and client
- [ ]   v0.8.x: Add PyTorch as backend with `transformers` to deploy a remote server
- [ ] > v0.9.0: Total reduction of dependencies for built-in functions (unless counter-optimizations)
- [ ]   v1.0.0: First complete version in Python without dependencies
- [ ]   v1.x.x: Reduce dependencies to Python for Rust backend
- [ ]   v2.0.0: Backend totally in Rust

## Advanced Examples

- [tools call in a JSON database with Qwen3 4b](https://github.com/SyntaxError4Life/open-taranis/blob/main/examples/test_json_database.py)

## Links

- [PyPI](https://pypi.org/project/open-taranis/)
- [GitHub Repository](https://github.com/SyntaxError4Life/open-taranis)
