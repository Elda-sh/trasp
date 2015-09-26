from django.shortcuts import render_to_response, get_object_or_404
from django.utils import dateparse

from schedule.models import City, Train, Station, TrainPath


def home(request):
    stations = Station.objects.all()
    trains = Train.objects.all()

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

    return render_to_response('index.html', locals())


def view_station(request, station_id):
    station = get_object_or_404(Station, pk=station_id)
    trains = TrainPath.objects.filter(station=station)
    return render_to_response('station.html', locals())


def view_train(request, train_id):
    train = get_object_or_404(Train, pk=train_id)
    path = TrainPath.objects.filter(train=train)
    return render_to_response('train.html', locals())
