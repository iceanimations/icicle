'''
Created on Aug 17, 2018

@author: qurban.ali
'''
from __future__ import unicode_literals
from django.contrib import admin
from .models import Employee, EmployeeType, Designation, Department, Project

admin.site.register([Employee, EmployeeType, Designation,
                     Department, Project])