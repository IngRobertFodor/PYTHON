# !!! RUN THIS FIRST (CMD)
# pip install beautifulsoup4
# This shows all installed packages
# pip list


import requests
from bs4 import BeautifulSoup


# This script scrapes a "demopage" from Real Python.
url = "https://realpython.github.io/fake-jobs/"
web_page_html = requests.get(url)

# Parse the HTML content using BeautifulSoup.
soup = BeautifulSoup(web_page_html.content, "html.parser")

all_jobs_container = soup.find(id="ResultsContainer")
all_jobs_list = list(all_jobs_container.find_all("div", class_="card-content"))
all_jobs_list_details = []
for job in all_jobs_list:
    # This finds the job title.
    job_name = job.find("h2", class_ = "title is-5")
    all_jobs_list_details.append(job_name.text.strip())
    # This finds the job link.
    job_link = job.find_all("a")
    #print(job_link)
    #print(job_link[1])
    job_link_relevant = job_link[1].get("href")
    #print(job_link_relevant)
    all_jobs_list_details.append(job_link_relevant)  
#print()

print(all_jobs_list_details[:4])
print()

# This finds all jobs and prints the text of each job title, job location and link.
print("---")
for job in all_jobs_list:
    job_name = job.find("h2", class_="title is-5")
    job_location = job.find("p", class_="location")
    job_link = job.find_all("a")
    job_link_relevant = job_link[1].get("href")
    print(job_name.text.strip())
    print(job_location.text.strip())
    print(job_link_relevant)
    print("---")