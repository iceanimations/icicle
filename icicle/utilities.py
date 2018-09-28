'''
Created on Sep 6, 2018

@author: qurban.ali
'''
import types
import datetime
import threading

timers = {}
    
def createTimer(func, tm):
    now = datetime.datetime.now()
    nxt = datetime.datetime(now.year, now.month, now.day,
                             tm.hour, tm.minute, tm.second)
    if nxt < now:
        nxt += datetime.timedelta(days=1)
    seconds = (nxt - now).seconds
    t = threading.Timer(seconds, lambda: timerCaller(func, tm))
    timers[t] = (func, tm)
    t.start()
    
def timerCaller(func, tm):
    # calls the func and create new timer at same time
    func()
    createTimer(func, tm)

def removeTimer(func, tm):
    for timer, val in timers.items():
        _func, _tm = val
        if func == _func and tm == _tm:
            timer.cancel()