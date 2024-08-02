import requests
from bs4 import BeautifulSoup


url = "https://market.feedbooks.com/"
html_content = requests.get(url).text
parsed_html = BeautifulSoup(html_content, "html.parser")
#print(parsed_html.prettify())

bookauthors = parsed_html.find_all("a", class_="block__item-author")
bookauthors_list = []
for author in bookauthors:
    print(author.text.strip())
    bookauthors_list.append(author.text.strip())
print()
print("These are bookauthors on web page:", bookauthors_list)