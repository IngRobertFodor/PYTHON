# SCRAPY


# Scrapy is a Python framework for large scale web scraping.
# It gives you all the tools you need to efficiently extract data from websites,
# process them as you want and store them in your preferred structure and format.


# STEP 1:
# Install Scrapy.

## pip install Scrapy


# STEP 2:
# Create a new Scrapy project.
# Test web page: https://pythonscraping.com/linkedin/ietf.html

## scrapy startproject ietf_scraper


# STEP 3:
# Move to the spiders directory and create new spider.

## cd ietf_scraper/ietf_scraper/spiders
## scrapy genspider pythonscraping pythonscraping.com


# STEP 4:
# Edit the spider file to extract the data.


# STEP 5:
# Run the spider.

## scrapy runspider pythonscraping.py