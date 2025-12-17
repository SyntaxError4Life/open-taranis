import openai
import json
import re

# For the python function to JSON/dict
import inspect
from typing import Any, Callable, Literal, Union, get_args, get_origin


__version__ = "0.1.4"

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

# ==============================
# 
# ==============================

class utils:
    def _parse_simple_docstring(doc: str | None) -> dict[str, Any]:
        """Parse docstring minimal (description + args)."""
        result = {"description": "", "args": {}}
        if not doc:
            return result
        
        # Extract main description (first paragraph)
        parts = inspect.cleandoc(doc).split('\n\n', 1)
        result["description"] = parts[0].strip()
        
        # Simple args parsing (Google/NumPy style)
        if len(parts) > 1:
            args_section = parts[1].split('Args:')[-1].split('Returns:')[0].split('Raises:')[0]
            lines = [l.strip() for l in args_section.split('\n') if l.strip()]
            
            for line in lines:
                if ':' in line and not line.startswith(' '):
                    # Format: "arg_name: description" or "arg_name (type): description"
                    arg_match = re.match(r'(\w+)\s*(?:\([^)]*\))?\s*:\s*(.+)', line)
                    if arg_match:
                        arg_name, desc = arg_match.groups()
                        result["args"][arg_name] = desc.strip()
        
        return result

    def _python_type_to_schema(py_type: Any) -> dict[str, Any]:
        """Convert Python type to JSON Schema - MINIMAL version."""
        origin = get_origin(py_type)
        args = get_args(py_type)
        
        # Optional: Union[X, None]
        if origin is Union and type(None) in args:
            non_none = [a for a in args if a is not type(None)]
            if len(non_none) == 1:
                schema = utils._python_type_to_schema(non_none[0])
                schema["nullable"] = True
                return schema
        
        # Literal for enums
        if origin is Literal:
            return {"type": "string", "enum": list(args)}
        
        # Basic types
        if py_type in (str, int, float, bool, type(None)):
            type_map = {str: "string", int: "integer", float: "number", bool: "boolean", type(None): "null"}
            return {"type": type_map[py_type]}
        
        # Collections
        if origin in (list,):
            item_schema = {"type": "string"}  # Default
            if args:
                item_schema = utils._python_type_to_schema(args[0])
            return {"type": "array", "items": item_schema}
        
        if origin in (dict,):
            return {"type": "object"}
        
        # Default fallback
        return {"type": "string"}

    def function_to_openai_tool(func: Callable) -> dict[str, Any]:
        """Convert Python function to OpenAI tool format - MINIMAL."""
        sig = inspect.signature(func)
        type_hints = func.__annotations__
        
        # Parse docstring
        doc_info = utils._parse_simple_docstring(func.__doc__ or "")
        
        # Build schema
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Get type annotation
            py_type = type_hints.get(param_name, str)
            schema = utils._python_type_to_schema(py_type)
            
            # Add description from docstring
            if param_name in doc_info["args"]:
                schema["description"] = doc_info["args"][param_name]
            
            # Handle defaults
            if param.default is not inspect.Parameter.empty:
                schema["default"] = param.default
                if param.default is None:
                    schema["nullable"] = True
            else:
                required.append(param_name)
            
            properties[param_name] = schema
        
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": doc_info["description"],
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        }

# Utility for multiple functions, code by Kimi k2 thinking
def functions_to_tools(funcs: list[Callable]) -> list[dict[str, Any]]:
    return [utils.function_to_openai_tool(f) for f in funcs]


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

    @staticmethod
    def ollama() -> openai.OpenAI:
        """
        Use `clients.generic_request` for call
        """
        return openai.OpenAI(api_key="", base_url="http://localhost:11434/v1")   

# ==============================
# Customers for calls with their specifications"
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
                if tool_call.function:
                    if tool_call.function.name:
                        accumulated_tool_calls[index]["function"]["name"] += tool_call.function.name
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