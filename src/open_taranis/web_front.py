import open_taranis as T

def create_fn_gradio(Agent):

        # Gradio chat function
        #   Gradio sends:  message, history
    def fn(message, history, *args): 

        partial = ""
        for token, is_thinking in Agent(message): 
            if is_thinking :
                yield partial + "\nThinking...."
                continue
            
            if token : partial += token
            yield partial

        return
    return fn