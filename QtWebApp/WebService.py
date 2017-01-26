import os, sys, bottle, bottle_session
import _thread
from bottle import hook, route, request, response, run, get, static_file

lib_path = os.path.abspath('../QtWebApp')
sys.path.append(lib_path)

from WebForm import *

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

class WebService():

  __cwd = None
  __isStarted = False

  @staticmethod
  def setCwd(cwd):
      WebService.__cwd = cwd

  @staticmethod
  def getCwd():
      return WebService.__cwd 

  @staticmethod
  def start_server():
    # Setup stuff here...
    print("run")
    app = bottle.app()
    plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
    app.install(plugin)
    app.install(EnableCors())
    
    run(host = WebService.getHost(), port = WebService.getPort())

  @staticmethod
  def start(path):
    WebService.setCwd(path)

    if 1 == 0:
       app = bottle.app()
       plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
       app.install(plugin)

    # start the server in a background thread
    _thread.start_new_thread(WebService.start_server, ())

    print("The server is running but my script is still executing!")

    result = WebService.execute("{}") 
    return result

  @staticmethod
  def execute(jsonData):
      path = WebService.getCwd()
	
      if (WebService.__isStarted == False):
          WebService.__isStarted = True
          operationType = "Starter"
      else:
          operationType = "Execute";
      
      #return Engine.interact(jsonData, session, path, operationType)
      WebForm.interact(jsonData)

  @staticmethod
  def getHost():
      return "127.0.0.1"

  @staticmethod
  def getPort():
      return "8080"
  
  #@hook('after_request') 
  #def enable_cors(): 
      """ 
      You need to add some headers to each request. 
      Don't use the wildcard '*' for Access-Control-Allow-Origin in production. 
      """ 
      """ 
      response.headers['Access-Control-Allow-Origin'] = '*' 
      response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS' 
      response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token' 
      """ 

  @route("/<projectName>/", method="GET")
  @route("/<projectName>/", method="POST")
  def default(projectName):
      filename = "Starter.html"
      return WebService.sendStatic(projectName, filename)

  @route('/<projectName>/<filename:path>')
  def sendStatic(projectName, filename):
      return static_file(filename, root = WebService.getCwd())

  #@route("/<projectName>/webresources/api/execute", method="GET")
  @route("/<projectName>/webresources/api/execute", method="POST")
  @route("/<projectName>/webresources/api/execute", method="OPTIONS")
  def webService(session, projectName):
      jsonData = request.json['jsonData']
      print (jsonData)
      return WebForm.interact1(jsonData)
      #return WebService.execute(jsonData);
