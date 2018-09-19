# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register([Day, Ramzan, Holiday, Session, LeaveType,
                     Attendance, LeaveRequest])

class DayOfShiftInline(admin.TabularInline):
    model = Shift.days.through
    extra = 1

class ShiftAdmin(admin.ModelAdmin):
    inlines = [DayOfShiftInline]

admin.site.register(Shift, ShiftAdmin)