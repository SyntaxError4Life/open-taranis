import openai
import json
import re

__version__ = "0.0.5", "genesis"

class clients:

# ==============================
# The clients with their URL
# ==============================

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
    def openrouter(api_key: str) -> openai.OpenAI:
        """
        Use `clients.openrouter_request` for call
        """
        return openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

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

# ==============================
# Customers for calls with their specifications
#
# Like "include_venice_system_prompt" for venice.ai or custom app for openrouter
# ==============================

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
                "HTTP-Referer": "https://zanomega.com/",
                "X-Title": "Zanomega/open-taranis"
            }
        )

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
