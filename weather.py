import requests
from bs4 import BeautifulSoup

def parse_weather(html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')
    temp_tag = soup.find('p', class_='AppFactTemperature_wrap__z_f_O')
    temperature = temp_tag.find('span', class_='AppFactTemperature_value__2qhsG').text if temp_tag else None

    feels_like_tag = soup.find('span', class_='AppFact_feels__IJoel')
    feels_like = feels_like_tag.text if feels_like_tag else None

    wind_tag = soup.find('li', class_='AppFact_details__item__QFIXI')
    wind_speed = wind_tag.text if wind_tag else None

    humidity_tags = soup.find_all('li', class_='AppFact_details__item__QFIXI')
    humidity = humidity_tags[2].text if len(humidity_tags) >= 3 else None

    return {
        'temperature': temperature,
        'feels_like': feels_like,
        'wind_speed': wind_speed,
        'humidity': humidity
    }

def get_weather(city: str):
    url = f'https://yandex.com/weather/en/{city}'
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return parse_weather(response.text)
