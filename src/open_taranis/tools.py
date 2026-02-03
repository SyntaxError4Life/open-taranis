from open_taranis import functions_to_tools

import requests
from bs4 import BeautifulSoup, Comment
import os
import re

def brave_research(web_request: str, count: int, country: str):
    try:
        api = os.environ['BRAVE_API']
    except KeyError:
        raise ValueError("Critical error: The BRAVE_API environment variable is missing.")

    params = {
        "q": web_request,
        "count": count,
        "country": country,
        "source": "web"
    }

    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api},
        params=params
    )

    # Explicitly check for HTTP errors before processing JSON
    response.raise_for_status()

    data = response.json()

    # Validate the expected structure before returning
    if not isinstance(data, dict):
        raise TypeError(f"Unexpected response type: {type(data).__name__}, expected dict.")
    
    if "web" not in data:
        # Check if the API returned an error structure instead
        if "error" in data:
            return f"API returned an error: {data['error']}"
        return "No results were found for this search."
    
    return data

def fast_scraping(url, timeout=10):
    """Quick scraping function, retrieves only the text from the given URL"""
    result = ""
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        # Gestion encodage
        if not response.encoding or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
        
        # Utilisation de response.text
        soup = BeautifulSoup(response.text, 'html.parser')

        # Nettoyage DOM
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'header', 'footer', 'nav', 'aside', 'form', 'svg']):
            tag.decompose()
            
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Extraction
        content_tag = soup.find('main') or soup.find('article') or soup.body
        if content_tag:
            text = content_tag.get_text(separator=' ', strip=True)
            text = re.sub(r'\s+', ' ', text).strip()
            result = text
        else:
            result = "Scraping failed: No content found."

    except requests.exceptions.Timeout:
        result = "Request failed: Timeout."
    except requests.exceptions.RequestException as e:
        msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
        result = f"Request failed: {msg}"
    except Exception as e:
        msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
        result = f"Scraping failed: {msg}"
    
    if not isinstance(result, str):
        result = str(result)
    
    return result.encode('utf-8', errors='ignore').decode('utf-8')
