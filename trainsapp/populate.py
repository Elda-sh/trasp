#!/usr/bin/env python
from datetime import datetime
import string
import random
from faker import Faker
from pytz import timezone
from django.utils import timezone as timezone2
from datetime import timedelta

from django.conf import settings
from schedule.models import City, Station, Train, TrainPath
fake = Faker()


def random_date(now_plus=28):
    current_tz = timezone(settings.TIME_ZONE)
    fake_date = fake.date_time_between(datetime.now(), now_plus)
    return current_tz.localize(fake_date)


def create_cities(cities_num):
    for i in xrange(cities_num):
        City.objects.create(name=fake.city())


def create_stations():
    stations_names = ["Main Station", "Central Station", "South Station",
                      "North Station", "East Station", "West Station"]
    for c in City.objects.all():
        snum = 1
        if random.random() > 0.9:
            snum += 1

        for i in xrange(snum):
            name = random.choice(stations_names)
            Station.objects.create(name=name, city=c)


def create_trains(num_trains):
    num_cities = City.objects.all().count()
    for i in xrange(num_trains):
        number = "{}{}".format(random.randint(1, 10000),
                               random.choice(string.ascii_letters))
        name = fake.military_ship()

        cities = []
        for i in xrange(random.randint(2, num_cities)):
            city = City.objects.all()[random.randint(0, num_cities-1)]
            if city not in cities:
                cities.append(city)

        if len(cities) < 2:
            continue

        stns = []
        for c in cities:
            num_st = c.station_set.all().count()
            stns.append(c.station_set.all()[random.randint(0, num_st-1)])

        stns_time = [timezone2.now() +
                     timedelta(hours=random.randint(-48, 48)), ]
        for s in stns[1:]:
            stns_time.append(stns_time[-1] +
                             timedelta(hours=random.randint(1, 4)))

        Train.create(number, name, zip(stns_time, stns))


def run(num_cities=10, num_trains=4):
    create_cities(num_cities)
    create_stations()
    create_trains(num_trains)


def clean():
    City.objects.all().delete()
    Station.objects.all().delete()
    Train.objects.all().delete()
    TrainPath.objects.all().delete()
