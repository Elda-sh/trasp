from django.db import models
from django.db.models import Q, Count
from django.utils import timezone


class City(models.Model):
    class Meta:
        verbose_name_plural = "cities"
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=200)
    city = models.ForeignKey('City')

    def __unicode__(self):
        return "{}/{}".format(self.name, self.city.name)


class Train(models.Model):
    number = models.CharField(max_length=10)
    name = models.CharField(max_length=200)

    from_city = models.ForeignKey('City', related_name='from_city')
    to_city = models.ForeignKey('City', related_name='to_city')

    @classmethod
    def create(cls, number, name, timeandstations):
        train = cls(number=number, name=name,
                    from_city=timeandstations[0][1].city,
                    to_city=timeandstations[-1][1].city)
        train.save()
        for time, station in sorted(timeandstations):
            TrainPath.objects.create(
                train=train, station=station, time=time)
        return train

    def __unicode__(self):
        return "#{num} {name}".format(num=self.number, name=self.name)

    @classmethod
    def search_raw(cls, from_city, to_city, train_date):
        c1 = City.objects.get(name=from_city)
        c2 = City.objects.get(name=to_city)

        if train_date:
            return Train.objects.raw(
                """SELECT tp1.train_id as id FROM
                      (SELECT train_id, city_id, time
                       FROM schedule_trainpath tp
                        INNER JOIN schedule_station st
                        ON tp.station_id=st.id) tp1
                      INNER JOIN
                      (SELECT train_id, city_id, time FROM schedule_trainpath tp
                        INNER JOIN schedule_station st
                        ON tp.station_id=st.id) tp2
                    ON tp1.train_id=tp2.train_id
                    AND tp1.city_id=%s AND tp2.city_id=%s
                    AND tp1.time < tp2.time
                    AND DATE(tp1.time) >= %s
                    AND DATE(tp1.time) < %s;
                """, [c1.id, c2.id,
                      train_date,
                      train_date+timezone.timedelta(days=1)])
        else:
            return Train.objects.raw(
                """SELECT tp1.train_id as id FROM
                      (SELECT train_id, city_id, time FROM schedule_trainpath tp
                        INNER JOIN schedule_station st ON tp.station_id=st.id) tp1
                      INNER JOIN
                      (SELECT train_id, city_id, time FROM schedule_trainpath tp
                        INNER JOIN schedule_station st ON tp.station_id=st.id) tp2
                    ON tp1.train_id=tp2.train_id
                    AND tp1.city_id=%s
                    AND tp2.city_id=%s
                    AND tp1.time < tp2.time;
                """, [c1.id, c2.id])


class TrainPath(models.Model):
    train = models.ForeignKey('Train')
    station = models.ForeignKey('Station')
    time = models.DateTimeField()

    def __unicode__(self):
        return "#{num}: {station}".format(
            num=self.train.number, station=self.station)
