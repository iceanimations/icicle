from django.test import TestCase
from . import models
from home import models as home_models
from datetime import datetime, date, timedelta, time as dTime
import time
import pytz
from icicle import settings, utilities

# Create your tests here.

class AttendanceTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        e = home_models.Employee.objects.create(username='qurban.ali',
                                                name='Qurban Ali')
        e.activate(date.today(), 9600242)
        s = models.Shift(name='Normal')
        s.save()
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            d = models.Day(name=day)
            d.save()
            if day == 'Sunday': status = models.DayOfShift.OFF
            status = models.DayOfShift.ON
            if day == 'Saturday': status = models.DayOfShift.OPT
            dos = models.DayOfShift(shift=s, day=d, timeFrom=dTime(10, 0),
                                    timeTo=dTime(19, 0), status=status,
                                    isTimeToNextDay=False)
            dos.save()
        models.EmployeeShift.objects.create(employee=e, shift=s)
            
        
    
    def create_in(self, **kwargs):
        dt = datetime(2018, 9, 26, 9) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=1, date=dt.date(), time=dt.time()).save()

    def create_out(self, **kwargs):
        dt = datetime(2018, 9, 26, 9) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=2, date=dt.date(), time=dt.time()).save()

    def test_out_is_null(self):
        self.create_in()
        s = models.Session.objects.filter(employee__employeeperiod__code=9600242).order_by('inTime').last()
        # test if out is None
        self.assertEqual(s.outTime, None)
        # test for session in out types
        self.assertTrue(s.inType == models.Session.BIOMETRIC)
        self.assertTrue(s.outType == '')
        
    def test_in_out_duration(self):
        duration = 2
        self.create_in()
        self.create_out(hours=duration)
        s = models.Session.objects.all()
        # test if there is only one session
        self.assertEqual(len(s), 2)
        # test if there are only two Entry objects
        self.assertEqual(len(models.Entry.objects.all()), 2)
        # test if the duration is same as specified
        self.assertEqual((s[0].outTime - s[0].inTime) + (s[1].outTime - s[1].inTime), timedelta(hours=duration, seconds=-1))
        # test for session in out types
        self.assertTrue(s[0].inType == models.Session.BIOMETRIC)
        self.assertTrue(s[0].outType == models.Session.COMPUTED)
        
        
    def test_consecutive_ins(self):
        self.create_in()
        self.create_in(minutes=10)
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
        self.create_out(days=10)
        e = models.Entry.objects.all()
        s = models.Session.objects.all().order_by('inTime')
        self.assertEqual(len(e), 2)
        self.assertEqual(len(s), 3)
        tz = pytz.timezone(settings.TIME_ZONE)
        self.assertEqual(s.first().outTime, tz.localize(datetime(2018, 9, 26,
                                                                 9, 59, 59)))
        self.assertEqual(s.last().inTime, tz.localize(datetime(2018, 10, 5,
                                                               10)))
    
    def test_single_attendance(self):
        self.create_in()
        self.create_out(hours=2)
        a = models.Attendance.objects.all()
        #print (models.Sessio)
        self.assertEqual(len(a), 1)
    
    def test_in_after_endtime(self):
        self.create_in(hours=11)
        self.create_out(hours=12)
        a = models.Attendance.objects.all()
        self.assertEqual(len(a), 0)
    
    def test_days_long_attendance(self):
        self.create_in(hours=2)
        self.create_out(days=10)
        a = models.Attendance.objects.all().order_by('date')
        self.assertEqual(len(a), 2)
        self.assertEqual(a.first().date, date(2018, 9, 26))
        self.assertEqual(a.last().date, date(2018, 10, 5))
        
    def test_consecutive_attendance_ins(self):
        self.create_in()
        self.create_in(days=1)
        self.create_out(days=1, hours=11)
        a = models.Attendance.objects.all()
        self.assertEqual(len(a), 2)
        
    def test_in_between_days_long_out(self):
        self.create_in()
        self.create_in(days=5)
        self.create_in(days=6, hours=2)
        self.create_out(days=10)
        a = models.Attendance.objects.all()
        self.assertEqual(len(a), 4)