from requests import (
    post as requests_post,
    get as requests_get
)
from requests.exceptions import HTTPError, RequestException, Timeout, ConnectionError

import json
import os
import re

# For the python function to JSON/dict
import inspect
from typing import Any, Callable, Literal, Union, get_args, get_origin

# For function "image_to_base64"
from base64 import b64encode
from mimetypes import guess_type as guess_image_type

__version__ = "0.3.1"

from packaging import version

if True : # You can disable it btw
    try:
        response = requests_get("https://pypi.org/pypi/open-taranis/json", timeout=0.1)
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
        if version.parse(latest_version) > version.parse(__version__):
            print(f'New version {latest_version} available for open-taranis !\nUpdate via "pip install -U open-taranis\n"')
    except Exception:
        pass


# ==============================
# 
# ==============================


class Client:
    def __init__(self, 
                 API_KEY_name:str,  # Pour récupérer dans l'env
                 BASE_URL:str,      # L'URL de base
                 default_headers: dict | None = None,
                ):
        self.API_KEY_name = API_KEY_name
        self.BASE_URL = BASE_URL

        self.default_headers = default_headers or {}
    
    def __call__(self, API_KEY:str=None): # Simplifier
        if self.API_KEY_name != "" : # Cas de ollama
            if API_KEY : 
                return API_KEY
            return os.environ.get(self.API_KEY_name)

class Request:
    def __init__(self,
            tools: list[dict] | None = None, tool_choice: str | dict = "auto", temperature: float = 0.4,
            top_p: float = 1.0, max_tokens: int = 4096, stop: str | list[str] | None = None,
            presence_penalty: float = 0.0, frequency_penalty: float = 0.0,
            response_format: dict | None = None, seed: int | None = None):
        
        payload = {
            "model": None, # À définir dans make
            "messages": None, # À définir dans make
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": True
        }
    
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice
    
        if stop is not None:
            payload["stop"] = stop
    
        if presence_penalty != 0.0:
            payload["presence_penalty"] = presence_penalty
    
        if frequency_penalty != 0.0:
            payload["frequency_penalty"] = frequency_penalty
    
        if response_format is not None:
            payload["response_format"] = response_format
    
        if seed is not None:
            payload["seed"] = seed

        self.payload = payload

    def make(self, client:Client, model:str, messages:list[dict], API_KEY:str=None):
        payload = self.payload.copy()
        payload["model"] = model
        payload["messages"] = messages

        headers = {
            "Authorization": f"Bearer {client(API_KEY)}",
            "Content-Type": "application/json"
        }

        if client.default_headers:
            headers = {**client.default_headers, **headers}

        try:
            R = requests_post(
                f"{client.BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            R.raise_for_status()
            return R

        except HTTPError as e:
            # L'API renvoie souvent des détails sur l'erreur
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            raise RuntimeError(f"HTTP Error {e.response.status_code}: {error_detail}")
        except Timeout:
            raise TimeoutError("The request has expired.")
        except ConnectionError:
            raise ConnectionError(f"Unable to connect to {client.BASE_URL}")
        except RequestException as e:
            raise RuntimeError(f"Error during API call : {e}")

# Copy from v0.2.4
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


# ==============================
# The clients with their URL
# ==============================


class Clients :

    veniceai = Client("VENICE_API_KEY", "https://api.venice.ai/api/v1")

    deepseek = Client("DEEPSEEK_API_KEY","https://api.deepseek.com")

    xai = Client("XAI_API_KEY", "https://api.x.ai/v1")

    groq = Client("GROQ_API_KEY", "https://api.groq.com/openai/v1")

    huggingface = Client("HUGGINGFACE_API_KEY", "https://router.huggingface.co/v1")

    mistralai = Client("MISTRALAI_API_KEY", "https://api.mistral.ai/v1")

    openrouter = Client("OPENROUTER_API_KEY", "https://openrouter.ai/api/v1",
                        default_headers={"HTTP-Referer": "https://zanomega.com/open-taranis/","X-Title": "open-taranis"
    })

    ollama = Client("", "http://localhost:11434/v1")

    kimi_code = Client("KIMI_CODE_API_KEY", "https://api.kimi.com/coding/v1",
        default_headers={"User-Agent": "RooCode/3.53.0","HTTP-Referer": "https://github.com/RooVetGit/Roo-Cline","X-Title": "Roo Code"}
    )

class VeniceRequest(Request):
    def __init__(self, tools = None, tool_choice = "auto", 
                include_venice_system_prompt:bool=False,
                enable_web_search:bool=False,
                enable_web_citations:bool=False,
                disable_thinking:bool=False,
                temperature = 0.4, top_p = 1, max_tokens = 4096, stop = None, presence_penalty = 0, frequency_penalty = 0, response_format = None, seed = None):
        super().__init__(tools, tool_choice, temperature, top_p, max_tokens, stop, presence_penalty, frequency_penalty, response_format, seed)

        self.payload["venice_parameters"] = {
                    "include_venice_system_prompt": include_venice_system_prompt,
                    "enable_web_search": "on" if enable_web_search else "off",
                    "enable_web_citations": enable_web_citations,
                    "disable_thinking": disable_thinking
                }


# ==============================
# Functions to simplify the messages roles
# ==============================


class create:

    @staticmethod
    def system_prompt(content:str) -> dict[str, str] :
        return {"role":"system", "content":content}

    @staticmethod
    def user_prompt(content:str=None, images:list[str] = None) -> dict:

        # Cas simple : texte seul sans image
        if images is None :
            return {"role": "user", "content": content}

        # Construction du format multimodal
        content_list = []

        if content :
            content_list.append({"type": "text", "text": content})

        for img in images :
            if img.startswith("http") or img.startswith("HTTP"):
                content_list.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })
            else:
                # Supposé être du base64
                content_list.append({
                    "type": "image_url",
                    "image_url": {"url": img}
                })

        return {"role": "user", "content": content_list}

    @staticmethod
    def assistant_response(content:str, tool_calls:list[dict]=None, reasoning_content:str=None) -> dict[str, str]:
        r = {"role": "assistant","content": content}
        if tool_calls : 
            r.update({"tool_calls":tool_calls})
        if reasoning_content :
            r.update({"reasoning_content":reasoning_content})
        return r
    
    @staticmethod
    def function_response(id:str, result:str, name:str) -> dict[str, str, str]:
        if not id or not name:
            raise ValueError("id and name are required")
        return {"role": "tool", "content": json.dumps(result), "tool_call_id": id, "name": name}


