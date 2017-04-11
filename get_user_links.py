from bs4 import BeautifulSoup
import json


file = 'answer_wiki.html'
soup = BeautifulSoup(open(file), 'html.parser')
user_links = soup.find_all('a')
to_be_saved = []
for user in user_links:
    to_be_saved.append(user['href'])

with open('user_links.json', 'w') as f:
    json.dump(to_be_saved, f, indent=4)
