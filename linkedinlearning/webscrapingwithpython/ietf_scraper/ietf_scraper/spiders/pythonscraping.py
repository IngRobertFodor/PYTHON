import scrapy # type: ignore


class PythonscrapingSpider(scrapy.Spider):
    name = "pythonscraping"
    allowed_domains = ["pythonscraping.com"]
    start_urls = ["https://pythonscraping.com/linkedin/ietf.html"]

    def parse(self, response):
        title = response.xpath("/html/body/div/pre/span[5]").get()
        title_text = response.xpath("/html/body/div/pre/span[5]/text()").get()
        author_text = response.xpath("/html/body/div/pre/span[1]/text()").get()
        date_text = response.xpath("/html/body/div/pre/span[4]/text()").get()
        longer_text = response.xpath("/html/body/div/pre/div/text()[3]").get()
        return {"title": title,
                "title_text": title_text,
                "author_text": author_text,
                "date_text": date_text,
                "longer_text": longer_text.strip()}