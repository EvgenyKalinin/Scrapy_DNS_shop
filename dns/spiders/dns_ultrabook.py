import scrapy


class DnsUltrabookSpider(scrapy.Spider):
    page = 1
    name = 'dns_ultrabook'
    allowed_domains = ['dns-shop.ru']
    start_urls = ['https://www.dns-shop.ru/catalog/17a892f816404e77/?f[65c]=264d&p=1']

    # Save scraping info
    custom_settings = {'FEED_URI': "dns_%(time)s.csv",
                       'FEED_FORMAT': 'csv'}

    def parse(self, response):
        print("procesing:" + response.url)
        # Give data of css
        product_name = response.css('.product-info__title-link > a::text').extract()
        # Example: technical parameters
        # [1366x768, SVA (TN+film), Intel Pentium 4417U, 2 х 2.3 ГГц, RAM 4 ГБ,
        #  SSD 128 ГБ, Intel HD 610 , Wi-Fi, Windows 10 Home]
        product_info = response.css('.product-info__title-description::text').extract()

        row_data = zip(product_name, product_info)

        for item in row_data:
            # Create dictionary
            info = item[1].split(", ")
            scraped_info = {
                'page': response.url,
                'product_name': item[0],
                'matrix': info[1],
                'processor': info[2],
                'core': info[3],
                'ram': info[4],
                'ssd': info[5],
                'card': info[6]

            }

            # Generate Information for scraping
            yield scraped_info

        # Pagination
        # TODO: infinity scraping
        max_page = response.css('.pagination-widget__page::attr(data-page-number)').extract()[-1]
        if max_page == DnsUltrabookSpider.page:
            yield scraped_info
        else:
            DnsUltrabookSpider.page += 1
            next_page = 'https://www.dns-shop.ru/catalog/17a892f816404e77/?f[65c]=264d&p=%s' % DnsUltrabookSpider.page 
            if next_page:
                yield scrapy.Request(response.urljoin(next_page),
                                     callback=self.parse)
