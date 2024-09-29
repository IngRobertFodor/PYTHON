import requests
from bs4 import BeautifulSoup


url = "https://market.feedbooks.com/"

html_content = requests.get(url).text
#print(html_content)

parsed_html = BeautifulSoup(html_content, "html.parser")
#print(parsed_html)
print(parsed_html.prettify())