class remove_from:
    
    def user_prompt(prompt:dict, content:bool=False, images:bool=False):
        
        # Cas simple : texte seul
        if isinstance(prompt["content"], str):
            if content:
                return {"role": "user", "content": ""}
            return prompt
        
        # Cas multimodal : liste de contenus
        new_content = []
        for item in prompt["content"]:
            if item["type"] == "text" and content:
                continue
            if item["type"] == "image_url" and images:
                continue
            new_content.append(item)
        
        # Si images supprimées, simplifier en string
        if images:
            text_content = ""
            for item in new_content:
                if item["type"] == "text":
                    text_content = item["text"]
                    break
            return {"role": "user", "content": text_content}
        
        return {"role": "user", "content": new_content}

    def assistant_response(response: dict, content:bool=False, reasoning:bool=False, tool_calls:bool=False):
        result = {"role": "assistant"}
        
        if content:
            result["content"] = ""
        else:
            result["content"] = response.get("content", "")
        
        if not reasoning and "reasoning_content" in response:
            result["reasoning_content"] = response["reasoning_content"]
        
        if not tool_calls and "tool_calls" in response:
            result["tool_calls"] = response["tool_calls"]
        
        return result
    
    def function_response(response:dict, content:bool=False):
        result = {
            "role": "tool",
            "tool_call_id": response["tool_call_id"],
            "name": response["name"]
        }
        
        if content:
            result["content"] = ""
        else:
            result["content"] = response.get("content", "")
        
        return result
    
    def auto(messages:list[dict], user_content:bool=False, user_images:bool=False,
        assistant_content:bool=False, assistant_reasoning:bool=False,
        tool_calls:bool=False, tool_response:bool=False) -> list[dict]:
    
        result = []
        
        for msg in messages:
            role = msg.get("role")
            
            if role == "user":
                result.append(remove_from.user_prompt(msg, content=user_content, images=user_images))
            elif role == "assistant":
                result.append(remove_from.assistant_response(msg, content=assistant_content, 
                                                            reasoning=assistant_reasoning, 
                                                            tool_calls=tool_calls))
            elif role == "tool":
                result.append(remove_from.function_response(msg, content=tool_response))
            else:
                result.append(msg)
        
        return result


