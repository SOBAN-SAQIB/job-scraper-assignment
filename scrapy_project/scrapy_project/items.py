# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    """
    Scrapy Item for job listings with all required fields.
    """
    job_title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    department = scrapy.Field()
    employment_type = scrapy.Field()
    posted_date = scrapy.Field()
    job_url = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    source_url = scrapy.Field()
