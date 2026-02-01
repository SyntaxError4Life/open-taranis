from open_taranis import functions_to_tools

import requests
from bs4 import BeautifulSoup
import os

def brave_research(web_request:str, count:int, country:str):

    try:
        api = os.environ['BRAVE_API']
    except KeyError:
        raise ValueError("Critical error: The BRAVE_API environment variable is missing..")
    
    return requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api},
        params={
            "q": web_request,
            "count": count,
            "country": country,
            "source": "web"
        }
    ).json()

def fast_scraping(url):
    """Quick scraping function, retrieves only the text from the given URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(strip=True)
        return text
    except requests.exceptions.RequestException as e:
        # Network errors, timeouts, etc.
        msg = str(e)[:100] + "..." if len(str(e)) > 50 else str(e)
        return f"Request failed: {msg}"
    except Exception as e:
        # Parser errors or unexpected issues
        msg = str(e)[:100] + "..." if len(str(e)) > 50 else str(e)
        return f"Scraping failed: {msg}"