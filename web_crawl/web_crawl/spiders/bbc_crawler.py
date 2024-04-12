from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json
from bs4 import BeautifulSoup


class BBCCrawler(CrawlSpider):

    name = 'bbccrawler'
    allowed_domains = ['bbc.com']  # allowed websites for the crawler
    start_urls = ['https://www.bbc.com/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow='https://www.bbc.com/', deny='sound', unique=True), callback='parse_item', follow=True),  # pase_item handles all these links
    )

    def parse_item(self, response):
        script = response.xpath("//script[@type='application/ld+json']/text()").get()
        if script:
            data = json.loads(script)
            if 'article' in data['@type'].lower():
                soup = BeautifulSoup(response.text, 'html.parser')
                content = soup.find_all('p')

                full_content = ''
                for paragraph in content:
                    paragraph_text = paragraph.get_text(separator=" ", strip=True)
                    full_content += paragraph_text + " "

                if 'image' in data.keys():
                    try:
                        image = data['image']['url']
                    except:
                        image = data['image'][0]
                    output = {'url': response.url, 'content': full_content, 'image': image, 'date': data['datePublished'],
                              'title': data['headline']}
                else:
                    output = {'url': response.url, 'content': full_content, 'date': data['datePublished'],
                              'title': data['headline']}
                print(output)


        #     with open(f'../news_papers/CNN/{data["headline"]}.json', 'w') as file:
        #         json.dump(output, file, indent=4)





