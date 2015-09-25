from django.contrib import admin
from schedule.models import City, Station, Train, TrainPath


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    pass


@admin.register(TrainPath)
class TrainPathAdmin(admin.ModelAdmin):
    pass
