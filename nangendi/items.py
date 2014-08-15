# -*- coding: utf-8 -*-

from scrapy import Field, Item
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import TakeFirst


class PlaceItem(Item):
    url = Field()
    place_id = Field()
    name = Field()
    raw_address = Field()
    provinsi = Field()
    kabupaten_kota = Field()
    kecamatan = Field()
    kelurahan = Field()
    info = Field()


class PlaceLoader(ItemLoader):
    default_item_class = PlaceItem
    default_output_processor = TakeFirst()
