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
all_jobs = list(soup.find_all("span", class_="listing-company-name"))
print(all_jobs[:5])
#print()

print("--First 5 Job Names--")
job_names_list = []
for job in all_jobs[0:5]:
    job_title = job.find("a").get_text()
    print(job_title)