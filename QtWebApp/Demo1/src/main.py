"""
//#include <QCoreApplication>
#include <QApplication>
#include <QDir>
#include <QWebEngineView>
#include "httplistener.h"
#include "templatecache.h"
#include "httpsessionstore.h"
#include "staticfilecontroller.h"
#include "filelogger.h"
#include "requestmapper.h"
#include "webform.h"
"""

import os, sys

from PyQt5.QtCore import (QSettings, QFile, QFileInfo, QDir, qDebug, qWarning)
#pyqtSignal, QByteArray, QDataStream, QIODevice, QThread, , , , , , qWarning, qFatal) 
from PyQt5.QtWidgets import (QApplication)
#, QDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout) 
#from PyQt5.QtNetwork import (QHostAddress, QNetworkInterface, QTcpServer, QTcpSocket) 

#lib_path = os.path.abspath('../QtWebApp')
lib_path_template = os.path.abspath('../../QtWebApp/templateengine')
sys.path.append(lib_path_template)
lib_path_http = os.path.abspath('../../QtWebApp/httpserver')
sys.path.append(lib_path_http)

from TemplateCache import *
from HttpSessionStore import *
from StaticFileController import *
from HttpListener import *
from RequestMapper import *
#from WebService import *

"""
#Cache for template files
TemplateCache* templateCache

#Storage for session cookies
HttpSessionStore* sessionStore

#Controller for static files
StaticFileController* staticFileController

#Redirects log messages to a file
FileLogger* logger
"""

#app = None

class QtWebApp:

    #Search the configuration file
    @staticmethod
    def searchConfigFile():
        #binDir = QCoreApplication.applicationDirPath()
        #appName = QCoreApplication.applicationName()
        binDir = QApplication.applicationDirPath()
        binDir = QFileInfo(".").absolutePath()
        appName = QApplication.applicationName()
        fileName = appName + ".ini"

        SEARCH_LIST = ( 
            binDir,
            binDir + "/etc",
            binDir + "/../etc",
            binDir + "/../../etc", #for development without shadow build
            binDir + "/../" + appName + "/etc", #for development with shadow build
            binDir + "/../../" + appName + "/etc", #for development with shadow build
            binDir + "/../../../" + appName + "/etc", #for development with shadow build
            binDir + "/../../../../" + appName + "/etc", #for development with shadow build
            binDir + "/../../../../../" + appName + "/etc", #for development with shadow build
            QDir.rootPath() + "etc/opt",
            QDir.rootPath() + "etc"
        )

        for dir in SEARCH_LIST:
            file = QFile(dir + "/" + fileName)
            if file.exists():
                #found
                fileName = QDir(file.fileName()).canonicalPath()
                #qDebug("Using config file %s", qPrintable(fileName))
                qDebug("Using config file %s" % (fileName))
                return fileName

        #not found
        for dir in SEARCH_LIST:
            qWarning("%s/%s not found" % (dir, fileName))
            #qWarning("%s/%s not found", qPrintable(dir), qPrintable(fileName))
        #qFatal("Cannot find config file %s", qPrintable(fileName))
        qFatal("Cannot find config file %s" % (fileName))
        return 0

    @staticmethod
    def main(args):
        import sys
        #global app
        app = QApplication(sys.argv)

        #app = QCoreApplication app(sys.argv)
        app.setApplicationName("Demo1")
        app.setOrganizationName("Butterfly")

        #Find the configuration file
        configFileName = QtWebApp.searchConfigFile()

        #Configure logging into a file
        """
        logSettings = QSettings(configFileName, QSettings.IniFormat, app)
        logSettings.beginGroup("logging")
        logger = FileLogger(logSettings, 10000, app)
        logger.installMsgHandler()
        """

        #Configure template loader and cache
        templateSettings = QSettings(configFileName, QSettings.IniFormat, app)
        templateSettings.beginGroup("templates")
        templateCache = TemplateCache(templateSettings, app)

        #Configure session store
        sessionSettings = QSettings(configFileName, QSettings.IniFormat, app)
        sessionSettings.beginGroup("sessions")
        sessionStore  = HttpSessionStore(sessionSettings, app)

        #Configure static file controller
        fileSettings = QSettings(configFileName, QSettings.IniFormat, app)
        fileSettings.beginGroup("docroot")
        staticFileController = StaticFileController(fileSettings, app)

        #Configure and start the TCP listener
        listenerSettings = QSettings(configFileName, QSettings.IniFormat, app)
        listenerSettings.beginGroup("listener")
        HttpListener(listenerSettings, RequestMapper(app), app)

        qWarning("Application has started")

        sys.exit(app.exec_())

        qWarning("Application has stopped")
        #WebService.start(os.getcwd())
        #sys.exit(app.exec_())

QtWebApp.main("")

"""
if __name__ == '__main__':
"""