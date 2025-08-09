from bs4 import BeautifulSoup

def extract_bbc_text(soup: BeautifulSoup) -> str:
    paragraphs = soup.select("main p")
    return "\n".join(p.get_text(strip=True) for p in paragraphs)

def extract_cointelegraph_text(soup: BeautifulSoup) -> str:
    paragraphs = soup.select("div.post-content p")
    return "\n".join(p.get_text(strip=True) for p in paragraphs)

def extract_reuters_text(soup: BeautifulSoup) -> str:
    paragraphs = soup.select("article p")
    return "\n".join(p.get_text(strip=True) for p in paragraphs)
