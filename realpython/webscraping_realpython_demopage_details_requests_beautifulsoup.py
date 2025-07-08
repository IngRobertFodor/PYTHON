# !!! RUN THIS FIRST (CMD)
# pip install beautifulsoup4
# This shows all installed packages
# pip list


import requests
from bs4 import BeautifulSoup


# This script scrapes a "demopage" from Real Python.
url = "https://realpython.github.io/fake-jobs/"
web_page_html = requests.get(url)
print(web_page_html.status_code)
print(web_page_html.text[0:45])
print()

# Parse the HTML content using BeautifulSoup.
soup = BeautifulSoup(web_page_html.content, "html.parser")
print(soup.prettify()[0:45])
print()

# The search result, part of HTML with all jobs.
all_jobs = soup.find(id="ResultsContainer")
print(all_jobs.prettify()[0:450])
print()

# Create list of all job titles in the search result.
### "class_" has underscore at the end.
all_jobs_list = list(all_jobs.find_all("h2", class_="title is-5"))
print(all_jobs_list)
print()

# Print the text of each job title.
for job in all_jobs_list:
    print(job.text.strip())
print()

# Find all "python" related jobs and print the text of each job title.
search_text = "python"
for job in all_jobs_list:
    if search_text in job.text.lower():
        print(job.text.strip())
print()

# This can look up other job relevant information, like the link to the job.
### "class_" has underscore at the end.
job_links_list = list(all_jobs.find_all("footer", class_="card-footer"))
relevant_job_links_list = []
for job_link in job_links_list:
    jlink = list(job_link.find_all("a"))
    relevant_jlink = jlink[1].get("href")
    print(relevant_jlink)
    relevant_job_links_list.append(relevant_jlink)
print()
print(relevant_job_links_list)
print()

# Find all "Senior" related jobs and print 1) the text of each job title and 2) link to the job.
next_search_text = "senior"
for job in all_jobs_list:
    if next_search_text in job.text.lower():
        print(job.text.strip())
    else:
        continue
for link in relevant_job_links_list:
    if next_search_text in link.lower():
        print(link)
    else:
        continue
print()