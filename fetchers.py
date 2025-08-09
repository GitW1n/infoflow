import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from parsers import extract_bbc_text, extract_cointelegraph_text, extract_reuters_text

async def fetch_full_news_text(session, link):
    async with session.get(link) as response:
        if response.status != 200:
            return None
        soup = BeautifulSoup(await response.text(), 'html.parser')
        domain = urlparse(link).netloc

        if 'bbc.com' in domain:
            return extract_bbc_text(soup)
        elif 'cointelegraph.com' in domain:
            return extract_cointelegraph_text(soup)
        elif 'reuters.com' in domain:
            return extract_reuters_text(soup)
        return None

async def fetch_news(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return []
            soup = BeautifulSoup(await response.text(), 'html.parser')
            items = soup.select('ul[data-testid="topic-promos"] li')
            news_list = []
            for item in items:
                link_tag = item.select_one('a.bbc-1i4ie53')
                if not link_tag:
                    continue
                link = link_tag['href'] if link_tag['href'].startswith("http") else "https://www.bbc.com" + link_tag['href']
                full_news = await fetch_full_news_text(session, link)
                news_list.append({"title": link_tag.text.strip(), "link": link, "full_text": full_news})
            return news_list

async def fetch_reuters_news():
    url = "https://www.reuters.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                return []
            soup = BeautifulSoup(await response.text(), "html.parser")
            articles = soup.select("a[data-testid='Heading']")
            news_list = []
            for article in articles[:10]:
                link = article.get('href')
                if not link:
                    continue
                link = link if link.startswith("http") else f"https://www.reuters.com{link}"
                full_news = await fetch_full_news_text(session, link)
                news_list.append({"title": article.get_text(strip=True), "link": link, "full_text": full_news})
            return news_list

async def fetch_cointelegraph_news():
    url = "https://cointelegraph.com"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return []
            soup = BeautifulSoup(await response.text(), 'html.parser')
            articles = soup.select('a[href^="/news/"]')
            news_list = []
            for article in articles[:10]:
                link = f"https://cointelegraph.com{article.get('href')}"
                full_news = await fetch_full_news_text(session, link)
                news_list.append({"title": article.get_text(strip=True), "link": link, "full_text": full_news})
            return news_list
