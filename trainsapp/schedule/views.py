from itertools import groupby
import json
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import dateparse
from django.utils import timezone

from schedule.models import City, Train, Station, TrainPath


def create_calendar(start, now, events, days):
    calendar = []

    for j in xrange(4):
        week = []
        for i in xrange(7):
            day = {}
            day['date'] = start + timezone.timedelta(days=i)
            day['is_today'] = (now.date() == day['date'])
            try:
                i = days.index(day['date'])
                day['events'] = events[i]
            except ValueError:
                day['events'] = []

            week.append(day)

        calendar.append(week)
        start = week[-1]['date'] + timezone.timedelta(days=1)

    return calendar


def home(request):
    is_search = False
    from_city = request.GET.get('from_city')
    to_city = request.GET.get('to_city')
    train_date = dateparse.parse_date(request.GET.get('date', ''))
    if from_city and to_city:
        is_search = True
        try:
            searched_trains = Train.search_raw(from_city, to_city, train_date)
            train_count = len(list(searched_trains))
        except City.DoesNotExist:
            train_count = 0
            zero_results = "Nothing found"

    if not is_search:
        cities = City.objects.all()[:50]
        trains = Train.objects.filter(
            departure_time__gte=timezone.now().date()
            ).order_by('departure_time')[:50]

    return render_to_response('index.html', locals())


def view_station(request, station_id):
    now = timezone.localtime(timezone.now())
    start = now.date() - timezone.timedelta(days=now.weekday())

    station = get_object_or_404(Station, pk=station_id)
    trains = TrainPath.objects.filter(station=station).filter(
        time__gte=start,
        time__lte=start + timezone.timedelta(days=28)
    )

    trains_by_day = []
    days = []
    for k, g in groupby(trains, lambda e: e.time.date()):
        trains_by_day.append(list(g))
        days.append(k)

    calendar = create_calendar(start, now, trains_by_day, days)

    return render_to_response('station.html', locals())


def view_train(request, train_id):
    train = get_object_or_404(Train, pk=train_id)
    path = TrainPath.objects.filter(train=train)
    return render_to_response('train.html', locals())


def get_cities(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        cities = City.objects.filter(name__icontains=q)[:20]
        results = [c.name for c in cities]
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
