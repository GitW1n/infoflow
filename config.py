import datetime

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
