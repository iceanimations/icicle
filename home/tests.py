from django.test import TestCase
from home.models import DepartmentShift, Department
import home.models as home_models
from attendance import models
from datetime import datetime, date, timedelta, time as dTime
from attendance.models import Shift
from datetime import date

class HomeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Department.objects.create(name='Software')
        
        
        e = home_models.Employee.objects.create(username='qurban.ali',
                                                name='Qurban Ali')
        e.activate(date(2018, 9, 26), 9600242)
        s = models.Shift(name='Normal')
        s.save()
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            d = models.Day(name=day)
            d.save()
            status = models.DayOfShift.ON
            if day == 'Saturday': status = models.DayOfShift.OPT
            if day == 'Sunday': status = models.DayOfShift.OFF
            dos = models.DayOfShift(shift=s, day=d, timeFrom=dTime(10, 0),
                                    timeTo=dTime(19, 0), status=status,
                                    isTimeToNextDay=False)
            dos.save()
        es = models.EmployeeShift.objects.create(employee=e, shift=s)
        es.dateFrom = date(2018, 9, 26)
        es.save()
        
        models.Holiday.objects.create(name='Test', date=date(2018, 10, 1))
        empType = home_models.EmployeeType(type='Permanent')
        empType.save()
        etm = home_models.EmployeeTypeMapping.objects.create(employee=e,
                                                             type=empType)
        etm.dateFrom = date(2018, 9, 26)
        etm.save()
        lt = models.LeaveType.objects.create(name=models.LeaveType.CASUAL_LEAVE,
                                             quota=10)
        lt.availability.set([empType])
        lt.save()


    def create_in(self, **kwargs):
        dt = datetime(2018, 9, 26, 9) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=1, date=dt.date(), time=dt.time()).save()

    def create_out(self, **kwargs):
        dt = datetime(2018, 9, 26, 9) + timedelta(**kwargs)
        models.Entry(uid=9600242, tid=2, date=dt.date(), time=dt.time()).save()

    def test_last_dept_shift(self):
        self.assertIsNone(DepartmentShift.lastShift(Department.objects.all()[0]))
        
    def test_dept_shift(self):
        DepartmentShift.objects.create(dept=Department.objects.all()[0],
                                       shift=Shift.objects.all()[0])
        self.assertEqual(len(DepartmentShift.objects.all()), 1)
        self.assertEqual(DepartmentShift.objects.all()[0].dateFrom, date.today())
        self.assertEqual(DepartmentShift.lastShift(Department.objects.all()[0]).shift,
                         Shift.objects.all()[0])
    
    def test_employee_attendances(self):
        self.create_in(hours=2)
        self.create_out(hours=8)
        self.create_in(hours=2, days=6)
        self.create_out(hours=8, days=6)
        self.create_in(hours=2, days=7)
        self.create_out(hours=8, days=7)
        e = home_models.Employee.objects.get(username='qurban.ali')
        self.assertEqual(len(e.attendances(status=models.Attendance.PRESENT)), 3)
        days = (date.today() - date(2018, 9, 26)).days
        # subtract weekends
        days -= len(models.Attendance.objects.filter(
                    status=models.Attendance.WEEKEND))
        # subtract presents
        days -= 3
        # subtract holiday
        days -= 1 # only absetns are left
        self.assertEqual(len(e.absents()), days)
        models.LeaveRequest.objects.create(employee=e, date=date(2018, 10, 4),
                                leaveType=models.LeaveType.objects.all()[0],
                                description='work at home')
        self.assertEqual(len(e.absents()), days)
        # approve the leave
        lv = models.LeaveRequest.objects.filter(employee=e,
                                    status=models.LeaveRequest.PENDING)[0]
        lv.approve(e, 'granted')
        # subtract approved leave
        days -= 1
        self.assertEqual(len(e.absents()), days)
        self.assertEqual(len(e.leaves(models.LeaveType.CASUAL_LEAVE)), 1)