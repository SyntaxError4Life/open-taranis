MODEL = "arcee-ai/trinity-large-preview:free"

import open_taranis as T

CLIENT = T.clients.openrouter()
REQUEST = T.clients.openrouter_request
MAX_TOKENS = 16000

# Made with v0.2.4
if T.__version__ < "0.2.4":
    exit(f"Version v0.2.4 minimum required, you have v{T.__version__}")

# =========================================

class Infinite_Agent(T.agent_base):
    def __init__(self):
        super().__init__(is_thinking_enabled = True)

        self.system_prompt = """"You are a compressive memory AI agent. 
NEVER speak about your memory to the user (it is private to you)! 
Here is the current state of your memory: You must ALWAYS respond in the user's language."
"""
        self.memory = ""

        self._system_prompt = [T.create_system_prompt(self.system_prompt)]
        self.turns = 1

    def create_stream(self):
        return REQUEST(
            client=CLIENT,
            messages=self._system_prompt + self.messages,
            model=MODEL
        )
    
    def manage_messages_after_reply(self):
        
        

        if self.turns % 2 == 0 :

            print("\n\n---\nMemory being compressed\n---\n")
            stream = REQUEST(CLIENT,
                messages=[
                    T.create_assistant_response(f"""You are an AI information summarizer. 
You will receive the current memory and the current conversation; you must integrate the latter into the summary (by creating a new one). 
Maximize relevant information while keeping in mind that the summary must be extensible (e.g., noting missing information). 
In this new summary (serving as memory for the rest of the session), you must include ONLY that and nothing else in the USER language !
Take the time to think carefully ! 

Current memory (summary): 
{self.memory} 


And the current conversation:
""")] + self.messages + [
                    T.create_system_prompt("End of conversation!!"),
                    T.create_user_prompt("Summarize the entire memory/conversation as requested.")],
                model=MODEL,
                temperature=0.2,
                max_tokens=MAX_TOKENS
            )

            is_thinking = False
            new_memory = ""
            for token, _, _ in T.handle_streaming(stream):
                is_thinking, norm_tok, cot_tok = T.handle_thinking(token, is_thinking)

                if norm_tok :
                    new_memory += norm_tok
                       
            self.memory = T.remove_thinks(new_memory)
            self._system_prompt = [T.create_system_prompt(
                self.system_prompt + self.memory
            )]

        self.messages = self.messages[-8:]
        self.turns += 1

My_agent = Infinite_Agent()

while True :
    prompt = input("user : ")

    if prompt == "/exit":
        print("="*60)

        print(My_agent.memory)
        
        exit()

    print("\n\nagent : ", end="")

    for t in My_agent(prompt):
        print(t, end="", flush=True)
    
    print("\n\n","="*60,"\n")