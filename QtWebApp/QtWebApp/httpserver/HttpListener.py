#include <QTcpServer>
#include <QSettings>
#include <QBasicTimer>
#include "httpglobal.h"
#include "httpconnectionhandler.h"
#include "httpconnectionhandlerpool.h"
#include "httprequesthandler.h"

"""
  Listens for incoming TCP connections and and passes all incoming HTTP requests to your implementation of HttpRequestHandler,
  which processes the request and generates the response (usually a HTML document).
  <p>
  Example for the required settings in the config file:
  <code><pre>
  ;host=192.168.0.100
  port=8080
  minThreads=1
  maxThreads=10
  cleanupInterval=1000
  readTimeout=60000
  ;sslKeyFile=ssl/my.key
  ;sslCertFile=ssl/my.cert
  maxRequestSize=16000
  maxMultiPartSize=1000000
  </pre></code>
  The optional host parameter binds the listener to one network interface.
  The listener handles all network interfaces if no host is configured.
  The port number specifies the incoming TCP port that this listener listens to.
  @see HttpConnectionHandlerPool for description of config settings minThreads, maxThreads, cleanupInterval and ssl settings
  @see HttpConnectionHandler for description of the readTimeout
  @see HttpRequest for description of config settings maxRequestSize and maxMultiPartSize
"""
#include "httplistener.h"
#include "httpconnectionhandler.h"
#include "httpconnectionhandlerpool.h"
#include <QCoreApplication>
from PyQt5.QtCore import (pyqtSignal, qDebug)
from PyQt5.QtNetwork import (QTcpServer, QHostAddress)
#from sip import (voidptr)

from HttpConnectionHandlerPool import *

class HttpListener(QTcpServer):
    """
      Sent to the connection handler to process a new incoming connection.
      @param socketDescriptor references the accepted connection.
    """
    #void handleConnection(tSocketDescriptor socketDescriptor);
    #handleConnection = pyqtSignal(voidptr)
    handleConnection = pyqtSignal(int)
    
    """
      Constructor.
      Creates a connection pool and starts listening on the configured host and port.
      @param settings Configuration settings for the HTTP server. Must not be 0.
      @param requestHandler Processes each received HTTP request, usually by dispatching to controller classes.
      @param parent Parent object.
      @warning Ensure to close or delete the listener before deleting the request handler.
    """
    def __init__(self, settings, requestHandler, parent = None):
        super(HttpListener, self).__init__(parent)
        #Q_ASSERT(settings != 0)
        #Q_ASSERT(requestHandler != 0)
        self.pool = None
        self.settings = settings
        self.requestHandler = requestHandler

        #Reqister type of socketDescriptor for signal/slot handling
        #qRegisterMetaType<tSocketDescriptor>("tSocketDescriptor")
        #Start listening

        self.listen()

    #Destructor
    def __del__(self):
        self.close()
        qDebug("HttpListener: destroyed")

    def listen(self):
        if (not self.pool):
            self.pool = HttpConnectionHandlerPool(self.settings, self.requestHandler)
        host = self.settings.value("host")
        port = int(self.settings.value("port"))
        super().listen(QHostAddress.Any if not host else QHostAddress(host), port)
        #QTcpServer.listen(QHostAddress.Any if host.isEmpty() else QHostAddress(host), port)
        #QTcpServer.listen(host.isEmpty() ? QHostAddress.Any : QHostAddress(host), port)
        if (not super().isListening()):
            qCritical("HttpListener: Cannot bind on port %i: %s" % (port, errorString()))
        else:
            qDebug("HttpListener: Listening on port %i" % (port))

    """
     Closes the listener, waits until all pending requests are processed,
     then closes the connection pool.
    """
    def close(self):
        super().close()
        #QTcpServer.close()
        qDebug("HttpListener: closed")
        if (self.pool):
            del self.pool
            self.pool = None

    def incomingConnection(self, socketDescriptor):
        #ifdef SUPERVERBOSE
        qDebug("HttpListener: New connection")
        #endif

        freeHandler = None
        if (self.pool):
            freeHandler = self.pool.getConnectionHandler()

        #Let the handler process the new connection.
        if (freeHandler):
            #The descriptor is passed via signal/slot because the handler lives in another
            #thread and cannot open the socket when directly called by another thread.

            #connect(this, SIGNAL(handleConnection(tSocketDescriptor)), freeHandler, SLOT(handleConnection(tSocketDescriptor)))
            #emit handleConnection(socketDescriptor)
            #disconnect(this, SIGNAL(handleConnection(tSocketDescriptor)), freeHandler, SLOT(handleConnection(tSocketDescriptor)))

            self.handleConnection.connect(freeHandler.handleConnection)
            self.handleConnection.emit(socketDescriptor)
            self.handleConnection.disconnect(freeHandler.handleConnection)
        else:
            #Reject the connection
            qDebug("HttpListener: Too many incoming connections")
            socket = QTcpSocket(self)
            socket.setSocketDescriptor(socketDescriptor)
            socket.disconnected.connect(socket.deleteLater)
            socket.write("HTTP/1.1 503 too many connections\r\nConnection: close\r\n\r\nToo many connections\r\n")
            socket.disconnectFromHost()