# ==============================
# Functions for the streaming
# ==============================


@staticmethod
def image_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    
    mime_type, _ = guess_image_type(path)
    if mime_type is None:
        mime_type = "image/jpeg"
    
    encoded = b64encode(data).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"

@staticmethod
def handle_streaming(request:Request, client:Client, model:str, messages:list[dict], API_KEY:str=None):
    assert isinstance(request, Request), "Incorrect request type !"
    assert isinstance(client, Client), "Not a good type of client !"

    response = request.make(
        client=client,
        model=model,
        messages=messages,
        API_KEY=API_KEY
    )
    
    is_thinking:bool=False

    tool_calls_accumulator = {}
    arg_chunks = {}  
    tool_calls = []

    last_package=None
    meta = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cached_tokens": 0
    }
      
    for line in response.iter_lines(): # Cas sans ligne
        if not line:
            continue

        TOKEN = ""
        COT_TOKEN = ""
          
        line_str = line.decode("utf-8")
          
        if line_str.startswith("data:") and not line_str.startswith("data: "): # Cas où on reçoit mal les données
            line_str = line_str.replace("data:", "data: ", 1)
          
        if not line_str.startswith("data: "): # Cas où on reçoit rien, on passe
            continue
              
        data = line_str[6:].strip() # Récupérer les données (les chunks ou [DONE])
          
        if data == "[DONE]": # Récupérer les données de fin avec les entrées/sorties
            # Extraction des métadonnées du dernier paquet
            
            if last_package:
                try:
                    last_chunk = json.loads(last_package)
                    usage = last_chunk.get("usage", {})
                    
                    if usage:
                        meta["prompt_tokens"] = usage.get("prompt_tokens", 0)
                        meta["completion_tokens"] = usage.get("completion_tokens", 0)
                        
                        # Cache : formats variés selon les endpoints
                        prompt_details = usage.get("prompt_tokens_details", {})
                        if prompt_details:
                            # DeepSeek, HuggingFace, Mistral, OpenRouter
                            meta["cached_tokens"] = prompt_details.get("cached_tokens", 0)
                            # HuggingFace alternative
                            if meta["cached_tokens"] == 0:
                                meta["cached_tokens"] = prompt_details.get("cache_read_input_tokens", 0)
                        
                        # DeepSeek alternative
                        if meta["cached_tokens"] == 0:
                            meta["cached_tokens"] = usage.get("prompt_cache_hit_tokens", 0)
                        
                        # Groq : usage direct (pas de cache)
                        if "x_groq" in last_chunk:
                            x_groq = last_chunk.get("x_groq", {})
                            usage_groq = x_groq.get("usage", {})
                            if usage_groq:
                                meta["prompt_tokens"] = usage_groq.get("prompt_tokens", meta["prompt_tokens"])
                                meta["completion_tokens"] = usage_groq.get("completion_tokens", meta["completion_tokens"])
                                
                except json.JSONDecodeError:
                    pass
            
            yield "", False, [], False, meta
            break
            
          
        try:
            chunk = json.loads(data)
            chunk["_is_valid_json"] = True
        except json.JSONDecodeError:
            # Pas du JSON valide, on crée quand même un dict exploitable
            chunk = {"_is_valid_json": False, "_raw": data}

        choices = chunk.get("choices", [])
        
        last_package = data
        if not choices:  # choices vide, on passe
            continue
            
        delta = choices[0].get("delta", {})
            
        # === RAISONNEMENT ===
            
        # Cas 1: reasoning_content (Venice AI, DeepSeek, HuggingFace, Kimi)
        if "reasoning_content" in delta and delta["reasoning_content"]:
            COT_TOKEN = delta["reasoning_content"]
            
        # Cas 2: reasoning string (Groq, Ollama)
        elif "reasoning" in delta and isinstance(delta.get("reasoning"), str) and delta["reasoning"]:
            COT_TOKEN = delta["reasoning"]
            
        # Cas 3: content liste avec thinking (Mistral natif)
        elif isinstance(delta.get("content"), list):
            for item in delta["content"]:
                if isinstance(item, dict) and item.get("type") == "thinking":
                    thinking_parts = item.get("thinking", [])
                    if isinstance(thinking_parts, list):
                        for t in thinking_parts:
                            if isinstance(t, dict) and t.get("text"):
                                COT_TOKEN = t["text"]

        # === CONTENU NORMAL ===
            
        # Cas 1: content string (tous les endpoints)
        if isinstance(delta.get("content"), str) and delta["content"]:
            TOKEN = delta["content"]
            
        # Cas 2: content liste avec text (Mistral natif - phase réponse)
        elif isinstance(delta.get("content"), list):
            for item in delta["content"]:
                if isinstance(item, dict) and item.get("type") == "text":
                    if item.get("text"):
                        TOKEN = item["text"]
                

        # === RAISONNEMENT DANS CONTENT ===

        temp_token = TOKEN # Temporaire

        if "<think>" in temp_token or is_thinking : # Détecter <think>
            TOKEN = ""
            COT_TOKEN = temp_token
            is_thinking = True

            if "</think>" in temp_token:
                is_thinking = False
            
            COT_TOKEN = re.sub(r"<think>|</think>", "", COT_TOKEN)
        
        # === TOOL CALLS (support 1 à infini) ===

        if "tool_calls" in delta and delta["tool_calls"]:
            for tc in delta["tool_calls"]:
                idx = tc.get("index", 0)
                    
                if idx not in tool_calls_accumulator:
                    tool_calls_accumulator[idx] = {
                        "id": None,
                        "type": "function",
                        "function": {"name": None, "arguments": ""}
                    }
                    arg_chunks[idx] = []
                    
                if tc.get("id") is not None:
                    tool_calls_accumulator[idx]["id"] = tc["id"]
                    
                if tc.get("type") is not None:
                    tool_calls_accumulator[idx]["type"] = tc["type"]
                    
                func = tc.get("function")
                if func and isinstance(func, dict):
                    if func.get("name") is not None:
                        tool_calls_accumulator[idx]["function"]["name"] = func["name"]
                        
                    args = func.get("arguments")
                    if isinstance(args, str) and args:
                        arg_chunks[idx].append(args)
        
        else :
            # yield si pas d'appel, cas normal !
            yield (TOKEN or COT_TOKEN), COT_TOKEN>"", [], False, None
        
    for idx in tool_calls_accumulator:
        if idx in arg_chunks and arg_chunks[idx]:
            joined_args = "".join(arg_chunks[idx])
                
            if joined_args:
                try:
                    parsed = json.loads(joined_args)
                    tool_calls_accumulator[idx]["function"]["arguments"] = json.dumps(parsed)
                except json.JSONDecodeError:
                    start = joined_args.rfind("{")
                    if start != -1:
                        try:
                            parsed = json.loads(joined_args[start:])
                            tool_calls_accumulator[idx]["function"]["arguments"] = json.dumps(parsed)
                        except json.JSONDecodeError:
                            tool_calls_accumulator[idx]["function"]["arguments"] = joined_args
                    else:
                        tool_calls_accumulator[idx]["function"]["arguments"] = joined_args

    if tool_calls_accumulator:
        tool_calls = [
            tool_calls_accumulator[i] 
            for i in sorted(tool_calls_accumulator.keys())
            if tool_calls_accumulator[i]["function"]["name"] is not None
        ]

    # Créateur du yield si appel de fonction
    if len(tool_calls)>0 :
        yield "", False, tool_calls, len(tool_calls)>0, None

