from PyQt5 import QtCore, QtWidgets
import sys, time

import os, sys, bottle, bottle_session
#import _thread
from PyQt5 import QtCore
from bottle import hook, route, request, response, run, get, static_file
#from flask_classy import FlaskView, route

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

class WebService(QtCore.QThread):

  __cwd = None
  __isStarted = False

  #def __init__(self, parent=None):
      #print("_init")
      #QtCore.QThread.__init__(self, parent)
  def __init__(self, parent):
      super(WebService, self).__init__(parent)

  @staticmethod
  def getInstance():
      return WebService(QtCore.QThread)

  @staticmethod
  def setCwd(cwd):
      WebService.__cwd = cwd

  @staticmethod
  def getCwd():
      return WebService.__cwd 

  #@staticmethod
  def run(self):
  #def start_server():
    # Setup stuff here...
    print("run")
    app = bottle.app()
    plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
    app.install(plugin)
    app.install(EnableCors())
    
    run(host = WebService.getHost(), port = WebService.getPort())

  @staticmethod
  def starter(path):
    WebService.setCwd(path)

    if 1 == 0:
       app = bottle.app()
       plugin = bottle_session.SessionPlugin(cookie_lifetime=600)
       app.install(plugin)

    WebService.start(WebService.getInstance());
    # start the server in a background thread
    #_thread.start_new_thread(WebService.start_server, ())

    print("The server is running but my script is still executing!")
    self.loadUrlSignal.connect(self.loadUrlSlot)
    
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
  def webService(projectName):
      jsonData = request.json['jsonData']
      print (jsonData)
      #WebService.__parent.loadUrlSignal.emit()
      #return WebView().loadPage1(jsonData)
      #return WebForm.interact1(jsonData)
      #return WebService.execute(jsonData)
      

# create the dialog for zoom to point
class WebView(QWebEngineView):
    
    loadUrlSignal = pyqtSignal()

    def __init__(self, parent = None): 
        super().__init__()
        #super(progress, self).__init__(parent)
        print("webview __init__")
        """
        self.thread = WebService(self)
        
        self.thread.start()

        #wf = WebForm()
        #wf.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/etc/docroot/index.html"))
        #wf.show()
        #WebForm.interact({})
        self.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/etc/docroot/index.html"))
        self.show()
        """
    def startServer(self):
        self.thread = WebService(self)
        
        self.thread.start()

        print("The server is running but my script is still executing!")
        self.loadUrlSignal.connect(self.loadUrlSlot)
        
    @pyqtSlot()
    def loadUrlSlot(self):
        print("loadUrlSlot")

    def loadPage(self):
        self.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/etc/docroot/index.html"))
        self.show()

    def loadPage1(self, jsonData):
        webView = WebView()
        print("ok")
        webView.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/index.html"))
        #self.show()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    webView = WebView()
    webView.startServer()
    webView.loadPage()
    sys.exit(app.exec_())
