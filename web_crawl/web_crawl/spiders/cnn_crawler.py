import sys

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json


class CNNCrawler(CrawlSpider):
    count = 0
    name = 'cnncrawler'
    allowed_domains = ['cnn.com']  # allowed websites for the crawler
    start_urls = ['https://edition.cnn.com/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow='index.html$', deny='arabic', unique=True), callback='parse_item', follow=True),  # pase_item handles all these links
    )

    def parse_item(self, response):
        article_content = response.xpath("//div[contains(@class, 'article__content-container')]")
        if article_content:
            script = response.xpath("//script[@type='application/ld+json']/text()").get()
            data = json.loads(script)
            if 'image' in data.keys():
                image = data['image'][0]['contentUrl']
                output = {'url': response.url, 'content': data['articleBody'], 'image': image, 'date': data['dateModified'],
                          'title': data['headline']}
            else:
                output = {'url': response.url, 'content': data['articleBody'], 'date': data['dateModified'],
                          'title': data['headline']}

            with open(f'../news_papers/CNN/{data["headline"]}.json', 'w') as file:
                json.dump(output, file, indent=4)
                self.count += 1
                if self.count == 50000:
                    sys.exit()

