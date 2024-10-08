# CRAWLSPIDER


import scrapy # type: ignore
from scrapy.spiders import CrawlSpider, Rule # type: ignore
from scrapy.linkextractors import LinkExtractor # type: ignore
# CRAWLSPIDER
from wiki_scraper.items import WikiScraperItem # type: ignore


class WikiscrapingSpider(CrawlSpider):
    name = "wikiscraping"
    allowed_domains = ["en.wikipedia.org"]
    start_urls = ["https://en.wikipedia.org/wiki/Kevin_Bacon"]

    rules = [Rule(LinkExtractor(allow=r'wiki/((?!:).)*$'), callback="parse_info", follow=True)]
    
    def parse_info(self, response):
        
        wikicrawler = WikiScraperItem()

        wikicrawler['title'] = response.xpath("//h1/i/text()").get() 
        wikicrawler['url'] = response.url                               
        
        return wikicrawler


# CRAWLSPIDER

# We can run this spider using the following command in the terminal.
## scrapy runspider wikiscraping.py -o wikicrawler.xml -t xml -s CLOSESPIDER_ITEMCOUNT=10

# But we can do the same thing using our settings.py file and adding these lines.
## CLOSESPIDER_ITEMCOUNT=10
## FEED_URI='wikicrawler.xml'
## FEED_FORMAT='xml'