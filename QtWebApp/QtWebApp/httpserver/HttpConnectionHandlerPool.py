#include <QList>
#include <QTimer>
#include <QObject>
#include <QMutex>
#include "httpglobal.h"
#include "httpconnectionhandler.h"

"""
  Pool of http connection handlers. The size of the pool grows and
  shrinks on demand.
  <p>
  Example for the required configuration settings:
  <code><pre>
  minThreads=4
  maxThreads=100
  cleanupInterval=60000
  readTimeout=60000
  ;sslKeyFile=ssl/my.key
  ;sslCertFile=ssl/my.cert
  maxRequestSize=16000
  maxMultiPartSize=1000000
  </pre></code>
  After server start, the size of the thread pool is always 0. Threads
  are started on demand when requests come in. The cleanup timer reduces
  the number of idle threads slowly by closing one thread in each interval.
  But the configured minimum number of threads are kept running.
  <p>
  For SSL support, you need an OpenSSL certificate file and a key file.
  Both can be created with the command
  <code><pre>
      openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout my.key -out my.cert
  </pre></code>
  <p>
  Visit http://slproweb.com/products/Win32OpenSSL.html to download the Light version of OpenSSL for Windows.
  <p>
  Please note that a listener with SSL settings can only handle HTTPS protocol. To
  support both HTTP and HTTPS simultaneously, you need to start two listeners on different ports -
  one with SLL and one without SSL.
  @see HttpConnectionHandler for description of the readTimeout
  @see HttpRequest for description of config settings maxRequestSize and maxMultiPartSize
"""

#ifndef QT_NO_OPENSSL
    #include <QSslSocket>
    #include <QSslKey>
    #include <QSslCertificate>
    #include <QSslConfiguration>
#endif
#include <QDir>
#include "httpconnectionhandlerpool.h"
from PyQt5.QtCore import (QObject, pyqtSlot, QMutex, QTimer)
from HttpConnectionHandler import *

class HttpConnectionHandlerPool(QObject):
    """
      Constructor.
      @param settings Configuration settings for the HTTP server. Must not be 0.
      @param requestHandler The handler that will process each received HTTP request.
      @warning The requestMapper gets deleted by the destructor of this pool
    """
    def __init__(self, settings, requestHandler):
        #Q_ASSERT(settings != 0)
        self.settings = settings
        self.requestHandler = requestHandler
        self.sslConfiguration = None
        self.pool = []
        self.loadSslConfig()
        self.mutex = QMutex()
        self.cleanupTimer = QTimer()
        self.cleanupTimer.start(int(settings.value("cleanupInterval", 1000)))
        self.cleanupTimer.timeout.connect(self.cleanup)
        #connect(&cleanupTimer, SIGNAL(timeout()), SLOT(cleanup()))

    #Destructor
    def __del__(self):
        #delete all connection handlers and wait until their threads are closed
        for handler in self.pool:
            del handler
            del self.sslConfiguration
            qDebug("HttpConnectionHandlerPool (%p): destroyed" % (self))

    #Get a free connection handler, or 0 if not available.
    def getConnectionHandler(self):
        freeHandler = None
        self.mutex.lock()
        #find a free handler in pool
        for handler in self.pool:
            if (not handler.isBusy()):
                freeHandler = handler
                freeHandler.setBusy()
                break
        #create a new handler, if necessary
        if (not freeHandler):
            maxConnectionHandlers = int(self.settings.value("maxThreads", 100))
            if (len(self.pool) < maxConnectionHandlers):
                freeHandler = HttpConnectionHandler(self.settings, self.requestHandler, self.sslConfiguration)
                freeHandler.setBusy()
                self.pool.append(freeHandler)
        self.mutex.unlock()
        return freeHandler

    @pyqtSlot()
    def cleanup(self):
        maxIdleHandlers = int(self.settings.value("minThreads", 1))
        idleCounter = 0
        self.mutex.lock()
        for handler in self.pool:
            if (not handler.isBusy()):
                if (++idleCounter > maxIdleHandlers):
                    del handler
                    #self.pool.removeOne(handler)
                    qDebug("HttpConnectionHandlerPool: Removed connection handler (%p), pool size is now %i" % (handler, pool.size()))
                    break #remove only one handler in each interval
        self.mutex.unlock()

    def loadSslConfig(self):
        #If certificate and key files are configured, then load them
        sslKeyFileName = self.settings.value("sslKeyFile", "")
        sslCertFileName = self.settings.value("sslCertFile", "")
        if (sslKeyFileName and sslCertFileName):
            #ifdef QT_NO_OPENSSL
                qWarning("HttpConnectionHandlerPool: SSL is not supported")
            #else
                #Convert relative fileNames to absolute, based on the directory of the config file.
                configFile = QFileInfo(self.settings.fileName())
                #ifdef Q_OS_WIN32
                if (QDir.isRelativePath(sslKeyFileName) and self.settings.format() != QSettings.NativeFormat):
                #else
                #if (QDir.isRelativePath(sslKeyFileName))
                #endif
                    sslKeyFileName = QFileInfo(configFile.absolutePath(), sslKeyFileName).absoluteFilePath()
                #ifdef Q_OS_WIN32
                if (QDir.isRelativePath(sslCertFileName) and self.settings.format() != QSettings.NativeFormat):
                #else
                #if (QDir.isRelativePath(sslCertFileName))
                #endif
                    sslCertFileName = QFileInfo(configFile.absolutePath(), sslCertFileName).absoluteFilePath()

                #Load the SSL certificate
                certFile =QFile(sslCertFileName)
                if (not certFile.open(QIODevice.ReadOnly)):
                    qCritical("HttpConnectionHandlerPool: cannot open sslCertFile %s" % (sslCertFileName))
                    return
                certificate = QSslCertificate(certFile, QSsl.Pem)
                certFile.close()

                #Load the key file
                keyFile = QFile(sslKeyFileName)
                if (not keyFile.open(QIODevice.ReadOnly)):
                    qCritical("HttpConnectionHandlerPool: cannot open sslKeyFile %s" % (sslKeyFileName))
                    return
                sslKey = QSslKey(keyFile, QSsl.Rsa, QSsl.Pem)
                keyFile.close()

                #Create the SSL configuration
                self.sslConfiguration = QSslConfiguration()
                self.sslConfiguration.setLocalCertificate(certificate)
                self.sslConfiguration.setPrivateKey(sslKey)
                self.sslConfiguration.setPeerVerifyMode(QSslSocket.VerifyNone)
                self.sslConfiguration.setProtocol(QSsl.TlsV1SslV3)

                qDebug("HttpConnectionHandlerPool: SSL settings loaded")
            #endif
