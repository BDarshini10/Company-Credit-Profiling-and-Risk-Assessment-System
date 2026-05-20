import requests
from bs4 import BeautifulSoup

def scrape_company(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        p = soup.find("p")
        if p:
            return p.get_text(strip=True)[:800]
        return "Company overview manually assessed."

    except:
        return "Website scraping failed. Manual overview used."