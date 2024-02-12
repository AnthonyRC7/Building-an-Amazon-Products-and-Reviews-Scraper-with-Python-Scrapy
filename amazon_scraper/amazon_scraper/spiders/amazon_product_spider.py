# import json
import scrapy
# from urllib.parse import urljoin
import re
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest


# To get a specific number of pages*************************************************
class AmazonSearchProductSpider(ScrapingBeeSpider):
    name = "amazon_product_spider"

    def start_requests(self):
        keyword_list = ['ipad']
        for keyword in keyword_list:
            for page_num in range(1, 7):
                amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'

                yield ScrapingBeeRequest(
                    url=amazon_search_url,
                    params={
                        'render_js': False,
                        'premium_proxy': False,
                    },
                    callback=self.discover_product_urls,
                )

    def discover_product_urls(self, response):

        # Discover Product URLs
        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        for product in search_products:
            relative_url = product.css("h2>a::attr(href)").get().split("?")[0]
            product_url = f'https://www.amazon.com{relative_url}'

            yield ScrapingBeeRequest(
                url=product_url,
                params={
                    'render_js': False,
                    'premium_proxy': False,
                },
                callback=self.parse_product_data,
            )

    def parse_product_data(self, response):
        # image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        # image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?])},\n", response.text)[0])
        variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        name = response.css("#productTitle::text").get("").strip()
        price = response.css('.a-price span[aria-hidden="true"] ::text').get("").strip()
        stars = response.css("i[data-hook=average-star-rating] ::text").get("").strip()
        rating_count = response.css("div[data-hook=total-review-count] ::text").get("").strip()
        feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]

        if not price:
            price = response.css('.a-price .a-offscreen::text').get("").strip()
        yield {
            "name": name,
            "price": price,
            "stars": stars,
            "rating_count": rating_count,
            "feature_bullets": feature_bullets,
            # "images": image_data,
            "variant_data": variant_data,
        }

# To get all products from all the pages*******************************************************
# class AmazonSearchProductSpider(scrapy.Spider):
#     name = "amazon_search_product"
#
#     def start_requests(self):
#         keyword_list = ['ipad']
#         for keyword in keyword_list:
#             amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page=1'
#             yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls,
#                                  meta={'keyword': keyword, 'page': 1})
#
#     def discover_product_urls(self, response):
#         page = response.meta['page']
#         keyword = response.meta['keyword']
#
#         # Discover Product URLs
#         search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
#         for product in search_products:
#             relative_url = product.css("h2>a::attr(href)").get()
#             product_url = urljoin('https://www.amazon.com/', relative_url).split("?")[0]
#             yield scrapy.Request(url=product_url, callback=self.parse_product_data,
#                                  meta={'keyword': keyword, 'page': page})
#
#         # Get All Pages
#         if page == 1:
#             available_pages = response.xpath(
#                 '//*[contains(@class, "s-pagination-item")][not(has-class("s-pagination-separator"))]/text()'
#             ).getall()
#
#             last_page = available_pages[-1]
#             for page_num in range(2, int(last_page)):
#                 amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
#                 yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls,
#                                      meta={'keyword': keyword, 'page': page_num})
#
#     def parse_product_data(self, response):
#         # image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
#         image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?])},\n", response.text)[0])
#         variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
#         name = response.css("#productTitle::text").get("").strip()
#         price = response.css('.a-price span[aria-hidden="true"] ::text').get("").strip()
#         stars = response.css("i[data-hook=average-star-rating] ::text").get("").strip()
#         rating_count = response.css("div[data-hook=total-review-count] ::text").get("").strip()
#         feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]
#
#         if not price:
#             price = response.css('.a-price .a-offscreen::text').get("").strip()
#         yield {
#             "name": name,
#             "price": price,
#             "stars": stars,
#             "rating_count": rating_count,
#             "feature_bullets": feature_bullets,
#             "images": image_data,
#             "variant_data": variant_data,
#         }

