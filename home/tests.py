from django.test import TestCase
from home.models import DepartmentShift, Department
from attendance.models import Shift
from datetime import date

class HomeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Shift.objects.create(name='Normal')
        Department.objects.create(name='Software')

    def test_last_dept_shift(self):
        self.assertIsNone(DepartmentShift.lastShift(Department.objects.all()[0]))
        
    def test_dept_shift(self):
        DepartmentShift.objects.create(dept=Department.objects.all()[0],
                                       shift=Shift.objects.all()[0])
        self.assertEqual(len(DepartmentShift.objects.all()), 1)
        self.assertEqual(DepartmentShift.objects.all()[0].dateFrom, date.today())
        self.assertEqual(DepartmentShift.lastShift(Department.objects.all()[0]).shift,
                         Shift.objects.all()[0])