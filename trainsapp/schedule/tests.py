from django.test import TestCase
from django.utils import timezone

from schedule.models import Train
from schedule.logic import search_train_raw
import populate as pop


class TrainTest(TestCase):
    def setUp(self):
        pop.run()

    def test_search(self):
        """Test search by searching existing route"""
        train = Train.objects.all()[0]
        st1 = train.trainpath_set.all()[0].station
        st2 = train.trainpath_set.all()[1].station

        # from st1 to st1
        search = search_train_raw(st1.city.name, st2.city.name, None)
        self.assertTrue(train in list(search))

        # but not backwards
        search = search_train_raw(st2.city.name, st1.city.name, None)
        self.assertFalse(train in list(search))

    def test_date_search(self):
        """Test search by searching existing route"""
        train = Train.objects.all()[0]
        tp1 = train.trainpath_set.all()[0]

        st1, time1 = tp1.station, tp1.time
        st2 = train.trainpath_set.all()[1].station

        search = search_train_raw(st1.city.name, st2.city.name, None)
        for train in search:
            st = train.trainpath_set.get(station=st1)
            self.assertTrue(abs(st.time - time1) <= timezone.timedelta(1))
