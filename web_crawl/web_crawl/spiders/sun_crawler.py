from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json
from bs4 import BeautifulSoup
import sys


class SunCrawler(CrawlSpider):
    count = 0
    name = 'suncrawler'
    allowed_domains = ['thesun.co.uk']  # allowed websites for the crawler
    start_urls = ['https://www.thesun.co.uk/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow='thesun.co.uk/\S+/\d{8}/\S+', unique=True), callback='parse_item', follow=True),  # pase_item handles all these links
    )

    def parse_item(self, response):
        article_content = response.xpath("//div[contains(@class, 'article__content')]")
        if article_content:
            script = response.xpath("//script[@type='application/ld+json']/text()").get().strip()
            text = response.xpath("//div[contains(@class, 'article__content')]//p//text()").getall()

            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', id='article__content')

            full_content = ''
            for paragraph in text:
                full_content += paragraph + ' '  # skip <p> and </p>

            data = json.loads(script)
            if 'image' in data.keys():
                image = data['image'][0]['url']
                output = {'url': response.url, 'content': full_content.strip(), 'image': image, 'date': data['datePublished'],
                          'title': data['headline'].strip()}
            else:
                output = {'url': response.url, 'content': full_content.strip(), 'date': data['datePublished'],
                          'title': data['headline'].strip()}

            with open(f'../news_papers/sun/{data["headline"]}.json', 'w') as file:
                json.dump(output, file, indent=4)
                self.count += 1
                if self.count == 50000:
                    sys.exit()
