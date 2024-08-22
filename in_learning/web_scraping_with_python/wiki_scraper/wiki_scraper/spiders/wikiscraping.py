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
## scrapy runspider wikiscraping.py -o wikicrawler.xml -t xml -s CLOSESPIDER_ITEMCOUNT=10