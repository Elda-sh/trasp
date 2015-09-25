from django.shortcuts import render_to_response, get_object_or_404

from schedule.models import Train, Station, TrainPath


def home(request):
    stations = Station.objects.all()
    trains = Train.objects.all()
    return render_to_response('index.html', locals())


def view_station(request, station_id):
    station = get_object_or_404(Station, pk=station_id)
    trains = TrainPath.objects.filter(station=station)
    return render_to_response('station.html', locals())


def view_train(request, train_id):
    train = get_object_or_404(Train, pk=train_id)
    path = TrainPath.objects.filter(train=train)
    return render_to_response('train.html', locals())
