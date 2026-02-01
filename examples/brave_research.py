import open_taranis as T
from open_taranis.tools import brave_research, fast_scraping

client = T.clients.openrouter(api_key=None)
request = T.clients.openrouter_request

messages = [
    T.create_system_prompt("""You are an autonomous AI web search agent.
For example, you can search for URLs in Brave and scrape them to obtain all their content.

Don't hesitate to conduct in-depth searches, such as navigating from site to site using the URLs you find there, and so on. 
Make as many function calls as needed for the tasks the user assigns you. 
You must execute them flawlessly and never cheat; complete your mission successfully!"""),
    T.create_user_prompt(input("Request : "))
]

run = True

while run :
    respond=""
    
    for token, tool_calls, run in T.handle_streaming(request(
        client=client,messages=messages,model="nvidia/nemotron-3-nano-30b-a3b:free",
        tools=T.functions_to_tools([brave_research,fast_scraping])
    )):
        if token :
            print(token, end="")
            respond+=token

    if run :
        messages.append(T.create_assistant_response(respond, tool_calls))

        for tool_call in tool_calls :
            fid, fname, args, _ = T.handle_tool_call(tool_call)
            tool_response=""

            if fname == "brave_research":

                print(f"\nSearch on Brave : {args["web_request"]} \n")

                results=brave_research(
                    web_request=args["web_request"],
                    count=5,
                    country="fr"
                )

                for item in results["web"]["results"]:
                    tool_response+= f"{item['title']} : {item['url']}\n"
            
            if fname == "fast_scraping":

                print(f"\nScraping {args["url"]}\n")
                tool_response=fast_scraping(url=args["url"])

                
            messages.append(T.create_function_response(
                id=fid,result=tool_response,name=fname
            ))
        
    if not run :
        messages.append(T.create_assistant_response(respond))