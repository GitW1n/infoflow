import asyncio
import pywhatkit
from config import news_url, current_time, instructions
from weather import get_weather
from crypto import get_crypto_prices
from fetchers import fetch_news, fetch_reuters_news, fetch_cointelegraph_news
from summarizer import generate_summary

async def periodic_news_check():
    city = "moscow"
    weather_info = get_weather(city)
    crypto_res = get_crypto_prices()

    while True:
        print("Starting new news check.")
        bbc_news = await fetch_news(news_url)
        reuters_news = await fetch_reuters_news()
        cointelegraph_news = await fetch_cointelegraph_news()

        all_news = (bbc_news[:3] if bbc_news else []) + \
                   (reuters_news[:3] if reuters_news else []) + \
                   (cointelegraph_news[:3] if cointelegraph_news else [])

        if all_news:
            summary = await generate_summary(all_news, current_time, weather_info, crypto_res, instructions)
            if summary:
                pywhatkit.sendwhatmsg_instantly("+79037530394", summary)
                print(summary)
            else:
                print("Summary is empty.")
        else:
            print("No news fetched.")

        print("Waiting 10 minutes...")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(periodic_news_check())
