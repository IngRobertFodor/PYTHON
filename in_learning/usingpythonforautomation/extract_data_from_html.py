import requests
from bs4 import BeautifulSoup


url = "https://market.feedbooks.com/"
html_content = requests.get(url).text
parsed_html = BeautifulSoup(html_content, "html.parser")
#print(parsed_html.prettify())

titles = parsed_html.find_all("a", class_="block__item-title")
titles_list = []
for title in titles:
    print(title.text.strip())
    titles_list.append(title.text.strip())
print()
print("These are book titles on web page:", titles_list)