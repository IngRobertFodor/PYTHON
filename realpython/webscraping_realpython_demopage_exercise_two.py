# !!! RUN THIS FIRST (CMD)
# pip install beautifulsoup4
# This shows all installed packages
# pip list


import requests
from bs4 import BeautifulSoup


web_url = "https://www.python.org/jobs/"

web_html = requests.get(web_url)

soup = BeautifulSoup(web_html.content, "html.parser")
#print(soup.prettify()[:1000])

# Find all job listings
all_jobs = list(soup.find_all("h2", class_="listing-company"))
#print(all_jobs[:5])
#print()

print("--Job Names--")
job_names_list = []
for job in all_jobs:
    job_title = job.find("span", class_="listing-company-name")
    job_title.find("a").get("href")
    job_title_text = job_title.get_text()
    job_title_text = job_title_text.replace("\n", "").replace("New", "")
    job_names_list.append(job_title_text)
#print(job_names_list)
for job in job_names_list:
    job_list = list(job.split("    "))
    print(job_list[0])