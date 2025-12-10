import openai
import json
import re

__version__ = "0.1.2"

import requests
from packaging import version

if True : # You can disable it btw
    try:
        response = requests.get("https://pypi.org/pypi/open-taranis/json", timeout=0.1)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        if version.parse(latest_version) > version.parse(__version__):
            print(f'New version {latest_version} available for open-taranis !\nUpdate via "pip install -U open-taranis"')
    except Exception:
        pass

class clients:

# ==============================
# The clients with their URL
# ==============================

    @staticmethod
    def generic(api_key:str, base_url:str) -> openai.OpenAI:
        """
        Use `clients.generic_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url=base_url)

    @staticmethod
    def veniceai(api_key: str) -> openai.OpenAI:
        """
        Use `clients.veniceai_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://api.venice.ai/api/v1")
    
    @staticmethod
    def deepseek(api_key: str) -> openai.OpenAI:
        """
        Use `clients.generic_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    @staticmethod
    def xai(api_key: str) -> openai.OpenAI:
        """
        Use `clients.generic_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1", timeout=3600)

    @staticmethod
    def groq(api_key: str) -> openai.OpenAI:
        """
        Use `clients.generic_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    
    @staticmethod
    def huggingface(api_key: str) -> openai.OpenAI:
        """
        Use `clients.generic_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://router.huggingface.co/v1")
    
    @staticmethod
    def openrouter(api_key: str) -> openai.OpenAI:
        """
        Use `clients.openrouter_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")   

# ==============================
# Customers for calls with their specifications
#
# Like "include_venice_system_prompt" for venice.ai or custom app for openrouter
# ==============================

    @staticmethod
    def generic_request(client: openai.OpenAI, messages: list[dict], model:str="defaut", temperature:float=0.7, max_tokens:int=4096, tools:list[dict]=None, **kwargs) -> openai.Stream:
        base_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "max_completion_tokens": kwargs.get("max_completion_tokens", 4096),
            "stream": kwargs.get("stream", True),
        }
        
        tool_params = {}
        if tools :
            tool_params = {
                "tools": tools,
                "tool_choice": kwargs.get("tool_choice", "auto")
            }
        
        params = {**base_params, **tool_params}
        
        return client.chat.completions.create(**params)

    @staticmethod
    def veniceai_request(client: openai.OpenAI, messages: list[dict], 
                        model:str="venice-uncensored", temperature:float=0.7, max_tokens:int=4096, tools:list[dict]=None, 
                        include_venice_system_prompt:bool=False, 
                        enable_web_search:bool=False,
                        enable_web_citations:bool=False,
                        disable_thinking:bool=False,
                        **kwargs) -> openai.Stream:
        base_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "max_completion_tokens": kwargs.get("max_completion_tokens", 4096),
            "stream": kwargs.get("stream", True),
        }
        
        tool_params = {}
        if tools :
            tool_params = {
                "tools": tools,
                "tool_choice": kwargs.get("tool_choice", "auto")
            }
        
        venice_params = {
            "extra_body": {
                "venice_parameters": {
                    "include_venice_system_prompt" : include_venice_system_prompt,
                    "enable_web_search" : "on" if enable_web_search else "off",
                    "enable_web_citations" : enable_web_citations,
                    "disable_thinking" : disable_thinking
                }
            }
        }
        
        params = {**base_params, **tool_params, **venice_params}
        
        return client.chat.completions.create(**params)

    @staticmethod
    def openrouter_request(client: openai.OpenAI, messages: list[dict], model:str="nvidia/nemotron-nano-9b-v2:free", temperature:float=0.7, max_tokens:int=4096, tools:list[dict]=None, **kwargs) -> openai.Stream:
        base_params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "max_completion_tokens": kwargs.get("max_completion_tokens", 4096),
            "stream": kwargs.get("stream", True),
        }
        
        tool_params = {}
        if tools :
            tool_params = {
                "tools": tools,
                "tool_choice": kwargs.get("tool_choice", "auto")
            }
        
        params = {**base_params, **tool_params}
        
        return client.chat.completions.create(
            **params,
            extra_headers={
                "HTTP-Referer": "https://zanomega.com/open-taranis/",
                "X-Title": "open-taranis"
            }
        )

# ==============================
# ollama, experimental and non-mandatory installation
# ==============================

try:
    import ollama # Code by Grok 4.1 on Venice.ai

    @staticmethod
    def ollama_request(messages: list[dict], model: str="Qwen3:4b", temperature: float=0.4, max_tokens: int=4096, tools: list[dict]=None, **kwargs):
        """
        Streaming requests with Ollama (local).
        Returns OpenAI-compatible ChatCompletionChunk stream for handle_streaming.
        Supports tool calls.
        """
        import time
        import json

        # OpenAI-compatible classes for handle_streaming
        class Function:
            def __init__(self, name="", arguments=""):
                self.name = name
                self.arguments = arguments

        class ToolCall:
            def __init__(self, index=0, id="", type="function", function=None):
                self.index = index
                self.id = id
                self.type = type
                self.function = function or Function()

        class Delta:
            def __init__(self, content="", tool_calls=None, finish_reason=None):
                self.content = content
                self.tool_calls = tool_calls
                self.finish_reason = finish_reason

        class Choice:
            def __init__(self, index=0, delta=None, finish_reason=None):
                self.index = index
                self.delta = delta or Delta()
                self.finish_reason = finish_reason

        class Chunk:
            def __init__(self, id="", object="chat.completion.chunk", model="", choices=None, created=0):
                self.id = id
                self.object = object
                self.model = model
                self.choices = choices or []
                self.created = created

        # Transform messages from OpenAI format to Ollama format
        ollama_messages = []
        for msg in messages:
            new_msg = dict(msg)

            # Transform tool_calls in assistant messages (OpenAI → Ollama)
            if "tool_calls" in new_msg and new_msg["tool_calls"]:
                transformed_tool_calls = []
                for tc in new_msg["tool_calls"]:
                    args = tc.get("function", {}).get("arguments", "{}")
                    # Ollama wants dict, OpenAI sends string JSON
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    # Ollama doesn't want id/type, only function
                    transformed_tool_calls.append({
                        "function": {
                            "name": tc.get("function", {}).get("name", ""),
                            "arguments": args
                        }
                    })
                new_msg["tool_calls"] = transformed_tool_calls

            ollama_messages.append(new_msg)

        # Map parameters to Ollama options format
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
        }
        if "max_completion_tokens" in kwargs:
            options["num_predict"] = kwargs["max_completion_tokens"]
        # Add other options from kwargs (exclude non-ollama params)
        for key, value in kwargs.items():
            if key not in ["tool_choice", "stream", "max_completion_tokens", "client"]:
                options[key] = value

        params = {
            "model": model,
            "messages": ollama_messages,
            "options": options,
            "stream": True,
        }
        if tools:
            params["tools"] = tools

        ollama_stream = ollama.chat(**params)

        base_time = int(time.time())
        chunk_id = f"chatcmpl-ollama-{base_time}"
        generated_ids = {}

        for ollama_chunk in ollama_stream:
            message = ollama_chunk.get("message", {})
            content = message.get("content", "")
            tool_calls_raw = message.get("tool_calls") or []

            # Transform tool_calls: Ollama dict → OpenAI object format
            tool_calls_transformed = None
            if tool_calls_raw:
                tool_calls_transformed = []
                for i, tc in enumerate(tool_calls_raw):
                    if i not in generated_ids:
                        generated_ids[i] = f"call_{i}_{base_time}"

                    func_data = tc.get("function", {})

                    # Handle arguments: Ollama returns dict, OpenAI expects JSON string
                    args = func_data.get("arguments", "")
                    if isinstance(args, dict):
                        args = json.dumps(args)

                    function_obj = Function(
                        name=func_data.get("name", ""),
                        arguments=args
                    )
                    tool_call_obj = ToolCall(
                        index=i,
                        id=generated_ids[i],
                        type="function",
                        function=function_obj
                    )
                    tool_calls_transformed.append(tool_call_obj)

            # Final chunk
            if ollama_chunk.get("done", False):
                delta = Delta(content="", tool_calls=None, finish_reason="stop")
                choice = Choice(0, delta, "stop")
                yield Chunk(chunk_id, model=model, choices=[choice], created=base_time)
                break

            # Yield content or tool_calls
            if content or tool_calls_transformed:
                delta = Delta(content=content, tool_calls=tool_calls_transformed)
                choice = Choice(0, delta)
                yield Chunk(chunk_id, model=model, choices=[choice], created=base_time)

except:
    pass

# ==============================
# Functions for the streaming
# ==============================

def handle_streaming(stream: openai.Stream):
    """
    return :
    - token : str or None
    - tool : list
    - tool_bool : bool
    """
    tool_calls = []
    accumulated_tool_calls = {}
    arg_chunks = {}  # Per tool_call index: list of argument chunks

    # Process each chunk
    for chunk in stream:
        # Skip if no choices
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta is None:
            continue

        # Handle content streaming
        if delta.content :
            yield delta.content, [], False

        # Handle tool calls in delta
        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                index = tool_call.index
                if index not in accumulated_tool_calls:
                    accumulated_tool_calls[index] = {
                        "id": tool_call.id,
                        "function": {"name": "", "arguments": ""},
                        "type": tool_call.type,
                        "arg_chunks": []  # New: list for arguments
                    }
                    arg_chunks[index] = []
                    if tool_call.function.name:
                        # Ollama sends full name each chunk, OpenAI sends incrementally
                        if accumulated_tool_calls[index]["function"]["name"] == "":
                            accumulated_tool_calls[index]["function"]["name"] = tool_call.function.name
                        # else: skip (already set, don't +=)
                    if tool_call.function.arguments:
                        # Append to list instead of +=
                        arg_chunks[index].append(tool_call.function.arguments)

    # Stream finished - check if we have accumulated tool calls
    # Finalize arguments for each tool call
    for idx in accumulated_tool_calls:
        call = accumulated_tool_calls[idx]
        # Join arg chunks
        joined_args = ''.join(arg_chunks.get(idx, []))
        if joined_args:
            # Try to parse the full joined string
            try:
                parsed_args = json.loads(joined_args)
                call["function"]["arguments"] = json.dumps(parsed_args)
            except json.JSONDecodeError:
                # Fallback: attempt to extract valid JSON substring
                # Look for balanced braces starting from end
                start = joined_args.rfind('{')
                if start != -1:
                    potential_json = joined_args[start:]
                    try:
                        parsed_args = json.loads(potential_json)
                        call["function"]["arguments"] = json.dumps(parsed_args)
                    except json.JSONDecodeError:
                        # Last resort: use raw joined as string
                        call["function"]["arguments"] = joined_args
                else:
                    call["function"]["arguments"] = joined_args

    if accumulated_tool_calls:
        tool_calls = [
            {
                "id": call["id"],
                "function": call["function"],
                "type": call["type"]
            }
            for call in accumulated_tool_calls.values()
        ]
    yield "", tool_calls, len(tool_calls) > 0

def handle_tool_call(tool_call:dict) -> tuple[str, str, dict, str] :
    """
    Return :
    - function id : str
    - function name : str
    - arguments : dict
    - error_message : str 
    """
    fid = tool_call.get("id", "")
    fname = tool_call.get("function", {}).get("name", "")
    raw_args = tool_call.get("function", {}).get("arguments", "{}")
    
    try:
        cleaned = re.sub(r'(?<=\d)_(?=\d)', '', raw_args)
        args = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return fid, fname, {}, str(e)

    return fid, fname, args, ""

# ==============================
# Functions to simplify the messages roles
# ==============================

def create_assistant_response(content:str, tool_calls:list[dict]=None) -> dict[str, str]:
    """
    Creates an assistant message, optionally with tool calls.
    
    Args:
        content (str): Textual content of the response
        tool_calls (list[dict], optional): List of tool calls
        
    Returns:
        dict: Message formatted for the API
    """
    if tool_calls : return {"role": "assistant","content": content,"tool_calls": tool_calls}
    return {"role": "assistant","content": content}

def create_function_response(id:str, result:str, name:str) -> dict[str, str, str]:
    if not id or not name:
        raise ValueError("id and name are required")
    return {"role": "tool", "content": json.dumps(result), "tool_call_id": id, "name": name}

def create_system_prompt(content:str) -> dict[str, str] :
    return {"role":"system", "content":content}

def create_user_prompt(content:str) -> dict[str, str] :
    return {"role":"user", "content":content}

# ==============================
# Agents coding (v0.2.0)
# ==============================

# class Agent():
#     def __init__(self):
#         pass
#
#    def __call__(self):
#        pass
#
#    ...