import scrapy
from urllib.parse import urljoin
from scrapy_scrapingbee import ScrapingBeeSpider, ScrapingBeeRequest


class AmazonReviewsSpider(ScrapingBeeSpider):
    name = "amazon_reviews"

    def start_requests(self):
        asin_list = ['B08HN1VVS1', 'B0BRQS862W', 'B0CJB92WJ4', 'B0CN312XV4',
                     'B0BVQSWJCL', 'B0C3GFZSXT', 'B09C5MJYTG', 'B0CMWNS8LQ', 'B0B3F5QSQY']
        for asin in asin_list:
            amazon_reviews_url = f'https://www.amazon.com/product-reviews/{asin}/'
            yield ScrapingBeeRequest(url=amazon_reviews_url,
                                     params={
                                         'render_js': False,
                                         'premium_proxy': True,
                                     },
                                     callback=self.parse_reviews,
                                     meta={'asin': asin, 'retry_count': 0})

    def parse_reviews(self, response):
        asin = response.meta['asin']
        retry_count = response.meta['retry_count']

        # Get Next Page Url
        next_page_relative_url = response.css(".a-pagination .a-last>a::attr(href)").get()
        if next_page_relative_url is not None:
            retry_count = 0
            next_page = urljoin('https://www.amazon.com/', next_page_relative_url)
            yield ScrapingBeeRequest(url=next_page,
                                     params={
                                         'render_js': False,
                                         'premium_proxy': True,
                                     },
                                     callback=self.parse_reviews,
                                     meta={'asin': asin, 'retry_count': retry_count})

        # Adding this retry_count here to bypass any amazon js rendered review pages
        elif retry_count < 3:
            retry_count = retry_count + 1
            yield ScrapingBeeRequest(url=response.url,
                                     params={
                                         'render_js': False,
                                         'premium_proxy': True,
                                     },
                                     callback=self.parse_reviews, dont_filter=True,
                                     meta={'asin': asin, 'retry_count': retry_count})

        # Parse Product Reviews
        review_elements = response.css("#cm_cr-review_list div.review")
        for review_element in review_elements:
            yield {
                "asin": asin,
                "text": "".join(review_element.css("span[data-hook=review-body] ::text").getall()).strip(),
                "title": review_element.css("*[data-hook=review-title]>span::text").get(),
                "location_and_date": review_element.css("span[data-hook=review-date] ::text").get(),
                "verified": bool(review_element.css("span[data-hook=avp-badge] ::text").get()),
                "rating": review_element.css("*[data-hook*=review-star-rating] ::text").re(r"(\d+\.*\d*) out")[0],
            }

