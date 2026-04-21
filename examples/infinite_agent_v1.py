MODEL = "nvidia/nemotron-3-super-120b-a12b:free"

import open_taranis as T

CLIENT = T.Clients.openrouter
REQUEST = T.Request()
MAX_TOKENS = 16000

# Made with v0.2.4
if T.__version__ < "0.3.0":
    exit(f"Version v0.3.0 minimum required, you have v{T.__version__}")

# =========================================

class Infinite_Agent(T.agent_base):
    def __init__(self):
        super().__init__()

        self.system_prompt = """"You are a compressive memory AI agent. 
NEVER speak about your memory to the user (it is private to you)! 
Here is the current state of your memory: You must ALWAYS respond in the user's language."
"""
        self.memory = ""
        self.Cost = {'prompt_tokens': 0, 'completion_tokens': 0, 'cached_tokens': 0}

        self._system_prompt = [T.create.system_prompt(self.system_prompt)]
        self.turns = 1

    def create_stream(self, history):
         return T.handle_streaming(
            REQUEST,
            CLIENT,
            MODEL,
            messages=self._system_prompt + history
        )
    
    def manage_messages_after_reply(self, history):
        meta = {'prompt_tokens': 0, 'completion_tokens': 0, 'cached_tokens': 0}
        new_memory = ""
        
        if self.turns % 2 == 0 :

            print("\n\n---\nMemory being compressed\n---\n")
            messages=[
                T.create.assistant_response(f"""You are an AI information summarizer. 
You will receive the current memory and the current conversation; you must integrate the latter into the summary (by creating a new one). 
Maximize relevant information while keeping in mind that the summary must be extensible (e.g., noting missing information). 
In this new summary (serving as memory for the rest of the session), you must include ONLY that and nothing else in the USER language !
Take the time to think carefully ! 

Current memory (summary): 
{self.memory} 


And the current conversation:
""")] + history + [
                T.create.system_prompt("End of conversation!!"),
                T.create.user_prompt("Summarize the entire memory/conversation as requested.")
            ]


            is_thinking = False
            new_memory = ""
            for token, is_thinking, _, _, meta, in T.handle_streaming(
                REQUEST, CLIENT, MODEL,
                messages=messages
            ):

                if not is_thinking :
                    new_memory += token
            
            self.memory = new_memory
                       
            self._system_prompt = [T.create.system_prompt(
                self.system_prompt + self.memory
            )]


        history = history[-8:]
        self.turns += 1
        self.Cost = T.add_meta(self.Cost, meta)


        return history

    def manage_token_yield(self, token, is_thinking = None, meta = None, tool_calls = None):
        return token, meta

My_agent = Infinite_Agent()

while True :
    prompt = input("user : ")

    if prompt == "/exit":
        print("="*60)
        print(f"Total cost : {My_agent.Cost}")
        print("="*60)

        print(My_agent.memory)
        
        exit()

    print("\n\nagent : ", end="")

    for t, meta in My_agent(T.create.user_prompt(prompt)):
        print(t, end="", flush=True)
    
    My_agent.Cost = T.add_meta(My_agent.Cost, meta)
    
    print("\n\n","="*60,"\n")