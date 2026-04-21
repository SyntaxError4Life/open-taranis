import open_taranis as T

def create_fn_gradio(Agent:T.agent_base):

    assert Agent.manage_token_yield("test", True) == ("test", True), "agent_base.manage_token_yield need to return the token and if thinking !"
    
        # Gradio chat function
        #   Gradio sends:  message, history
    def fn(message, history, *args):

        messages = []
        for i in range(0, len(history), 2):
            user_text = history[i]['content'][0]['text']
            assistant_text = history[i + 1]['content'][0]['text']
            messages.extend([T.create.user_prompt(user_text), T.create.assistant_response(assistant_text)])
        
        partial = ""
        for token, is_thinking in Agent(
            user_prompt=T.create.user_prompt(message),
            temporary_history=messages
        ):
            
            if is_thinking :
                yield partial + "\nThinking...."
                continue
            
            if token : partial += token
            yield partial

        return
    return fn