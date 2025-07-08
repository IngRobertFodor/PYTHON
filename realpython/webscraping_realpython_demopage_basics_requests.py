import requests
from requests.auth import HTTPBasicAuth


url = "https://realpython.github.io/fake-jobs/"
web_page_html = requests.get(url)
print(web_page_html.status_code)
print(web_page_html.text[0:45])
print()


url_theinternet = "https://the-internet.herokuapp.com/"
web_page_html = requests.get(url_theinternet)
print(web_page_html.status_code)
print(web_page_html.text[0:45])
print()


web_page_html = requests.get("https://the-internet.herokuapp.com/basic_auth", auth=HTTPBasicAuth("admin", "admin"))
print(web_page_html.status_code)
print(web_page_html.text[0:5000])