# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register([Day, Shift, Ramzan, Holiday])

class LeaveAvailabilityInline(admin.TabularInline):
    model = LeaveType.availability.through
    extra = 1
    
class LeaveTypeAdmin(admin.ModelAdmin):
    inlines = (LeaveAvailabilityInline,)
    
class DayOfWeekendInline(admin.TabularInline):
    model = DayOfWeekend
    extra = 1
    
class WeekendAdmin(admin.ModelAdmin):
    inlines = (DayOfWeekendInline,)
    
class InOutAdmin(admin.ModelAdmin):
    exclude = ('inoutId', 'datetime')
    
admin.site.register(Weekend, WeekendAdmin)
admin.site.register(LeaveType, LeaveTypeAdmin)
admin.site.register(InOut, InOutAdmin)