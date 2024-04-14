import sys

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json
from bs4 import BeautifulSoup


class BBCCrawler(CrawlSpider):
    count = 0
    name = 'bbccrawler'
    allowed_domains = ['bbc.com']  # allowed websites for the crawler
    start_urls = ['https://www.bbc.com/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow='https://www.bbc.com/', deny=('sound', 'cymrufyw', 'sport'), unique=True), callback='parse_item', follow=True),
    )

    def extract_text(self, blocks):
        text = ''
        for block in blocks:
            if block['type'] == 'paragraph':
                text += block['model']['text'] + ' '
        return text.strip()

    def parse_item(self, response):
        script = response.xpath("//script[@type='application/ld+json']/text()").get()
        if script:

            data_info = json.loads(script)

            data_script = response.xpath("//script[@type='application/json']/text()").get()
            data = json.loads(data_script)
            if 'article' in data_info['@type'].lower():
                url_endpoint = response.url.split('/')[-1]

                # Extract the text content
                text_content = ''
                try:
                    for content in data['props']['pageProps']['page'][f'@\"news\",\"{url_endpoint}\",']['contents']:
                        if content['type'] == 'text':
                            text_content += self.extract_text(content['model']['blocks'])
                except:
                    for content in data['props']['pageProps']['page'][list(data['props']['pageProps']['page'].keys())[0]]['contents']:
                        if content['type'] == 'text':
                            text_content += self.extract_text(content['model']['blocks'])

                if 'image' in data.keys():
                    try:
                        image = data_info['image']['url']
                    except:
                        image = data_info['image'][0]
                    output = {'url': response.url, 'content': text_content, 'image': image, 'date': data_info['datePublished'],
                              'title': data_info['headline']}
                else:
                    output = {'url': response.url, 'content': text_content, 'date': data_info['datePublished'],
                              'title': data_info['headline']}

                with open(f'../news_papers/BBC/{data["headline"]}.json', 'w') as file:
                    json.dump(output, file, indent=4)
                    self.count += 1
                    if self.count == 50000:
                        sys.exit()

