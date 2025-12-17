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

    def create_stream(self, messages):
        """
        TO IMPLEMENT
        """

        return self.request(
            self.client,
            messages=messages,
            model=self.model
        )

    def create_fn(self):

            # Gradio chat function
            #   Gradio sends:  message, history
        def fn(message, history, *args):

            messages=[]

            for user, assistant in history :
                messages.append(T.create_user_prompt(user))
                messages.append(T.create_assistant_response(assistant))   
            messages.append(T.create_user_prompt(message))    
            

            stream = self.request(
                self.client,
                messages=self._system_prompt+messages,
                model=self.model
            )

            stream = self.create_stream(
                messages=messages
            )

            partial = ""
            is_thinking = False

            for token, _, _ in T.handle_streaming(stream):
                if token :

                    if "<think>" in token or is_thinking :
                        is_thinking = True

                        if "</think>" in token :
                            is_thinking = False

                    else : partial += token

                    yield partial
            return
        return fn