import aiohttp
import time

async def generate_summary(news_items, current_time, weather_info, crypto_res, instructions):
    api_url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}

    formatted_news = "\n\n".join(
        f"Title: {n['title']}\nText: {n['full_text']}"
        for n in news_items
    )

    prompt_text = f"""Hi, without extra fluff, first:
1. Greet user named Yakov Abramov.
2. State current date (format DD.MM.YY and time HH:MM:SS): {current_time}
3. Provide weather info: {weather_info}.
4. Provide current cryptocurrency prices (in one line): {crypto_res}
5. Analyze all news below and generate a coherent summary.

News:
{formatted_news}

Additional instructions: {instructions if instructions else "None"}
"""

    payload = {"model": "mistral", "prompt": prompt_text, "stream": False}

    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        async with session.post(api_url, json=payload, headers=headers) as response:
            print("Response time:", time.time() - start_time)
            if response.status == 200:
                data = await response.json()
                return data.get("response", "")
            return None
