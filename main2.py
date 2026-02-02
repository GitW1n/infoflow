import aiohttp
import asyncio
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

class Weather:
    def __init__(self, city: str):
        self.city = city

    def get_weather(self):
        url = f'https://yandex.com/weather/en/{self.city}'
        response = requests.get(url)
        if response.status_code != 200:
            print("Error retrieving data!")
            return {}

        soup = BeautifulSoup(response.text, 'html.parser')

        def safe_select(selector, default="N/A"):
            tag = soup.select_one(selector)
            return tag.text.strip() if tag else default

        return {
            'temperature': safe_select('span.AppFactTemperature_value__2qhsG'),
            'feels_like': safe_select('span.AppFact_feels__IJoel'),
            'wind_speed': safe_select('li.AppFact_details__item__QFIXI'),
            'humidity': safe_select('li.AppFact_details__item__QFIXI:nth-of-type(3)')
        }


class Crypto:
    def __init__(self, coins=None):
        self.coins = coins or ['bitcoin', 'solana', 'ethereum', 'binancecoin', 'litecoin', 'ripple']

    def get_prices(self):
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(self.coins),
            'vs_currencies': 'usd'
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {coin: data[coin]['usd'] for coin in self.coins}
        except Exception as e:
            print("Error requesting crypto prices:", e)
            return {}


async def fetch_news_from_source(session, url, article_selector, limit=10):
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Error loading {url}: {response.status}")
                return []

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.select(article_selector)
            news_list = []

            for article in articles[:limit]:
                title = article.get_text(strip=True)
                link = article.get('href')
                if not title or not link:
                    continue
                full_link = urljoin(url, link)
                news_list.append({'title': title, 'link': full_link})

            return news_list

    except Exception as e:
        print(f"Error fetching {url}:", e)
        return []


async def main():
    # Пример использования
    weather = Weather("moscow")
    crypto = Crypto()

    print("Weather:", weather.get_weather())
    print("Crypto:", crypto.get_prices())

    async with aiohttp.ClientSession() as session:
        tech_news = await fetch_news_from_source(session, "https://cointelegraph.com", "a[href^='/news/']", limit=5)
        print("Cointelegraph news:")
        for item in tech_news:
            print("-", item['title'], item['link'])


if __name__ == "__main__":
    asyncio.run(main())
