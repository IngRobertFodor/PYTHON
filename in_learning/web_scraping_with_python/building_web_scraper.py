# SCRAPY


# Scrapy is a Python framework for large scale web scraping.
# It gives you all the tools you need to efficiently extract data from websites,
# process them as you want and store them in your preferred structure and format.

# STEP 1:
# Install Scrapy.
## pip install Scrapy

# STEP 2:
# Create a new Scrapy project.
# Test web page: https://pythonscraping.com/linkedin/ietf.html      (Other example: https://en.wikipedia.org.)
## scrapy startproject ietf_scraper     (Other example: scrapy startproject wiki_scraper.)

# STEP 3:
# Move to the spiders directory and create new spider.
## cd ietf_scraper/ietf_scraper/spiders     (Other example: cd wiki_scraper/wiki_scraper/spiders.)
## scrapy genspider pythonscraping pythonscraping.com       (Other example: scrapy genspider wikiscraping en.wikipedia.org.)

# STEP 4:
# Edit the spider file to extract the data.

# STEP 5:
# Run the spider.
## scrapy runspider pythonscraping.py       (Other example: scrapy runspider wikiscraping.py.)