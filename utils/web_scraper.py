# utils/web_scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

FAQ_KEYWORDS = ["faq", "faqs", "frequently-asked-questions"]

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def is_faq_page(url):
    lower_url = url.lower()
    return any(keyword in lower_url for keyword in FAQ_KEYWORDS)

def get_all_faq_links(url, domain):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag.attrs['href']
            full_url = urljoin(url, href)
            if is_valid(full_url) and domain in full_url and is_faq_page(full_url):
                links.add(full_url)

        return links
    except:
        return set()

def extract_visible_text(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        for script_or_style in soup(["script", "style", "noscript"]):
            script_or_style.decompose()

        visible_text = soup.get_text(separator=" ", strip=True)
        return visible_text
    except:
        return ""

def scrape_website(base_url, max_pages=3):
    visited = set()
    to_visit = set()
    domain = urlparse(base_url).netloc

    # If base_url is already a FAQ page, include it
    if is_faq_page(base_url):
        to_visit.add(base_url)
    else:
        # Crawl base URL to find FAQ links
        to_visit = get_all_faq_links(base_url, domain)

    collected_texts = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue

        print(f"Scraping FAQ: {url}")
        visited.add(url)

        page_text = extract_visible_text(url)
        if page_text:
            collected_texts.append(page_text)

    return "\n".join(collected_texts)
