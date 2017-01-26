#http://candordeveloper.com/2013/03/29/running-apache-on-windows-8-with-python/

import web
import os, sys

lib_path = os.path.abspath('../EasyLibrary')
sys.path.append(lib_path)

from ComponentServer import *
from Interact import *
#from WebSession import *

urls = (
    '/', 'EasyLibraryWeb'
)

class EasyLibraryWeb:
  
  def GET(self):
    return self.POST(self)
  
  def POST(self):
    return "Hello, world!"
  
  @staticmethod
  def execute(jsonData):
    ComponentServer.addParameter("WebService.type", "RESTful")
    ComponentServer.addParameter("WebService.path", "webresources/api/execute")
  
    if (self.__applicationStarted == False):
      self.__applicationStarted = True
      operationType = "Starter"
    else:
      operationType = "Execute"
  
    path = os.getcwd()
    #return Interact.interact(jsonData, WebSession(_SESSION), path, operationType)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()