import threading
import PyV8

class ComponentThread():
  __hashSet = {}

  @staticmethod
  def setThreadTimer(callback, delay, onlyOnce, id):
    def handler():
      callback()
      #with PyV8.JSUnlocker():
      ComponentThread.setThreadTimer(callback, delay, onlyOnce, id)

    #with PyV8.JSLocker():
    if onlyOnce == "true":
      timer = threading.Timer(delay / 1000.0, callback)
    else :
      timer = threading.Timer(delay / 1000.0, handler)

    ComponentThread.__hashSet[id] = timer

    #with PyV8.JSLocker():
    with PyV8.JSLocker():
      pass

    timer.start()
    return id 

  @staticmethod
  def cancelThreadTimer(id):
    if id in ComponentThread.__hashSet:
      ComponentThread.__hashSet[id].cancel()
      del ComponentThread.__hashSet[id]

'''
from threading import Timer, Thread, Event
#import threading

class ComponentThread:

  __hashSet = {}

  @staticmethod
  def setThreadTimer(fn, delay, onlyOnce, id):
    if onlyOnce == "true":
      onlyOnce = 1
    else:
      onlyOnce = 0

    ComponentThread.set_interval(fn, delay, onlyOnce, id)
    #timer = threading.Timer(delay, fnWrapper)
    #timer.start()
    #ComponentThread.__hashSet[id] = timer  
    return id   
  
  @staticmethod
  def cancelThreadTimer(id):
    if id in ComponentThread.__hashSet:
      timer = ComponentThread.__hashSet[id]
      timer.cancel()  
      del ComponentThread.__hashSet[id]

  @staticmethod
  def set_interval(fn, delay, onlyOnce, id):
    def fnWrapper(fn):
      fn()
      if not onlyOnce:
        ComponentThread.set_interval(fn, delay, onlyOnce, id)


    timer = Timer(delay, fnWrapper)
    timer.start()
    ComponentThread.__hashSet[id] = timer  
'''
'''
from threading import Timer, Thread, Event

class SingleThread:
  def __init__(self, fn, delay, onlyOnce):
    self.delay = delay
    
    if onlyOnce == "true":
      self.onlyOnce = 1
    else :
      self.onlyOnce = 0

    self.thread = Timer(self.delay, self.handle_function, fn)

  def handle_function(self, fn):
    print (fn)
    fn()
    if not self.onlyOnce:
      self.thread = Timer(self.delay, self.handle_function, fn)
      self.thread.start()

  def start(self):
    self.thread.start()

  def cancel(self):
    self.thread.cancel()

class ComponentThread:

  __hashSet = {}

  @staticmethod
  def setThreadTimer(fn, delay, onlyOnce, id):
    #singleThread = ComponentThread.SingleThread(fn, delay / 1000, onlyOnce)
    singleThread = SingleThread(fn, delay / 1000, onlyOnce)
    singleThread.start()
    ComponentThread.__hashSet[id] = singleThread  
    return id   
  
  @staticmethod
  def cancelThreadTimer(id):
    if id in ComponentThread.__hashSet:
      singleThread = ComponentThread.__hashSet[id]
      singleThread.cancel()  
      del ComponentThread.__hashSet[id]
'''