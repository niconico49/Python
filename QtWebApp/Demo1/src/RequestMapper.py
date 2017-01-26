#include "httprequesthandler.h"
#include "controller/webservicecontroller.h"
#include "abstractnoscriptobject.h"


#include <QCoreApplication>
#include "requestmapper.h"
#include "filelogger.h"
#include "staticfilecontroller.h"
#include "controller/webservicecontroller.h"
#include "controller/dumpcontroller.h"
#include "controller/templatecontroller.h"
#include "controller/formcontroller.h"
#include "controller/fileuploadcontroller.h"
#include "controller/sessioncontroller.h"

#include "abstractnoscriptobject.h"
#include "webform.h"

from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QUrl) 
from PyQt5.QtWebChannel import (QWebChannel)
#from PyQt5.QtGui import (QCloseEvent)
#Redirects log messages to a file
#extern FileLogger* logger;

#Controller for static files
from StaticFileController import *
from WebForm import *
from AbstractNoScriptObject import *

import os, sys
lib_path_controller = os.path.abspath('controller')
sys.path.append(lib_path_controller)

from WebServiceController import *

lib_path_controller = os.path.abspath('controller')
sys.path.append(lib_path_controller)

"""
  The request mapper dispatches incoming HTTP requests to controller classes
  depending on the requested path.
"""
class RequestMapper(HttpRequestHandler):

    wake = pyqtSignal(str)

    """
      Constructor.
      @param parent Parent object
    """
    def __init__(self, parent = None):
        super(RequestMapper, self).__init__(parent)

        qDebug("RequestMapper: created")

        #QTextStream(stdout) << QDir::currentPath() << "\r\n"

        self.webServiceController = WebServiceController()
        self.webServiceController.loadUrl.connect(self.loadUrl)
        self.wake.connect(self.webServiceController.wake)

        self.qWebEngineView = WebForm()
        self.qWebEngineView.closeEvent.connect(self.closeApp)
        self.qWebEngineView.load(QUrl("file:///%s/etc/docroot/index.html" % (QFileInfo(".").absolutePath())))
        self.qWebEngineView.show()
        #connect(self.webServiceController, &WebServiceController::loadUrl, this, &RequestMapper::loadUrl)
        #connect(self, &RequestMapper::wake, webServiceController, &WebServiceController::wake)
        #----connect(self.webServiceController, &WebServiceController::loadUrl, this, &RequestMapper::loadUrl, Qt::BlockingQueuedConnection)

    def __del__(self):
        qDebug("RequestMapper: deleted")

    """
      Dispatch incoming HTTP requests to different controllers depending on the URL.
      @param request The received HTTP request
      @param response Must be used to return the response
    """
    def service(self, request, response):
        #QByteArray path = request.getPath()
        #path = request.getPath()
        path = request.getPath().data().decode('ascii')
        #qDebug("RequestMapper: path=%s" % (path.data().decode('ascii')))
        qDebug("RequestMapper: path=%s" % (path))

        #For the following pathes, each request gets its own new instance of the related controller.

        if (path.startswith("/webresources/api/execute")):
            #WebServiceController().service(request, response);
            self.webServiceController.service(request, response);
        elif (path.startswith("/dump")):
            DumpController().service(request, response)
        elif (path.startswith("/template")):
            TemplateController().service(request, response)
        elif (path.startswith("/form")):
            FormController().service(request, response)
        elif (path.startswith("/file")):
            FileUploadController().service(request, response)
        elif (path.startswith("/session")):
            SessionController().service(request, response)
        #All other pathes are mapped to the static file controller.
        #In this case, a single instance is used for multiple requests.
        else:
            staticFileController.service(request, response)

        qDebug("RequestMapper: finished request")

        #Clear the log buffer
        #if (logger):
        #    logger.clear()

    def loadUrl(self, url, bodyJson):
        self.channel = QWebChannel()

        self.qWebEngineView1 = WebForm()

        self.qWebEngineView1.closeEvent.connect(self.closeEvent)
        #connect(qWebEngineView, &WebForm::closeEvent, self, &RequestMapper::closeEvent)
        self.qWebEngineView1.page().setWebChannel(self.channel)
        self.channel.registerObject("widget", self.qWebEngineView1)

        #QTextStream(stdout) << bodyJson << "\r\n"
        #AbstractNoScriptObject* abstractNoScriptObject = AbstractNoScriptObject::getInstance(bodyJson)
        self.abstractNoScriptObject = AbstractNoScriptObject.getInstance(bodyJson)
        self.channel.registerObject("AbstractNoScriptObject", self.abstractNoScriptObject)

        self.channel.registerObject("ComponentDevelopment", self.abstractNoScriptObject.getComponentDevelopment())
        self.channel.registerObject("ComponentRequestResponse", self.abstractNoScriptObject.getComponentRequestResponse())

        #self.qWebEngineView1.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/index.html"))
        #QTextStream(stdout) << url << "\r\n"
        #self.qWebEngineView1.load(QUrl(url))
        #self.qWebEngineView1.load(QUrl("file:///C:/Users/Nick/Desktop/usb/QtWebApp/Demo1/index.html"))
        self.qWebEngineView1.load(QUrl(url))
        #self.qWebEngineView1.show()

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, event):
        #this.close()
        print("closeEvent")
        result = self.abstractNoScriptObject.getComponentRequestResponse().getResponse()
        print("result: ", result)
        #QTextStream(stdout) << "c++result = " << result << "\r\n"
        event.accept()
        self.wake.emit(result)
        #emit wake(result)

    @pyqtSlot()
    def closeApp(self, event):
        #QTextStream(stdout) << "closeApp" << "\r\n"
        print("closeApp")
        event.accept()
        QApplication.exit()
        #QCoreApplication.quit()
