import requests

def get_crypto_prices():
    url = "https://api.coingecko.com/api/v3/simple/price"
    coins = ['bitcoin', 'solana', 'ethereum', 'binancecoin', 'litecoin', 'ripple']
    params = {'ids': ','.join(coins), 'vs_currencies': 'usd'}

    response = requests.get(url, params=params)
    
