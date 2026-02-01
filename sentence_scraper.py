# sentence_scraper.py

import requests
from bs4 import BeautifulSoup
import urllib.parse
import html
import random
import time

class CaptchaError(Exception):
    """Raised when Satzapp blocks access with a captcha."""
    pass

def get_example_sentences(term, max_sentences=5):
    """
    Fetches example sentences for a given term from Satzapp.
    Returns a formatted HTML string with German sentences and English translations.
    """
    # URL encode the term and use tl=en for English translations
    encoded_term = urllib.parse.quote_plus(term)
    url = f"https://www.satzapp.com/saetze/?w={encoded_term}&tl=en"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.satzapp.com/saetze/"
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random delay before request to mimic human behavior (0.5s to 2s)
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(url, headers=headers, timeout=12)
            
            if response.status_code == 429 or "Maximale Anzahl an Zugriffen" in response.text or "captcha" in response.text.lower():
                # Rate limited or Captcha triggered
                print(f"⚠️ Rate limited/Captcha detected by Satzapp for '{term}'.")
                raise CaptchaError("Satzapp requested a captcha. Please solve it in your browser.")

            response.raise_for_status()
            break # Success!
            
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"⚠️ Connection error for '{term}' (Attempt {attempt+1}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed to fetch examples for '{term}' after {max_retries} attempts: {e}")
                return ""
        except Exception as e:
            print(f"❌ Unexpected error fetching Satzapp for '{term}': {e}")
            return ""

    # Check if we actually got a successful response
    if not 'response' in locals() or not response or not response.text:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    
    # Looking for German sentence paragraphs
    german_ps = [p for p in soup.find_all("p") if p.find("span", class_="sTxt")]
    
    for p in german_ps[:max_sentences]:
        span = p.find("span", class_="sTxt")
        if not span:
            continue
            
        german_text = "".join([m.get_text() for m in span.find_all("mark")])
        german_text = german_text.replace('\u00A0', ' ').replace('\xa0', ' ').strip()
        
        # Find translation in the next p tag
        translation = ""
        next_p = p.find_next_sibling("p")
        if next_p:
            if ("rLinks" in next_p.get("class", []) or next_p.find("img", alt="English")):
                translation = next_p.get_text().strip()
                translation = " ".join(translation.split())

        if german_text:
            results.append((german_text, translation))

    if not results:
        return ""

    # Format for Anki (HTML)
    html_output = "<ul>"
    for german, english in results:
        if english:
            html_output += f"<li><b>{german}</b><br><small>{english}</small></li>"
        else:
            html_output += f"<li><b>{german}</b></li>"
    html_output += "</ul>"
    
    # Add attribution as per CC BY-SA 4.0 requirements
    attribution = '<div style="text-align: right; margin-top: 10px; font-size: 0.5em; color: #999;">'
    attribution += f'<a href="{url}" style="color: #999; text-decoration: none;">Example sentences: Netzverb (SatzApp)</a>'
    attribution += '</div>'
    
    html_output += attribution
    
    return html_output

if __name__ == "__main__":
    # Test
    term = "guten"
    print(f"Fetching examples for '{term}'...")
    examples = get_example_sentences(term)
    print("\nFormatted HTML:")
    print(examples)
