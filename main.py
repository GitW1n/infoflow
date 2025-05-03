import aiohttp
import asyncio
from bs4 import BeautifulSoup
import time
import requests
import datetime
from urllib.parse import urlparse
import pywhatkit
print(pywhatkit.__file__)

requirements = """Описывайте всё на русском языке. Когда вы получаете разные новости то в резюме разделяйте их, 
так чтобы каждая начиналась с новой строки и со знака '—'. 
Когда приветствуйте в конце первого пункта ставьте знак 👋, когда говорите дату в конце второго пункта ставьте знак ⌛, 
когда говорите о погоде в конце третьего пункта ставьте знак ☂️,
когда говорите о ценах в конце четвёртого пункта ставьте  знак 💸.
Новости разделяйте на: 🗞️ Политика и мировые новости, 📈 Финансы&криптовалюты&экономика, 
💻Технологии и IT, 📊 Наука и образование, ⚽ Спорт

После каждой новости в скобках указывай источник(если есть информация)
"""
news_url = "https://www.bbc.com/russian"

current_time = datetime.datetime.now()

def get_weather(city):
    url = f'https://yandex.com/weather/en/{city}'
    
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Ошибка при получении данных!")
        return
    
    
    soup = BeautifulSoup(response.text, 'html.parser')

    
    temp = soup.find('p', class_='AppFactTemperature_wrap__z_f_O')
    if temp:
        temperature = temp.find('span', class_='AppFactTemperature_value__2qhsG').text
    else:
        temperature = "Не удалось найти температуру."

    # Извлекаем описание погоды (чувствуется как)
    feels_like = soup.find('span', class_='AppFact_feels__IJoel')
    if feels_like:
        feels_like_temp = feels_like.text
    else:
        feels_like_temp = "Нет данных о температуре ощущаемой."

    # Извлекаем скорость ветра
    wind_speed = soup.find('li', class_='AppFact_details__item__QFIXI')
    if wind_speed:
        wind_speed_value = wind_speed.text
    else:
        wind_speed_value = "Нет данных о скорости ветра."

    # Извлекаем влажность
    humidity = soup.find_all('li', class_='AppFact_details__item__QFIXI')[2]  # Для влажности нужно взять третий элемент
    if humidity:
        humidity_value = humidity.text
    else:
        humidity_value = "Нет данных о влажности."

    return {
        'temperature': temperature,
        'feels_like': feels_like_temp,
        'wind_speed': wind_speed_value,
        'humidity': humidity_value
    }

# Пример использования

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
    crypto_res = "\n".join([f"{coin.capitalize()}: ${data[coin]['usd']}" for coin in coins]) #результат сбора цен
else:
    crypto_res = "Ошибка при запросе данных."

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
                                "full_text": full_news  # Добавляем полный текст новости
                            })

                    return news_list if news_list else "Новости не найдены"
                else:
                    return f"Ошибка при загрузке страницы: {response.status}"
        except Exception as e:
            return f"Ошибка при парсинге: {e}"

async def fetch_reuters_news():
    url = "https://www.reuters.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Ошибка при загрузке Reuters: {response.status}"

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

                return news_list or "Новости не найдены"
        except Exception as e:
            return f"Ошибка при парсинге Reuters: {e}"

reuters = fetch_reuters_news()


async def fetch_cointelegraph_news():
    url = "https://cointelegraph.com"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    return f"Ошибка при загрузке Cointelegraph: {response.status}"
                
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

                return news_list if news_list else "Новости не найдены"
        except Exception as e:
            return f"Ошибка при парсинге Cointelegraph: {e}"



async def fetch_full_news_text(session, link):
    try:
        async with session.get(link) as response:
            if response.status != 200:
                return "Ошибка при загрузке текста новости"

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
                return "Неизвестный источник"
    except Exception as e:
        return f"Ошибка при парсинге текста: {e}"

async def generate_summary(news_items):
    api_url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    formatted_news = "\n\n".join(
        f"Заголовок: {n['title']}\nВремя: {n['time']}\nОписание: {n['description']}\nТекст: {n['full_text']}"
        for n in news_items
    )


    prompt_text = f"""Привет, без лишнего в своем сообщении сначала:
1. Поприветствуй пользователя с именем Яков Абрамов.
2. Укажи текущую дату(только в формате DD.MM.YY  и время HH:MM:SS):{current_time}
3. Предоставь информацию о погоде: {weather_info}.
4. Предоставь текущие цены на криптовалюты(в одну строчку):{crypto_res}
5. Проанализируй все новости ниже и сделай связное, логичное резюме, состоящее из нескольких предложений. Не повторяй пункты заново для каждой новости, просто сделай обзор ключевых моментов в одном блоке.

Новости:
{formatted_news}

Доп. указания: {requirements if requirements else "Нет"}
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
                    summary = data.get("response", "Резюме не получено.")
                    return summary
                else:
                    return f"Ошибка генерации текста: {response.status}"
        except Exception as e:
            return f"Ошибка при запросе: {e}"

async def periodic_news_check():
    while True:
        print("Начало новой проверки новостей.")
        bbc_news = await fetch_news(news_url)
        reuters_news = await fetch_reuters_news()
        cointelegraph_news = await fetch_cointelegraph_news()

        # Объединение новостей
        all_news = []
        for news_source in [bbc_news, reuters_news, cointelegraph_news]:
            if isinstance(news_source, list):
                all_news.extend(news_source[:3])  # Берем по 3 новости из каждого источника

        if all_news:
            summary = await generate_summary(all_news)
            if isinstance(summary, str):
                pywhatkit.sendwhatmsg_instantly("+79037530394", summary)
                print(summary)
            else:
                print("Резюме не является строкой, сообщение не отправлено.")
        else:
            print("Ошибка: Не удалось извлечь новости.")

        print("Ожидание 10 минут(а)...")
        await asyncio.sleep(600)





asyncio.run(periodic_news_check())
