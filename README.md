# infoflow

InfoFlow is an asynchronous Python-based news and data aggregation bot that fetches news, weather information, and cryptocurrency prices, summarizes the content using a local AI model, and sends the result via WhatsApp using `pywhatkit`.

## Features

- Fetches news from multiple sources:
  - BBC
  - Reuters
  - Cointelegraph
- Scrapes weather data for a specific city
- Retrieves live cryptocurrency prices from the CoinGecko API
- Uses a local LLM to generate a summary
- Sends the result to WhatsApp using `pywhatkit`
- Formats summary according to strict structure and style rules

## Tech Stack

- Python 3
- aiohttp
- requests
- beautifulsoup4
- pywhatkit
- Local LLM API
- CoinGecko API for crypto prices
- Weather scraping

