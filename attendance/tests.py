from django.test import TestCase
from . import models
from home import models as home_models
from datetime import datetime, date, timedelta
import time

# Create your tests here.
class SessionTestCase(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        e = home_models.Employee.objects.create(username='qurban.ali',
                                                name='Qurban Ali')
        e.activate(date.today(), 9600242)
    
    def create_in(self, **kwargs):
        models.Entry(uid=9600242, tid=1, date=date.today(),
                                    time=datetime.time(datetime.now() + timedelta(**kwargs))).save()
                                    
    def create_out(self, **kwargs):
        models.Entry(uid=9600242, tid=2, date=date.today(),
                                    time=datetime.time(datetime.now() +
                                                       timedelta
                                                       (**kwargs))).save()

    def test_out_is_null(self):
        self.create_in()
        s = models.Session.objects.filter(employee__employeeperiod__code=9600242).order_by('inTime').last()
        # test if out is None
        self.assertEqual(s.outTime, None)
        # test for session in out types
        self.assertTrue(s.inType == models.Session.BIOMETRIC)
        self.assertTrue(s.outType == '')
        
    def test_in_out_duration(self):
        duration = 1
        self.create_in()
        self.create_out(hours=duration)
        s = models.Session.objects.all()[0]
        # test if the duration is same as specified
        self.assertTrue((s.outTime - s.inTime) == timedelta(hours=duration))
        # test if there is only one session
        self.assertEqual(len(models.Session.objects.all()), 1)
        # test if there are only two Entry objects
        self.assertEqual(len(models.Entry.objects.all()), 2)
        # test for session in out types
        self.assertTrue(s.inType == models.Session.BIOMETRIC)
        self.assertTrue(s.outType == models.Session.BIOMETRIC)
        
        
    def test_consecutive_ins(self):
        self.create_in()
        time.sleep(2)
        self.create_in()
        s = models.Session.objects.all().order_by('inTime')
        # test if there are two Session objects
        self.assertTrue(len(s) == 2)
        # test if in out types
        self.assertTrue(s.first().outType == models.Session.COMPUTED)
        self.assertTrue(s.first().inType == models.Session.BIOMETRIC)
        self.assertTrue(s.last().inType == models.Session.BIOMETRIC)
        # test if last out is None
        self.assertTrue(s.last().outTime is None)
        # test if the duration between first out and second in is 1 sec
        self.assertEqual(s.last().inTime - s.first().outTime, timedelta(seconds=1))
        
    def test_consecutive_outs(self):
        self.create_in()
        self.create_out(hours=1)
        self.create_out(hours=2)
        # test if there are only two session and three entry objects
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 3)
        self.assertEqual(len(s), 2)
        # test if the last session is 1 second long
        self.assertEqual(s.last().outTime - s.last().inTime, timedelta(seconds=1))
        
    def test_in_between_session(self):
        duration = 1
        self.create_in()
        self.create_out(hours=duration)
        self.create_in(minutes=30)
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 3)
        self.assertEqual(len(s), 2)
        # test if first out and second in are 1 second long
        self.assertEqual(s.last().inTime - s.first().outTime, timedelta(seconds=1))
        # test if first out is computed
        self.assertEqual(s.first().outType, models.Session.COMPUTED)
        
    def test_out_between_session(self):
        self.create_in()
        self.create_out(hours=1)
        self.create_out(minutes=30)
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 3)
        self.assertEqual(len(s), 2)
        # test if first out is Biometric and second in is computed
        self.assertEqual(s.first().outType, models.Session.BIOMETRIC)
        self.assertEqual(s.last().inType, models.Session.COMPUTED)
        
    def test_out_before_in(self):
        self.create_out(hours=1)
        self.create_in()
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 2)
        self.assertEqual(len(s), 1)
        # test if session is 1 hour long
        self.assertEqual(s[0].outTime - s[0].inTime, timedelta(hours=1))
    
    def test_days_long_session(self):
        self.create_in()
        self.create_out(days=1, hours=1)
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 2)
        self.assertEqual(len(s), 2)