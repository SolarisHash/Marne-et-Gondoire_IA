import scrapy

class TestSpider(scrapy.Spider):
    name = "test_spider"
    start_urls = ["https://httpbin.org/html"]

    def parse(self, response):
        title = response.css("h1::text").get()
        yield {"title": title}
