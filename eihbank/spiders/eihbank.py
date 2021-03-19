import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from eihbank.items import Article


class EihbankSpider(scrapy.Spider):
    name = 'eihbank'
    start_urls = ['http://www.eihbank.de/en/news-archive/']

    def parse(self, response):
        links = response.xpath('//a[@class="sc-button "]/@href').getall()
        links = [link for link in links if link[-1] != '#']
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('(//h1)[last()]//text()').getall()
        title = [text for text in title if text.strip()]
        if len(title) > 1:
            date = title[1].strip()
        else:
            date = ''
        title = title[0]

        content = response.xpath('//div[@class="wpb_column vc_column_container vc_col-sm-9"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()
        if not content:
            return

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
