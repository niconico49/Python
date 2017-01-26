import os, sys, bottle, bottle_session
from bottle import route, request, run, get, static_file

lib_path = os.path.abspath('../EasyLibrary')
sys.path.append(lib_path)

from ComponentServer import *
from Engine import *
from BatchSession import *
from WebSession import *

class WebService:

  __cwd = None
  __isStarted = False

  @staticmethod
  def setCwd(cwd):
      WebService.__cwd = cwd

  @staticmethod
  def getCwd():
      return WebService.__cwd 

  @staticmethod
  def start(path):
    WebService.setCwd(path)

    batchSession = BatchSession()

    result = WebService.execute("{}", batchSession) 

    app = bottle.app()
    plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
    app.install(plugin)

    run(host = WebService.getHost(), port = WebService.getPort())
    
    return result

  @staticmethod
  def execute(jsonData, session):
      path = WebService.getCwd()
	
      ComponentServer.addParameter("WebService.type", "Classic")
      ComponentServer.addParameter("WebService.path", "webresources/api/execute")

      if (WebService.__isStarted == False):
          WebService.__isStarted = True
          operationType = "Starter"
      else:
          operationType = "Execute";
      
      return Engine.interact(jsonData, session, path, operationType)

  @staticmethod
  def getHost():
      return "127.0.0.1"

  @staticmethod
  def getPort():
      return "8888"
  
  @route("/<projectName>/", method="GET")
  @route("/<projectName>/", method="POST")
  def default(projectName):
      filename = "Starter.html"
      return WebService.sendStatic(projectName, filename)

  @route('/<projectName>/<filename:path>')
  def sendStatic(projectName, filename):
      return static_file(filename, root = WebService.getCwd())

  @route("/<projectName>/webresources/api/execute", method="POST")
  def webService(session, projectName):
      jsonData = request.json['jsonData']
      webSession = WebSession()
      webSession.setSession(session) 
      return WebService.execute(jsonData, webSession);
