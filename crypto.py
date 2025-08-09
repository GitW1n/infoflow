import requests

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    coins = ['bitcoin', 'solana', 'ethereum', 'binancecoin', 'litecoin', 'ripple']
    params = {'ids': ','.join(coins), 'vs_currencies': 'usd'}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return "\n".join([f"{coin.capitalize()}: ${data[coin]['usd']}" for coin in coins])
    return "Error requesting crypto prices."
