import scrapy


class DnsUltrabookSpider(scrapy.Spider):
    page = 1
    last_page = None
    name = 'dns_ultrabook'
    allowed_domains = ['dns-shop.ru']
    start_urls = ['https://www.dns-shop.ru/catalog/17a892f816404e77/?f[65c]=264d&p=1']

    # Save scraping info
    custom_settings = {'FEED_URI': "dns_%(time)s.csv",
                       'FEED_FORMAT': 'csv'}

    def parse(self, response):
        # Give data of css
        product_name = response.css('.product-info__title-link > a::text').extract()
        # Example: technical parameters
        # [1366x768, SVA (TN+film), Intel Pentium 4417U, 2 х 2.3 ГГц, RAM 4 ГБ,
        #  SSD 128 ГБ, Intel HD 610 , Wi-Fi, Windows 10 Home]
        product_info = response.css('.product-info__title-description::text').extract()
        product_url = response.css('.product-info__title-link > a::attr(href)').extract()
        full_product_url = []
        for url in product_url:
            full_product_url.append("https://www.dns-shop.ru" + url)
        for i in range(len(full_product_url)):
            try:
                yield scrapy.Request(full_product_url[i],
                                     callback=self.price_parse,
                                     errback=self.errback_page2,
                                     cb_kwargs=dict(product_name=product_name[i],
                                                    product_info=product_info[i],
                                                    product_url=full_product_url[i]))
            except IndexError:
                print("ERROR:", product_name[i])

        print(self.page)
        # Pagination
        # Create Last page
        if not self.last_page:
            self.last_page = response.css('.pagination-widget__page::attr(data-page-number)').extract()[-1]
            print(self.last_page)
        # Exit if scrap last page
        if int(self.last_page) == int(self.page):
            raise scrapy.exceptions.CloseSpider('bandwidth_exceeded')
        else:
            self.page += 1
            next_page = 'https://www.dns-shop.ru/catalog/17a892f816404e77/?f[65c]=264d&p=' + self.page
            if next_page:
                yield scrapy.Request(response.urljoin(next_page),
                                     callback=self.parse)

    def price_parse(self, response, product_name, product_info, product_url):
        price = response.css(".current-price-value::attr(data-price-value)").extract_first()
        info = product_info.split(", ")
        scrap_info = {
            'product_name': product_name,
            'product_url': product_url,
            'price': price,
            'matrix': info[1],
            'processor': info[2],
            'core': info[3],
            'ram': info[4],
            'ssd': info[5],
            'card': info[6],
        }
        return scrap_info

    def errback_page2(self, failure):
        yield dict(main_url=failure.request.cb_kwargs['product_url'])
