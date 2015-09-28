from django.db import models


class City(models.Model):
    class Meta:
        verbose_name_plural = 'cities'
        ordering = ['name']

    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Station(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(max_length=200)
    city = models.ForeignKey('City')

    def __unicode__(self):
        return '{} / {}'.format(self.city.name, self.name)


class Train(models.Model):
    class Meta:
        ordering = ['departure_time']

    number = models.CharField(max_length=10)
    name = models.CharField(max_length=200)

    from_city = models.ForeignKey('City', related_name='from_city')
    to_city = models.ForeignKey('City', related_name='to_city')

    departure_time = models.DateTimeField()

    def __unicode__(self):
        return '#{num} {name}, {fr} - {to}'.format(
            num=self.number, name=self.name,
            fr=self.from_city, to=self.to_city)


class TrainPath(models.Model):
    class Meta:
        ordering = ['time']

    train = models.ForeignKey('Train')
    station = models.ForeignKey('Station')
    time = models.DateTimeField()

    def __unicode__(self):
        return '#{num}: {station}'.format(
            num=self.train.number, station=self.station)
