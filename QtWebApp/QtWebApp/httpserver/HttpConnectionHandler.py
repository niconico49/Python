#ifndef QT_NO_OPENSSL
   #include <QSslConfiguration>
#endif
#include <QTcpSocket>
#include <QSettings>
#include <QTimer>
#include <QThread>
#include "httpglobal.h"
#include "httprequest.h"
#include "httprequesthandler.h"

#Alias type definition, for compatibility to different Qt versions
"""
#if QT_VERSION >= 0x050000
typedef qintptr tSocketDescriptor;
#else
typedef int tSocketDescriptor;
#endif
"""
#Alias for QSslConfiguration if OpenSSL is not supported
#ifdef QT_NO_OPENSSL
  #define QSslConfiguration QObject
#endif
from PyQt5.QtCore import (QThread, pyqtSlot, QTimer, qDebug, qCritical)
from PyQt5.QtNetwork import (QTcpSocket)

from HttpRequest import *
from HttpResponse import *
#include "httpconnectionhandler.h"
#include "httpresponse.h"
"""
  The connection handler accepts incoming connections and dispatches incoming requests to to a
  request mapper. Since HTTP clients can send multiple requests before waiting for the response,
  the incoming requests are queued and processed one after the other.
  <p>
  Example for the required configuration settings:
  <code><pre>
  readTimeout=60000
  maxRequestSize=16000
  maxMultiPartSize=1000000
  </pre></code>
  <p>
  The readTimeout value defines the maximum time to wait for a complete HTTP request.
  @see HttpRequest for description of config settings maxRequestSize and maxMultiPartSize.
"""
class HttpConnectionHandler(QThread):
    """
      Constructor.
      @param settings Configuration settings of the HTTP webserver
      @param requestHandler Handler that will process each incoming HTTP request
      @param sslConfiguration SSL (HTTPS) will be used if not NULL
    """
    def __init__(self, settings, requestHandler, sslConfiguration = None):
        super(HttpConnectionHandler, self).__init__()
        #Q_ASSERT(settings != 0)
        #Q_ASSERT(requestHandler != 0)
        self.settings = settings
        self.requestHandler = requestHandler
        self.sslConfiguration = sslConfiguration
        self.currentRequest = 0
        self.busy = False
        self.readTimer = QTimer()

        #Create TCP or SSL socket
        self.createSocket()

        #execute signals in my own thread
        self.moveToThread(self)
        self.socket.moveToThread(self)
        self.readTimer.moveToThread(self)

        #Connect signals
        #connect(self.socket, SIGNAL(readyRead()), SLOT(read()))
        #connect(self.socket, SIGNAL(disconnected()), SLOT(disconnected()))
        #connect(self.&readTimer, SIGNAL(timeout()), SLOT(readTimeout()))
        self.socket.readyRead.connect(self.read)
        self.socket.disconnected.connect(self.disconnected)
        self.readTimer.timeout.connect(self.readTimeout)
        self.readTimer.setSingleShot(True)

        qDebug("HttpConnectionHandler ({0}): constructed".format(self))
        self.start()

    #Destructor
    def __del__(self):
        self.quit()
        self.wait()
        qDebug("HttpConnectionHandler ({0}): destroyed".format(self))

    def createSocket(self):
        #If SSL is supported and configured, then create an instance of QSslSocket
        #ifndef QT_NO_OPENSSL
        if (self.sslConfiguration):
            sslSocket = QSslSocket()
            sslSocket.setSslConfiguration(self.sslConfiguration)
            self.socket = sslSocket
            qDebug("HttpConnectionHandler ({0}): SSL is enabled".format(self))
            return
        #endif
        #else create an instance of QTcpSocket
        self.socket = QTcpSocket()

    def run(self):
        qDebug("HttpConnectionHandler ({0}): thread started".format(self))
        try:
            self.exec()
        except:
            qCritical("HttpConnectionHandler ({0}): an uncatched exception occured in the thread".format(self))
            import sys
            #(type, value, traceback) = sys.exc_info()
            #sys.excepthook(type, value, traceback)
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            print(sys.exc_info()[2])
            
        self.socket.close()
        del self.socket
        self.readTimer.stop()
        qDebug("HttpConnectionHandler ({0}): thread stopped".format(self))

    """
      Received from the listener, when the handler shall start processing a new connection.
      @param socketDescriptor references the accepted connection.
    """
    @pyqtSlot(int)
    def handleConnection(self, socketDescriptor):
        qDebug("HttpConnectionHandler ({0}): handle new connection".format(self))
        self.busy = True
        #Q_ASSERT(socket.isOpen() == False) #if not, then the handler is already busy

        #UGLY workaround - we need to clear writebuffer before reusing this socket
        #https://bugreports.qt-project.org/browse/QTBUG-28914
        self.socket.connectToHost("", 0)
        self.socket.abort()

        if (not self.socket.setSocketDescriptor(socketDescriptor)):
            qCritical("HttpConnectionHandler ({0}): cannot initialize socket: {1}".format(self, self.socket.errorString()))
            return

        #ifndef QT_NO_OPENSSL
        #Switch on encryption, if SSL is configured
        if (self.sslConfiguration):
            qDebug("HttpConnectionHandler ({0}): Starting encryption".format(self))
            #((QSslSocket*)socket).startServerEncryption()
            self.socket.startServerEncryption()
        #endif

        #Start timer for read timeout
        readTimeout = int(self.settings.value("readTimeout", 10000))
        self.readTimer.start(readTimeout)
        #delete previous request
        del self.currentRequest
        self.currentRequest = 0

    #Returns true, if this handler is in use.
    def isBusy(self):
        return self.busy

    #Mark this handler as busy
    def setBusy(self):
        self.busy = True

    #Received from the socket when a read-timeout occured
    @pyqtSlot()
    def readTimeout(self):
        qDebug("HttpConnectionHandler ({0}): read timeout occured".format(self))

        #Commented out because QWebView cannot handle this.
        #socket->write("HTTP/1.1 408 request timeout\r\nConnection: close\r\n\r\n408 request timeout\r\n")

        self.socket.flush()
        self.socket.disconnectFromHost()
        del self.currentRequest
        self.currentRequest = 0

    #Received from the socket when a connection has been closed
    @pyqtSlot()
    def disconnected(self):
        qDebug("HttpConnectionHandler ({0}): disconnected".format(self))
        self.socket.close()
        self.readTimer.stop()
        self.busy = False

    #Received from the socket when incoming data can be read
    @pyqtSlot()
    def read(self):
        #The loop adds support for HTTP pipelinig
        while (self.socket.bytesAvailable()):
            #ifdef SUPERVERBOSE
            qDebug("HttpConnectionHandler ({0}): read input".format(self))
            #endif

            #Create new HttpRequest object if necessary
            if (not self.currentRequest):
                self.currentRequest = HttpRequest(self.settings)

            #Collect data for the request object
            while (self.socket.bytesAvailable() and self.currentRequest.getStatus() != RequestStatus.complete and self.currentRequest.getStatus() != RequestStatus.abort):
                self.currentRequest.readFromSocket(self.socket)
                if (self.currentRequest.getStatus() == RequestStatus.waitForBody):
                    #Restart timer for read timeout, otherwise it would
                    #expire during large file uploads.
                    readTimeout = int(self.settings.value("readTimeout", 10000))
                    self.readTimer.start(readTimeout)

            #If the request is aborted, return error message and close the connection
            if (self.currentRequest.getStatus() == RequestStatus.abort):
                self.socket.write(b"HTTP/1.1 413 entity too large\r\nConnection: close\r\n\r\n413 Entity too large\r\n")
                self.socket.flush()
                self.socket.disconnectFromHost()
                del self.currentRequest
                self.currentRequest = 0
                return

            #If the request is complete, let the request mapper dispatch it
            if (self.currentRequest.getStatus() == RequestStatus.complete):
                self.readTimer.stop()
                qDebug("HttpConnectionHandler ({0}): received request".format(self))

                #Copy the Connection:close header to the response
                response = HttpResponse(self.socket)
                #closeConnection = QString.compare(self.currentRequest.getHeader("Connection"), "close", Qt.CaseInsensitive) == 0
                closeConnection = self.currentRequest.getHeader(b"Connection")[0].data().lower() == "close"
                if (closeConnection):
                    response.setHeader("Connection", "close")

                #In case of HTTP 1.0 protocol add the Connection:close header.
                #This ensures that the HttpResponse does not activate chunked mode, which is not spported by HTTP 1.0.
                else:
                    #http1_0 = QString.compare(self.currentRequest.getVersion(), "HTTP/1.0", Qt.CaseInsensitive) == 0
                    http1_0 = self.currentRequest.getVersion().data().lower() == "HTTP/1.0"
                    if (http1_0):
                        closeConnection = True
                        response.setHeader("Connection", "close")

                #Call the request mapper
                try:
                    self.requestHandler.service(self.currentRequest, response)
                except:
                    qCritical("HttpConnectionHandler ({0}): An uncatched exception occured in the request handler".format(self))
                    import sys
                    #(type, value, traceback) = sys.exc_info()
                    #sys.excepthook(type, value, traceback)
                    print(sys.exc_info()[0])
                    print(sys.exc_info()[1])
                    print(sys.exc_info()[2])

                #Finalize sending the response if not already done
                if (not response.hasSentLastPart()):
                    response.write(QByteArray(), True)

                qDebug("HttpConnectionHandler ({0}): finished request".format(self))

                #Find out whether the connection must be closed
                if (not closeConnection):
                    #Maybe the request handler or mapper added a Connection:close header in the meantime
                    #closeResponse = QString.compare(response.getHeaders().value("Connection"), "close", Qt.CaseInsensitive) == 0
                    closeResponse = b"Connection" in response.getHeaders().keys() and response.getHeaders()[b"Connection"].lower() == "close"
                    if (closeResponse == True):
                        closeConnection = True
                    else:
                        #If we have no Content-Length header and did not use chunked mode, then we have to close the
                        #connection to tell the HTTP client that the end of the response has been reached.
                        #hasContentLength = response.getHeaders().contains("Content-Length")
                        hasContentLength = b"Content-Length" in response.getHeaders().keys()
                        if (not hasContentLength):
                            #hasChunkedMode = QString.compare(response.getHeaders().value("Transfer-Encoding"), "chunked", Qt.CaseInsensitive) == 0
                            hasChunkedMode = b"Transfer-Encoding" in response.getHeaders().keys() and response.getHeaders()[b"Transfer-Encoding"].lower() == "chunked"
                            if (not hasChunkedMode):
                                closeConnection = True

                #Close the connection or prepare for the next request on the same connection.
                if (closeConnection):
                    self.socket.flush()
                    self.socket.disconnectFromHost()
                else:
                    #Start timer for next request
                    readTimeout = int(self.settings.value("readTimeout", 10000))
                    self.readTimer.start(readTimeout)
                del self.currentRequest
                self.currentRequest = 0
