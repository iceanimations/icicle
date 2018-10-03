'''
Created on Sep 6, 2018

@author: qurban.ali
'''
import datetime
import threading

timers = {}

def createTimer(func, tm, repeat=False):
    # check if it already exists
    for _, val in timers.items():
        if (func, tm) == val:
            raise ValueError('A Timer already exists')

    now = datetime.datetime.now()
    nxt = datetime.datetime(now.year, now.month, now.day,
                             tm.hour, tm.minute, tm.second, 0)
    if repeat or nxt < now:
        nxt = nxt + datetime.timedelta(days=1)
    seconds = (nxt - now).total_seconds()
    t = threading.Timer(seconds, lambda: timerCaller(func, tm))
    timers[t] = (func, tm)
    t.start()

def timerCaller(func, tm):
    # calls the func and create new timer at same time
    func()
    removeTimer(func, tm)
    createTimer(func, tm, repeat=True)

def removeTimer(func, tm):
    for timer, val in timers.items():
        _func, _tm = val
        if func == _func and tm == _tm:
            timer.cancel()
            break
    timers.pop(timer)
    
def createTimerCaller():
    '''
    this method is called only once, when starting the application
    '''
    print ('create timer caller')