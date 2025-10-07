import open_taranis as T
print("program launched\n\n")

# User database - contains only Jean Dupont's information
user_database = {
    "jean dupont": {
        "age": 45,
        "position": "Director Marketing",
        "company": "TechCorp",
        "city": "Paris"
    },
    "marie dubois": {
        "age": 32,
        "position": "Software Engineer",
        "company": "TechCorp",
        "city": "Lyon"
    },
    "pierre martin": {
        "age": 29,
        "position": "Data Analyst",
        "company": "DataVision",
        "city": "Marseille"
    },
    "sophie leroy": {
        "age": 38,
        "position": "HR Manager",
        "company": "PeopleFirst",
        "city": "Toulouse"
    },
    "luc bertrand": {
        "age": 50,
        "position": "Chief Financial Officer",
        "company": "FinSecure",
        "city": "Bordeaux"
    },
    "emma moreau": {
        "age": 27,
        "position": "Product Designer",
        "company": "InnovateX",
        "city": "Nantes"
    }
}

# Tool definition - describes the get_user_info function available to the model
tools = [{
    "type": "function",
    "function": {
        "name": "get_user_info",
        "description": "Access the employee database",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name of the employee to look up"}
            },
            "required": ["name"]
        }
    }
}]

# Function implementation - retrieves user data from our database
def get_user_info(name):
    """Fetch user information from the database by name (case-insensitive)"""
    return user_database.get(name.strip().lower(), "User not found in database")

client = T.clients.openrouter("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")
prompt = """Give me the information you have access to on the following users :
- jean dupont
- marie dubois
- pierre martin
- sophie leroy
- luc bertrand
- emma moreau
"""

messages = [
    T.create_system_prompt("api_key"),
    T.create_user_prompt(prompt)
]

stream = T.clients.openrouter_request(
    client=client,
    messages=messages,
    model="qwen/qwen3-4b:free",
    tools=tools  
)

final_response = ""
print("assistant : ",end="")
for token, tool_calls, _ in T.handle_streaming(stream) : 
    if token :
        print(token, end="")
        final_response += token

print("\n")
print(tool_calls)
print("Number of calls : ",len(tool_calls))
print("="*50,"\n")

messages.append(T.create_assistant_response(final_response, tool_calls))

for tool_call in tool_calls :
    id, name, argument, _ = T.handle_tool_call(tool_call)
    print(id, argument,)
    messages.append(T.create_function_response(
        id, get_user_info(argument["name"]), name
    ))

print("\n","="*50,"\n")

stream = T.clients.openrouter_request(
    client=client,
    messages=messages,
    model="qwen/qwen3-4b:free"
)

final_response = ""
print("assistant final : ",end="")
for token, tool_calls, _ in T.handle_streaming(stream) : 
    if token :
        print(token, end="")
        final_response += token
print()
messages.append(T.create_assistant_response(final_response))

print("\n","="*50,"\n")

for m in messages :
    print(m)