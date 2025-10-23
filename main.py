import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time
import requests
import datetime
from urllib.parse import urlparse
import pywhatkit
import webbrowser

webbrowser.open("https://www.youtube.com/feed/subscriptions")
print(pywhatkit.__file__)

instructions = """Write everything in Russian. When you get different news, separate them in the summary so that each starts on a new line with the symbol '—'. 
When greeting in the first item, add 👋 at the end. When stating the date in the second item, add ⌛ at the end. 
When mentioning the weather in the third item, add ☂️ at the end. 
When talking about prices in the fourth item, add 💸 at the end.
Divide the news into: 🗞️ Politics and World News, 📈 Finance & Crypto & Economy, 
💻 Tech and IT, 📊 Science and Education, ⚽ Sports.

After each news item, put the source in parentheses (if available).
"""

news_url = "https://www.bbc.com/russian"

current_time = datetime.datetime.now()

def get_weather(city):
    url = f'https://yandex.com/weather/en/{city}'
    
    response = requests.get(url)
    if response.status_code != 200:
        print("Error retrieving data!")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    temp = soup.find('p', class_='AppFactTemperature_wrap__z_f_O')
    if temp:
        temperature = temp.find('span', class_='AppFactTemperature_value__2qhsG').text
    else:
        temperature = "Temperature not found."

    feels_like = soup.find('span', class_='AppFact_feels__IJoel')
    if feels_like:
        feels_like_temp = feels_like.text
    else:
        feels_like_temp = "No 'feels like' temperature data."

    wind_speed = soup.find('li', class_='AppFact_details__item__QFIXI')
    if wind_speed:
        wind_speed_value = wind_speed.text
    else:
        wind_speed_value = "No wind speed data."

    humidity = soup.find_all('li', class_='AppFact_details__item__QFIXI')[2]
    if humidity:
        humidity_value = humidity.text
    else:
        humidity_value = "No humidity data."

    return {
        'temperature': temperature,
        'feels_like': feels_like_temp,
        'wind_speed': wind_speed_value,
        'humidity': humidity_value
    }

# Example usage
city = "moscow"
weather_info = get_weather(city)

url = "https://api.coingecko.com/api/v3/simple/price"
coins = ['bitcoin', 'solana', 'ethereum', 'binancecoin', 'litecoin', 'ripple']
params = {
    'ids': ','.join(coins),
    'vs_currencies': 'usd'
}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    crypto_res = "\n".join([f"{coin.capitalize()}: ${data[coin]['usd']}" for coin in coins])
else:
    crypto_res = "Error requesting crypto prices."

async def fetch_news(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    items = soup.select('ul[data-testid="topic-promos"] li')
                    news_list = []

                    for item in items:
                        link_tag = item.select_one('a.bbc-1i4ie53')
                        desc_tag = item.select_one('p')
                        time_tag = item.select_one('time')

                        if link_tag:
                            title = link_tag.text.strip()
                            link = link_tag['href'] if link_tag['href'].startswith("http") else "https://www.bbc.com" + link_tag['href']
                            description = desc_tag.text.strip() if desc_tag else ""
                            timestamp = time_tag.text.strip() if time_tag else ""

                            full_news = await fetch_full_news_text(session, link)
                            news_list.append({
                                "title": title,
                                "link": link,
                                "description": description,
                                "time": timestamp,
                                "full_text": full_news
                            })

                    return news_list if news_list else "No news found"
                else:
                    return f"Error loading page: {response.status}"
        except Exception as e:
            return f"Parsing error: {e}"

async def fetch_reuters_news():
    url = "https://www.reuters.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error loading Reuters: {response.status}"

                soup = BeautifulSoup(await response.text(), "html.parser")
                articles = soup.select("a[data-testid='Heading']")

                news_list = []
                for article in articles:
                    title = article.get_text(strip=True)
                    href = article.get('href')
                    if not title or not href:
                        continue

                    link = href if href.startswith("http") else f"https://www.reuters.com{href}"
                    full_text = await fetch_full_news_text(session, link)

                    news_list.append({
                        "title": title,
                        "link": link,
                        "description": "",
                        "time": "",
                        "full_text": full_text
                    })

                    if len(news_list) >= 10:
                        break

                return news_list or "No news found"
        except Exception as e:
            return f"Reuters parsing error: {e}"

async def fetch_cointelegraph_news():
    url = "https://cointelegraph.com"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Error loading Cointelegraph: {response.status}"
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                articles = soup.select('a[href^="/news/"]')
                news_list = []

                for article in articles:
                    title = article.get_text(strip=True)
                    href = article.get('href')
                    if not href or not title:
                        continue
                    link = f"https://cointelegraph.com{href}"

                    full_text = await fetch_full_news_text(session, link)

                    news_list.append({
                        "title": title,
                        "link": link,
                        "description": "",
                        "time": "",
                        "full_text": full_text
                    })

                    if len(news_list) >= 10:
                        break

                return news_list if news_list else "No news found"
        except Exception as e:
            return f"Cointelegraph parsing error: {e}"

async def fetch_full_news_text(session, link):
    try:
        async with session.get(link) as response:
            if response.status != 200:
                return "Error loading news text"

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            domain = urlparse(link).netloc

            if 'bbc.com' in domain:
                return extract_bbc_text(soup)
            elif 'cointelegraph.com' in domain:
                return extract_cointelegraph_text(soup)
            elif 'reuters.com' in domain:
                return extract_reuters_text(soup)
            else:
                return "Unknown source"
    except Exception as e:
        return f"Error parsing text: {e}"

async def generate_summary(news_items):
    api_url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    formatted_news = "\n\n".join(
        f"Title: {n['title']}\nTime: {n['time']}\nDescription: {n['description']}\nText: {n['full_text']}"
        for n in news_items
    )

    prompt_text = f"""Hi, without extra fluff, first:
1. Greet user named Yakov Abramov.
2. State current date (format DD.MM.YY and time HH:MM:SS): {current_time}
3. Provide weather info: {weather_info}.
4. Provide current cryptocurrency prices (in one line): {crypto_res}
5. Analyze all news below and generate a coherent summary with several sentences. Don't repeat each item, just summarize the key points in one block.

News:
{formatted_news}

Additional instructions: {instructions if instructions else "None"}
"""

    payload = {
        "model": "mistral",
        "prompt": prompt_text,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        try:
            start_time = time.time()
            async with session.post(api_url, json=payload, headers=headers) as response:
                print("Response time:", time.time() - start_time)

                if response.status == 200:
                    data = await response.json()
                    summary = data.get("response", "No summary received.")
                    return summary
                else:
                    return f"Text generation error: {response.status}"
        except Exception as e:
            return f"Request error: {e}"

async def periodic_news_check():
    while True:
        print("Starting new news check.")
        bbc_news = await fetch_news(news_url)
        reuters_news = await fetch_reuters_news()
        cointelegraph_news = await fetch_cointelegraph_news()

        all_news = []
        for news_source in [bbc_news, reuters_news, cointelegraph_news]:
            if isinstance(news_source, list):
                all_news.extend(news_source[:3])  # Take top 3 from each

        if all_news:
            summary = await generate_summary(all_news)
            if isinstance(summary, str):
                pywhatkit.sendwhatmsg_instantly("", summary)
                print(summary)
            else:
                print("Summary is not a string, message not sent.")
        else:
            print("Error: Could not fetch news.")

        print("Waiting 10 minutes...")
        await asyncio.sleep(600)

asyncio.run(periodic_news_check())
