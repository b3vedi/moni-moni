import random
import os
import django
import dotenv

os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"
django.setup()
dotenv.read_dotenv(".env")

from django_seed import Seed
from server.apps.catalogue.models import Category, Fundraiser


def init_seeders(seeders_list):
    seeders = dict()
    for seeder in seeders_list:
        seeders[seeder] = Seed.seeder(locale="en_US")
    return seeders


def seed(seeders):
    for name, seeder in seeders.items():
        if name == "fundraiser":
            seeder.add_entity(
                Fundraiser,
                {
                    "title": lambda x: seeder.faker.title(),
                    "author": lambda x: seeder.faker.name(),
                    "description": lambda x: seeder.faker.word(),
                    "image": lambda x: seeder.faker.word(),
                    "slug": lambda x: seeder.faker.word(),
                    "tags": lambda x: seeder.faker.word(),
                    "total_amount": random.randint(10000000, 3030430405450),
                    "remaining_amount": random.randint(10000000, 3030430405450),
                    "fund_method": random.randint(10000000, 3030430405450),
                },
            )


def execute(seeders):
    l = list()
    for seeder in seeders:
        l.append(seeder.execute())
    print(l)
    return l


if __name__ == "__main__":
    seeders_list = [
        # "category",
        "fundraiser",
        # "funding_options",
        # "payment_selection",
        # "order",
        # "order_item",
        # "custom_user",
        # "address",
    ]
    seeders = init_seeders(seeders_list)
    seed(seeders)
    execute(seeders)
