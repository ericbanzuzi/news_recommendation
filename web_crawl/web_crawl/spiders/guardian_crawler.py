import sys

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json


class GuardianCrawler(CrawlSpider):
    count = 0
    name = 'guardiancrawler'
    allowed_domains = ['theguardian.com']  # allowed websites for the crawler
    start_urls = ['https://www.theguardian.com/europe']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow='https://www.theguardian.com/', deny=('jobs', 'profile', 'syndication'), unique=True), callback='parse_item', follow=True),  # pase_item handles all these links
    )

    def parse_item(self, response):
        article_content = response.xpath("//div[contains(@class, 'article-body-commercial')]")
        if article_content:
            script = response.xpath("//script[@type='application/ld+json']/text()").get().strip()
            text = response.xpath("//div[contains(@class, 'article-body-commercial')]//p//text()").getall()

            full_content = ''
            for paragraph in text:
                full_content += paragraph + ' '

            data = json.loads(script)[0]
            if 'image' in data.keys():
                image = data['image'][0]
                output = {'url': response.url, 'content': full_content.strip(), 'image': image, 'date': data['datePublished'],
                          'title': data['headline'].strip()}
            else:
                output = {'url': response.url, 'content': full_content.strip(), 'date': data['datePublished'],
                          'title': data['headline'].strip()}

            with open(f'../news_papers/guardian/{data["headline"]}.json', 'w') as file:
                json.dump(output, file, indent=4)
                self.count += 1
                if self.count == 50000:
                    sys.exit()

