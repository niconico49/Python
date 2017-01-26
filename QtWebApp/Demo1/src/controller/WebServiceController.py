#include "httprequest.h"
#include "httpresponse.h"
#include "httprequesthandler.h"
#include <QtWebEngineWidgets>

#This controller dumps the received HTTP request in the response.

#include "webservicecontroller.h"
#include <QVariant>
#include <QDateTime>

#include <QWebChannel>
#include <QWebEngineView>
#include "../abstractnoscriptobject.h"
#include "../htmlpage.h"
#include "../webform.h"

from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QWaitCondition, QFileInfo, QMutex)
#, QUrl) 

from HttpRequestHandler import *

class WebServiceController(HttpRequestHandler):
    loadUrl = pyqtSignal(str, str)

    def __init__(self):
        super(WebServiceController, self).__init__()

    @pyqtSlot(str)
    def wake(self, result): 
        print("wake")
        self.waiter.wakeAll()
        self.result = result

    #Generates the response 
    def service(self, request, response):
        response.setHeader("Access-Control-Allow-Origin", "*")
        response.setHeader("Access-Control-Allow-Methods", "GET,POST")
        response.setHeader("Access-Control-Allow-Headers", "origin, x-requested-with, content-type")
        """
        response.setHeader("Content-Type", "text/html; charset=ISO-8859-1")
        response.setCookie(HttpCookie("firstCookie","hello",600))
        response.setCookie(HttpCookie("secondCookie","world",600))
        """
        bodyJson = request.getBody().data().decode('ascii')

        print("bodyJson: ", bodyJson)
        mutex = QMutex()
        mutex.lock()
        #url = "file:///%1/Demo1/index.html" % (QFileInfo(".").absolutePath())
        url = "file:///{0}/index.html".format(QFileInfo(".").absolutePath())
        self.loadUrl.emit(url, bodyJson)
        self.waiter = QWaitCondition()
        self.waiter.wait(mutex)
        #QTextStream(stdout) << "after wait" << "\r\n"
        mutex.unlock()
        #QTextStream(stdout) << "after unlock" << "\r\n"

        #QTextStream(stdout) << QByteArray::fromHex(self.result.toLatin1()) << "\r\n"
        #QString result = abstractNoScriptObject.getComponentRequestResponse().getResponse()
        #response.write(QByteArray.fromHex(self.result.toLatin1()))
        #QByteArray array (self.result.toStdString().c_str())
        print("self.result: ", self.result)
        response.write(self.result)
        #response.write(self.result.toStdString().c_str())

        #http://stackoverflow.com/questions/9777911/how-do-i-create-a-window-in-different-qt-threads
