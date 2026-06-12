from open_taranis import functions_to_tools

import requests
from bs4 import BeautifulSoup, Comment
import os
import re
import time
 
def brave_research(web_request: str, count: int, country: str):
    """
    - country : "US', "FR"...
    - count recommended : 5 (max 8)
    """
    
    try:
        api = os.environ['BRAVE_API']
    except KeyError:
        raise ValueError("Critical error: The BRAVE_API environment variable is missing.")

    if count > 8:
        count = 8

    params = {
        "q": web_request,
        "count": count,
        "country": country,
        "source": "web"
    }

    try:
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": api},
            params=params
        )
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise TypeError(f"Unexpected response type: {type(data).__name__}, expected dict.")

        if "web" not in data:
            if "error" in data:
                return f"API returned an error: {data['error']}"
            return "No results were found for this search."

        return data

    except requests.exceptions.HTTPError as e:
        # Check specifically for 429 Too Many Requests
        if e.response is not None and e.response.status_code == 429:
            return "Too many requests have been made at the same time"
        # For other HTTP errors, we re-raise them as they might be critical
        raise

def fast_scraping(url, timeout=10):
    """Quick scraping function, retrieves only the text from the given URL"""
    result = ""
    max_display = 100

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        if not response.encoding or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup(['script', 'style', 'noscript', 'iframe', 'header', 'footer', 'nav', 'aside', 'form', 'svg']):
            tag.decompose()

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

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
        msg = str(e)[:max_display] + "..." if len(str(e)) > max_display else str(e)
        result = f"Request failed: {msg}"
    except Exception as e:
        msg = str(e)[:max_display] + "..." if len(str(e)) > max_display else str(e)
        result = f"Scraping failed: {msg}"

    if not isinstance(result, str):
        result = str(result)

    return result.encode('utf-8', errors='ignore').decode('utf-8')
