# -*- coding: utf-8 -*-

from urlparse import urljoin

from scrapy import FormRequest, Request, Spider
from scrapy.contrib.loader.processor import MapCompose
from scrapy.shell import inspect_response

from nangendi.items import PlaceLoader


class PastipasPertaminaComSpider(Spider):
    name = 'pastipas.pertamina.com'
    start_urls = ['http://pastipas.pertamina.com/lokasi.asp']

    def parse(self, response):
        inspect_response(response)
        all_provinces_value = response.xpath(
            '//select[@name="propinsi"]/option[contains(., "All")]/@value'
        ).extract()[0]

        return FormRequest.from_response(
            response,
            formdata={
                'propinsi': all_provinces_value,
                'keyword': '',
                'submit': 'search!',
            },
            callback=self.parse_list
        )

    def parse_list(self, response):
        spbu_links = response.xpath('//a[contains(@href, "?id=")]')
        for spbu_link in spbu_links:
            spbu_name = u''.join(spbu_link.xpath('./text()').extract())
            spbu_href = u''.join(spbu_link.xpath('./@href').extract())
            spbu_url = urljoin(response.url, spbu_href)
            yield Request(
                spbu_url,
                callback=self.parse_item,
                meta={
                    'spbu_name': spbu_name
                }
            )

    def parse_item(self, response):
        place_loader = PlaceLoader(response=response)
        place_loader.add_value('url', response.url)
        place_loader.add_value('name', response.meta['spbu_name'])
        place_loader.add_value(
            'place_id',
            response.meta['spbu_name'],
            MapCompose(
                lambda s: s.split(',')[0].replace(u'SPBU ', u'')
            )
        )
        place_loader.add_xpath(
            'raw_address',
            '//strong[contains(., "Alamat")]/following-sibling::text()[1][normalize-space()]',
            MapCompose(
                unicode.strip
            )
        )
        place_loader.add_xpath(
            'provinsi',
            '//strong[contains(., "Alamat")]/following-sibling::text()[3][normalize-space()]',
            MapCompose(
                unicode.strip
            ),
            re=r'\s-\s(.+)$'
        )
        place_loader.add_xpath(
            'kabupaten_kota',
            '//strong[contains(., "Alamat")]/following-sibling::text()[3][normalize-space()]',
            MapCompose(
                unicode.strip
            ),
            re=r'(.+)\s-\s'
        )

        info = dict()
        facilities = response.xpath(
            '//strong[contains(.,"Fasilitas")]/following-sibling::text()'
            '[count(preceding-sibling::strong)=2]'
        ).extract()
        facilities = [f for f in [f.strip().replace(u'- ', u'') for f in facilities] if f]
        if facilities:
            info['Fasilitas'] = facilities

        products = response.xpath(
            '//strong[contains(.,"Produk")]/following-sibling::text()'
        ).extract()
        products = [p for p in [p.strip().replace(u'- ', u'') for p in products] if p]
        if products:
            info['Produk'] = products

        place_loader.add_value('info', info)

        return place_loader.load_item()
