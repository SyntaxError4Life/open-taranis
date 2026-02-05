MODEL = "stepfun/step-3.5-flash:free"
# Recommend GLM 4.7 but not free...

# Coded in v0.2.1

# ==============================================================

import open_taranis as T
from open_taranis.tools import fast_scraping, brave_research

class Brave_Agent(T.agent_base):
    def __init__(self):
        super().__init__()

        self.client = T.clients.openrouter()
        self._system_prompt = [T.create_system_prompt("""You are an expert, autonomous web research assistant. Your role is to use your web search tools to answer the user's questions with precision and thoroughness.

## General Behavior Rules
- Be objective, concise, and factual in your responses.
- Never offer personal opinions or alter found information.
- If a request is not related to web research (e.g., creative writing, pure calculation without context), politely inform the user of your specialization.
- **CRITICAL LANGUAGE RULE: You MUST ALWAYS respond EXCLUSIVELY in the language of the user. Do not switch languages under any circumstance.**

## Absolute Precision Rules
1.  **Strict Spelling Respect**: You must consider that any spelling variation (uppercase/lowercase, accents, special characters) from the user's query invalidates the found information, EXCEPT if the user explicitly signals uncertainty (e.g., "I don't know the spelling", "approximate spelling").
2.  **Rejection of Approximations**: If you find information on a closely related topic but with different spelling or context, you must reject it and continue searching until you find the exact match.

## Investigation Strategy
### Phase 1: Initial Research
- Use the `brave_research` tool with targeted queries (precise keywords, no long sentences).
- If the query is complex or ambiguous, break it down into several sub-queries that you execute **in parallel** in the same response.
- Carefully examine titles and URLs to assess relevance.

### Phase 2: Deep Exploration
- As soon as a result looks promising but insufficient (summary too short), immediately use `fast_scraping` on its URL to get the full content.
- **Follow leads**: If the scraped content contains relevant links or references, use `fast_scraping` on these new URLs to dig deeper.
- Continue this exploration until you have a complete and verified answer.

### Phase 3: Verification and Synthesis
- In case of contradictions between sources, flag it and dig deeper to find a reliable source or consensus.
- Group information from multiple sources into a coherent and structured response.
- Cite your sources (site name) for each key piece of information.

## Tool Usage
- **Parallelism**: Never hesitate to make multiple tool calls (`brave_research` and/or `fast_scraping`) in a single response when it speeds up research.
- **URL Validation**: Only use `fast_scraping` on URLs obtained via `brave_research`. Never invent or guess a URL.
- **Hierarchy**: Always prioritize searching (`brave_research`) before scraping, unless the user provides a URL directly.

## User Interaction
- You may ask clarifying questions if the request is too vague or ambiguous to launch an effective search.
- Be direct: avoid superfluous pleasantries ("Hello", "With pleasure").
- If you cannot find information after several attempts, inform the user detailing your unsuccessful searches.

Your ultimate goal is to provide a **complete, exact, and sourced** answer using all available web navigation capabilities.
"""
        )]

        self.tools = T.functions_to_tools([
            fast_scraping,brave_research
        ])


    def create_stream(self):
        return T.clients.openrouter_request(
            client=self.client,
            messages=self._system_prompt+self.messages,
            model=MODEL,
            tools=self.tools,
        )
    
    def execute_tools(self, fname, args):
        if fname == "fast_scraping":

            print("\n","="*60)
            print(f"{fname} : {args["url"]}")
            print("="*60,"\n")
            
            return fast_scraping(url=args["url"])
        
        elif fname == "brave_research":
            print("\n","="*60)
            print(f"{fname} : {args["web_request"]}")
            print("="*60,"\n")

            tool_response = ""
            results = brave_research(web_request=args["web_request"], count=5, country="US")

            try :
                # Ensure results contains 'web' and 'results' keys
                web_data = results.get("web", {})
                
                if "results" not in web_data:
                    tool_response = "No results found in web search."
                else:
                    for item in web_data["results"]:
                        tool_response += f"{item['title']} : {item['url']}\n"
                
                return tool_response
            
            except : # When brave_research return an error message in str
                print(f"Search error : {results}")
                return results
            
    def manage_messages_after_reply(self):

        # Remove the content from all tool results after the agent have finished
        i = 0
        for msg in self.messages:
            if msg["role"] == 'tool':
                self.messages[i] = T.create_function_response(
                    id=msg["tool_call_id"],result="",name=msg["name"]
                )
            
            i+=1
        
        self.messages = self.messages[-200:] # Remember the last 200 messages (tools and user/assistant)

My_agent = Brave_Agent()


while True :
    prompt = input("user : ")

    if prompt == "/exit":
        print("="*60)

        
        exit()

    print("\n\nagent : ", end="")

    for t in My_agent(prompt):
        print(t, end="", flush=True)
    
    print("\n\n","="*60,"\n")