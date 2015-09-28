#!/usr/bin/env python
import string
import random
from faker import Faker
from django.utils import timezone as timezone2
from datetime import timedelta

from schedule.models import City, Station, Train, TrainPath
from schedule.logic import create_train
fake = Faker()


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

        create_train(number, name, zip(stns_time, stns))


def run(num_cities=10, num_trains=4):
    create_cities(num_cities)
    create_stations()
    create_trains(num_trains)


def clean():
    City.objects.all().delete()
    Station.objects.all().delete()
    Train.objects.all().delete()
    TrainPath.objects.all().delete()
