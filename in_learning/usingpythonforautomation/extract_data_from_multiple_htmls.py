import requests
from bs4 import BeautifulSoup
from time import sleep


'''
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
'''


for page_number in range(2, 5):
    url_martinus_klasics_allpages = "https://www.martinus.sk/l?categories%5B0%5D=6100&clasmods%5B0%5D=308346&page="+str(page_number)
    html_content_martinus = requests.get(url_martinus_klasics_allpages).text
    parsed_html_martinus = BeautifulSoup(html_content_martinus, "html.parser")
    #print(parsed_html_martinus.prettify())
    booktitles_martinus = parsed_html_martinus.find_all("span", class_="link link--product")
    #print(booktitles_martinus)
    print("Page:", page_number)
    for book_title in booktitles_martinus:
        print(book_title.text.strip())
    print()
    sleep(1)