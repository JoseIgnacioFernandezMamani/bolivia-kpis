import scrapy


class ElectionResultItem(scrapy.Item):
    year = scrapy.Field()
    election_type = scrapy.Field()
    department = scrapy.Field()
    party = scrapy.Field()
    candidate = scrapy.Field()
    votes = scrapy.Field()
    percentage = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()


class ConflictItem(scrapy.Item):
    title = scrapy.Field()
    department = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    type = scrapy.Field()
    description = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()


class EconomicDataItem(scrapy.Item):
    indicator = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    value = scrapy.Field()
    unit = scrapy.Field()
    department = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()


class ContractItem(scrapy.Item):
    sicoes_id = scrapy.Field()
    title = scrapy.Field()
    amount = scrapy.Field()
    contractor = scrapy.Field()
    department = scrapy.Field()
    date = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()


class EnvironmentItem(scrapy.Item):
    indicator = scrapy.Field()
    year = scrapy.Field()
    value = scrapy.Field()
    unit = scrapy.Field()
    geometry_wkt = scrapy.Field()
    source_url = scrapy.Field()
    scraped_at = scrapy.Field()
