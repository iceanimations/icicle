'''
Created on Oct 16, 2018

@author: qurban.ali
'''
from django import template


register = template.Library()

@register.simple_tag
def availedLeaves(employee, typ, year):
    return employee.availedLeaves(typ, year)