from django.db import models


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

    @classmethod
    def create(cls, number, name, timeandstations):
        train = cls(number=number, name=name)
        train.save()
        for time, station in sorted(timeandstations):
            TrainPath.objects.create(
                train=train, station=station, time=time)
        return train

    def __unicode__(self):
        return "#{num} {name}".format(num=self.number, name=self.name)


class TrainPath(models.Model):
    train = models.ForeignKey('Train')
    station = models.ForeignKey('Station')
    time = models.DateTimeField()

    def __unicode__(self):
        return "#{num}: {station}".format(
            num=self.train.number, station=self.station)
