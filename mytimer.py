# -*- coding: utf-8 -*-
## My Timer Class ##

from threading import Timer as threadTimer
from time import time

class MyTimer:
    def __init__(self,deadline,stop):
        self.deadline = deadline
        self.stop = stop
        self.timer = threadTimer(deadline, stop,args=None)
        self.acumTime = 0.0
        self.timer.start()
        self.startTime = time()
    def pause(self):
        self.cancel()
    def resume(self):
        self.timer = threadTimer(self.deadline-(self.acumTime),  self.stop, args=None)
        self.startTime = time()
        self.timer.start()
    def cancel(self):
        self.acumTime += time()-self.startTime
        self.timer.cancel()
    def remaining(self):
        self.cancel()
        self.resume()
        return int(self.deadline-self.acumTime)