@staticmethod
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

@staticmethod
def functions_to_tools(funcs: list[Callable]) -> list[dict[str, Any]]:
    return [utils.function_to_openai_tool(f) for f in funcs]

def add_meta(old_meta, meta_to_add):
    """
    {'prompt_tokens': 0, 'completion_tokens': 0, 'cached_tokens': 0}
    """
    for k in ("cached_tokens", "completion_tokens", "prompt_tokens"):
        old_meta[k] += meta_to_add[k]
    return old_meta

# ==============================
# Agents base
# ==============================

class agent_base :
    def __init__(self, yield_thinking:bool=False):

        self.request_profil:Request = None
        self.client:Client = None

        # Par défaut mais peut être modifié comme on veut !
        self._system_prompt = [create.system_prompt("")]
        self.persistent_history = []
        self.tools = []

        self.meta = {
            "yield_thinking":yield_thinking,
        }
    
    def create_stream(self, history):
        """
        # TO IMPLEMENT

        Like this :
        ```python
                return T.handle_streaming(
            self.request_profil,
            self.client,
            model="Your model",
            messages= self._system_prompt + history # Most important !
        )
        ```
        """
        raise NotImplementedError("Subclasses must implement create_stream()")

    def manage_user_prompt(self, prompt):
        """
        # TO IMPLEMENT if needed
        """

        return prompt

    def manage_assistant_response(self, response:dict):
        """
        # TO IMPLEMENT if needed
        """

        return response

    def manage_messages_in_reply(self, history=None):
        """
        Function to manage message history, executed at each step (after agent response or tool call)
        """
        return history

    def manage_messages_after_reply(self, history=None):
        """
        Message history management function, executed after each reply

        Ex:
        - Compress messages
        - Reduce to the last X
        - And more...

        ---

        Example to always store only the 2 lasts turns (without tools !) :
        ```python
        history = history[-4:]

        return history
        ```
        """
        return history

    def execute_tools(self, fname, args):
        raise NotImplementedError("Subclasses must implement execute_tools()")

    def manage_token_yield(self, token:str, is_thinking:bool=None, meta:dict=None, tool_calls:list=None):
        """
        # TO IMPLEMENT if needed for custom front !
        """
        return token
    
    def __call__(self, user_prompt:str, temporary_history=None):
        assert type(user_prompt) == dict, "user_prompt must be a dictionary !"
        
        if temporary_history : # Si on donne un historique temporaire on fait qu'une requête
            single_request = True
            history = temporary_history
        else : # Sinon on reste en persistant
            single_request = False
            history = self.persistent_history.copy()
        
        meta_toks = {'prompt_tokens': 0, 'completion_tokens': 0, 'cached_tokens': 0}
        
        run = True
        if user_prompt == "" :
            user_prompt = " "

        history.append(self.manage_user_prompt(user_prompt))
        
        while run :
            response = ""
            reasoning = ""

            for token, is_thinking, tool_calls, run, meta in self.create_stream(history):

                if meta :
                    for k in ("cached_tokens", "completion_tokens", "prompt_tokens"):
                        meta_toks[k] += meta[k]
                
                if is_thinking: # Si le modèle réfléchit
                    reasoning += token
                
                    if self.meta["yield_thinking"] and token : # Si on doit le retourner
                        yield self.manage_token_yield(token, True, meta_toks, tool_calls)
                
                else :
                    yield self.manage_token_yield(token, False, meta_toks, tool_calls)
                    response += token   
                


            if run : # Si on a des outils et donc qu'on doit continuer 

                yield self.manage_token_yield("\n", is_thinking, meta_toks, tool_calls)

                history.append(self.manage_assistant_response(
                    create.assistant_response(
                        content=response,
                        tool_calls=tool_calls,
                        reasoning_content=reasoning
                    )
                ))

                for tool_call in tool_calls :
                    fid, fname, args, _ = handle_tool_call(tool_call)

                    result = self.execute_tools(fname, args)

                    history.append(create.function_response(
                        id=fid, result=result, name=fname
                    ))
            
            history = self.manage_messages_in_reply(history)
        
        if not single_request : # Évite de perdre du temps pour rien s'il ne faut pas les stocker
            
            # Ne se fait QUE QUAND il n'y a plus d'outils !
            history.append(self.manage_assistant_response(
                create.assistant_response(
                    content=response,
                    reasoning_content=reasoning
                )
            ))

            history = self.manage_messages_after_reply(history)
        
            self.persistent_history = history