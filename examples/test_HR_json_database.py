import open_taranis as T

# Made by Grok 4

model = "qwen/qwen3-4b:free"
client = T.clients.openrouter("API_KEY")
request = T.clients.openrouter_request

print(f"Program launched with {model}\n\n")

# User database
user_database = {
    "jean dupont": {"age": 45, "position": "Director Marketing", "company": "TechCorp", "city": "Paris"},
    "marie dubois": {"age": 32, "position": "Software Engineer", "company": "TechCorp", "city": "Lyon"},
    "pierre martin": {"age": 29, "position": "Data Analyst", "company": "DataVision", "city": "Marseille"},
    "sophie leroy": {"age": 38, "position": "HR Manager", "company": "PeopleFirst", "city": "Toulouse"},
    "luc bertrand": {"age": 50, "position": "Chief Financial Officer", "company": "FinSecure", "city": "Bordeaux"},
    "emma moreau": {"age": 27, "position": "Product Designer", "company": "InnovateX", "city": "Nantes"}
}

# List of users for system prompt
user_list = ", ".join(user_database.keys())

# Tool definition with optional field
tools = [{
    "type": "function",
    "function": {
        "name": "get_user_info",
        "description": "Access employee database. Fetch specific field(s) if needed.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name of the employee (case-insensitive)"},
                "field": {"type": "string", "description": "Optional: Comma-separated fields to fetch (age, position, company, city). If omitted, return all."}
            },
            "required": ["name"]
        }
    }
}]

# Function implementation
def get_user_info(name, field=None):
    name = name.strip().lower()
    user = user_database.get(name, "User not found")
    if user == "User not found":
        return user
    if field:
        fields = [f.strip() for f in field.split(",")]
        return {f: user.get(f, "Field not found") for f in fields}
    return user

client = T.clients.openrouter(API_KEY)

# System prompt with user list
system_prompt = f"You are a HR assistant who MUST use the get_user_info tool before answering questions about users. Available users: {user_list}."

messages = [T.create_system_prompt(system_prompt)]

# Automatic questions
questions = [
    "Who is the youngest employee and in which city do they live?",
    "List all employees at TechCorp with their positions.",
    "What is the average age of all employees? (Calculate it step by step)"
]

for i, question in enumerate(questions, 1):
    print(f"Question {i}: {question}\n")
    messages.append(T.create_user_prompt(question))
    
    # First pass: Get tool calls
    stream = T.clients.openrouter_request(client=client, messages=messages, model="qwen/qwen3-4b:free", tools=tools)
    first_response = ""
    tool_calls = []
    print("Assistant thinking (first pass): ", end="")
    for token, tools_out, has_tools in T.handle_streaming(stream):
        if token:
            print(token, end="")
            first_response += token
        if has_tools:
            tool_calls = tools_out
    print("\n")
    
    # Print tool calls explicitly
    if tool_calls:
        print("Tool Calls Generated:")
        for tc in tool_calls:
            print(tc)
        print(f"Number of calls: {len(tool_calls)}\n")
    else:
        print("No tool calls generated.\n")
    
    messages.append(T.create_assistant_response(first_response, tool_calls))
    
    # Execute tools and append responses
    for tool_call in tool_calls:
        fid, fname, args, err = T.handle_tool_call(tool_call)
        if err:
            print(f"Error in tool call: {err}")
            continue
        print(f"Executing {fname} with args: {args}")
        field = args.get("field")
        result = get_user_info(args["name"], field)
        messages.append(T.create_function_response(fid, result, fname))
    
    print("=" * 50 + "\n")
    
    # Second pass: Final response
    stream = T.clients.openrouter_request(client=client, messages=messages, model="qwen/qwen3-4b:free")
    final_response = ""
    print("Assistant final response: ", end="")
    for token, _, _ in T.handle_streaming(stream):
        if token:
            print(token, end="")
            final_response += token
    print("\n")
    messages.append(T.create_assistant_response(final_response))
    
    print("=" * 50 + "\n")

# Final messages for debug
print("Final conversation history:")
for m in messages:
    print(m)
print("\nProgram ended.")