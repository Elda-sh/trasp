from django.utils import timezone

from schedule.models import City, Train, TrainPath


def create_train(number, name, timeandstations):
    train = Train(number=number, name=name,
                  from_city=timeandstations[0][1].city,
                  to_city=timeandstations[-1][1].city,
                  departure_time=timeandstations[0][0])
    train.save()
    for time, station in sorted(timeandstations):
        TrainPath.objects.create(
            train=train, station=station, time=time)
    return train


def search_train_raw(from_city, to_city, train_date):
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
