from django.utils import timezone
from django.db.models import Q, Count

from schedule.models import City, Train, TrainPath


def create_train(number, name, timeandstations):
    """ Creates a new train object

    Args:
        number (str): Train number
        name (str): Train name
        timeandstations (list of tuples): List of time and Station object

    Returns:
        models.Train: Train object

    """
    train = Train(number=number, name=name,
                  from_city=timeandstations[0][1].city,
                  to_city=timeandstations[-1][1].city,
                  departure_time=timeandstations[0][0])
    train.save()
    for time, station in sorted(timeandstations):
        TrainPath.objects.create(
            train=train, station=station, time=time)
    return train


def search_train(from_city, to_city, train_date):
    """ Looking for trains which has from City to City

        If date is None returns all trains

    Args:
        from_city (str): City name start point
        to_city (str): City name to_city
        train_date (date object): Departure date, could be None

    Returns:
        list: List of train objects

    """
    c1 = City.objects.get(name=from_city)
    c2 = City.objects.get(name=to_city)

    if train_date:
        TrainPathQ = TrainPath.objects.filter(
            time__gte=train_date,
            time__lte=train_date+timezone.timedelta(days=1))
    else:
        TrainPathQ = TrainPath.objects.all()

    train_dict = TrainPathQ.filter(
        Q(station__city=c1) | Q(station__city=c2)
    ).values('train_id').annotate(
        Count('id')
    ).order_by().filter(id__count__gt=1)

    trains = []
    for x in train_dict:
        try:
            tp1 = TrainPath.objects.filter(
                    train__pk=x['train_id']
                ).filter(station__city=c1)[0]
            tp2 = TrainPath.objects.filter(
                    train__pk=x['train_id']
                ).filter(station__city=c2)[0]
            if tp1.time < tp2.time:
                tp1.train.st_dep_time = tp1.time
                tp1.train.st_arr_time = tp2.time
                td = (tp2.time-tp1.time)
                tp1.train.traveltime = 24*td.days+td.seconds//3600

                trains.append(tp1.train)
        except IndexError:
            print("Exception in search: TrainPath filter IndexError")
            print(from_city, to_city, train_date)
            pass

    return sorted(trains, key=lambda tr: tr.st_dep_time)


def search_train_raw(from_city, to_city, train_date):
    """ Looking for trains which has from City to City

        The same as search_train, but different realisation.
        If date is None returns all trains

    Args:
        from_city (str): City name start point
        to_city (str): City name to_city
        train_date (date object): Departure date, could be None

    Returns:
        list: List of train objects

    """
    c1 = City.objects.get(name=from_city)
    c2 = City.objects.get(name=to_city)

    if train_date:
        return Train.objects.raw(
            """SELECT tp1.train_id as id,
            tp1.time as st_dep_time,
            tp2.time as st_arr_time,
            TIMESTAMPDIFF(HOUR, tp1.time, tp2.time) as traveltime FROM
                  (SELECT train_id, city_id, time
                   FROM schedule_trainpath tp
                    INNER JOIN schedule_station st
                    ON tp.station_id=st.id) tp1
                  INNER JOIN
                  (SELECT train_id, city_id, time
                   FROM schedule_trainpath tp
                    INNER JOIN schedule_station st
                    ON tp.station_id=st.id) tp2
                ON tp1.train_id=tp2.train_id
                AND tp1.city_id=%s AND tp2.city_id=%s
                AND tp1.time < tp2.time
                AND DATE(tp1.time) >= %s
                AND DATE(tp1.time) < %s
                ORDER BY st_dep_time;
            """, [c1.id, c2.id,
                  train_date,
                  train_date+timezone.timedelta(days=1)])
    else:
        return Train.objects.raw(
            """SELECT tp1.train_id as id,
            tp1.time as st_dep_time,
            tp2.time as st_arr_time,
            TIMESTAMPDIFF(HOUR, tp1.time, tp2.time) as traveltime FROM
                  (SELECT train_id, city_id, time
                   FROM schedule_trainpath tp
                    INNER JOIN schedule_station st
                    ON tp.station_id=st.id) tp1
                  INNER JOIN
                  (SELECT train_id, city_id, time
                   FROM schedule_trainpath tp
                    INNER JOIN schedule_station st
                    ON tp.station_id=st.id) tp2
                ON tp1.train_id=tp2.train_id
                AND tp1.city_id=%s
                AND tp2.city_id=%s
                AND tp1.time < tp2.time
                ORDER BY st_dep_time;
            """, [c1.id, c2.id])
