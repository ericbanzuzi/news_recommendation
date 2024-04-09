from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json
from bs4 import BeautifulSoup

class usCrawler(CrawlSpider):

    name = 'uscrawler'
    allowed_domains = ['eu.usatoday.com']  # allowed websites for the crawler
    start_urls = ['https://eu.usatoday.com/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow=(), unique=True), callback='parse_item', follow=True),  # parse_item handles all these links
    )

    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', id='content')
        content = ""
        if content_div:
            paragraphs = content_div.find_all('p')
            for paragraph in paragraphs:
                paragraph_text = paragraph.get_text(separator=" ", strip=False)
                print(paragraph_text)
                content += paragraph_text + " "
            scripts = response.xpath("//script[@type='application/ld+json']/text()").getall()
            for script in scripts:
                data = json.loads(script)
                if isinstance(data, dict) and '@type'in data.keys() and data['@type'] == 'NewsArticle':
                    if 'image' in data.keys():
                        image = data['image']['url']
                        output = {'url': response.url, 'content': content, 'image': image, 'date': data['dateModified'],
                                  'title': data['headline']}
                    else:
                        output = {'url': response.url, 'content': content, 'date': data['dateModified'],
                                  'title': data['headline']}

                    with open(f'../news_papers/US/{data["headline"]}.json', 'w') as file:
                        json.dump(output, file, indent=4)