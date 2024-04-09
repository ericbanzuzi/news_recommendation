from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class WebCrawler(CrawlSpider):
    name = 'mycrawler'
    allowed_domains = ['toscrape.com']  # allowed websites for the crawler
    start_urls = ['http://books.toscrape.com/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow='catalogue/category')),
        Rule(LinkExtractor(allow='catalogue', deny='category'), callback='parse_item'),  # parse_item handles all these links
    )

    def parse_item(self, response):
        yield {
            'title': response.css('.product_main h1::text').get(),
            'price': response.css('.price_color::text').get(),
            'availability': response.css('.availability::text')[1].get().replace('\n', '').strip()
        }

