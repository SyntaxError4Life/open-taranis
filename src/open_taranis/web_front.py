import gradio as gr
import open_taranis as T

class chat_fn_gradio:
    def __init__(self, 
                 client:T.openai.OpenAI,
                 request:T.openai.Stream,
                 model:str,
                 _system_prompt:str=""
                ):
        
        self.client:T.openai.OpenAI = client
        self.request:T.openai.Stream = request
        self.model = model
        self._system_prompt = [{"role":"system", "content":_system_prompt}]

        self.meta = {
            "defaut_create_stream_used":False
        }
        self.memory = []

    def create_stream(self, messages):
        """
        TO IMPLEMENT

        ```
        if self.meta["defaut_create_stream_used"]==False : # Just used to detect, must be rewritten by the user
            print("Classic create_stream method used !")
            self.meta=True

        return self.request(self.client,messages=messages,model=self.model)
        ```

        """
        if self.meta["defaut_create_stream_used"]==False : # Just used to detect, must be rewritten by the user
            print("Classic create_stream method used !")
            self.meta=True

        return self.request(self.client,messages=messages,model=self.model)

    def create_fn(self):

            # Gradio chat function
            #   Gradio sends:  message, history
        def fn(message, history, *args):
            
            # Here we use our own internal memory rather than that of the gradio :
            self.memory.append(T.create_user_prompt(message))

            stream = self.create_stream(
                self._system_prompt+self.memory # We make the system prompt adaptable and never at the beginning of the memory
            )

            partial = ""
            token_nb = 0
            for token, _, _ in T.handle_streaming(stream):
                if token :
                    partial += token
                    token_nb += 1

                    yield f"""Tokens : {token_nb}
Model : {self.model}

---

{partial}"""
            self.memory.append(T.create_assistant_response(partial))
            print(partial)
            return
        return fn