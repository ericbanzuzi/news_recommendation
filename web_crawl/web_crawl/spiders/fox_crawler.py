from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import json


class FOXCrawler(CrawlSpider):

    name = 'foxcrawler'
    allowed_domains = ['foxnews.com']  # allowed websites for the crawler
    start_urls = ['https://www.foxnews.com/']  # base link

    # use scrapy shell url to test stuff interactively
    rules = (
        Rule(LinkExtractor(allow=(r'^https://www\.foxnews\.com/',), unique=True), callback='parse_item', follow=True),  # pase_item handles all these links
    )

    def parse_item(self, response):
        #article_content = response.xpath("//div[contains(@class, 'article__content-container')]")
        article_content=True
        if article_content:
            scripts = response.xpath("//script[@type='application/ld+json']/text()").getall()
            for script in scripts:
                data = json.loads(script)
                if data['@type'] == 'NewsArticle':
                    if 'image' in data.keys():
                        image = data['image']['url']
                        output = {'url': response.url, 'content': data['articleBody'], 'image': image, 'date': data['dateModified'],
                                'title': data['headline']}
                    else:
                        output = {'url': response.url, 'content': data['articleBody'], 'date': data['dateModified'],
                                'title': data['headline']}

                    with open(f'../news_papers/FOX/{data["headline"]}.json', 'w') as file:
                        json.dump(output, file, indent=4)