#include <QMap>
#include <QString>
#include <QTcpSocket>
#include "httpglobal.h"
#include "httpcookie.h"

"""
  This object represents a HTTP response, used to return something to the web client.
  <p>
  <code><pre>
    response.setStatus(200,"OK"); // optional, because this is the default
    response.writeBody("Hello");
    response.writeBody("World!",true);
  </pre></code>
  <p>
  Example how to return an error:
  <code><pre>
    response.setStatus(500,"server error");
    response.write("The request cannot be processed because the servers is broken",true);
  </pre></code>
  <p>
  In case of large responses (e.g. file downloads), a Content-Length header should be set
  before calling write(). Web Browsers use that information to display a progress bar.
"""
#Request headers
#QMap<QByteArray,QByteArray> headers;

#Cookies
#QMap<QByteArray,HttpCookie> cookies;

#include "httpresponse.h"
from PyQt5.QtCore import (QByteArray)

class HttpResponse():
    """
      Constructor.
      @param socket used to write the response
    """
    def __init__(self, socket):
        self.socket = socket
        self.statusCode = 200
        self.statusText = "OK"
        self.sentHeaders = False
        self.sentLastPart = False
        self.chunkedMode = False
        self.headers = {}
        self.cookies = {}

    """
      Set a HTTP response header.
      You must call this method before the first write().
      @param name name of the header
      @param value value of the header
    """
    def setHeader(self, name, value):
        #Q_ASSERT(self.sentHeaders == False)
        self.headers[name] = value

    """
      Set a HTTP response header.
      You must call this method before the first write().
      @param name name of the header
      @param value value of the header
    """
    """
    def setHeader(self, name, value):
        #Q_ASSERT(self.sentHeaders == False)
        self.headers[name] = QByteArray.number(value)
    """

    #Get the map of HTTP response headers
    def getHeaders(self):
        return self.headers

    """
      Set status code and description. The default is 200,OK.
      You must call this method before the first write().
    """
    def setStatus(self, statusCode, description):
        self.statusCode = statusCode
        self.statusText = description

    #Return the status code.
    def getStatusCode(self):
        return self.statusCode

    """
      Write the response HTTP status and headers to the socket.
      Calling this method is optional, because writeBody() calls
      it automatically when required.
    """
    def writeHeaders(self):
        #Q_ASSERT(self.sentHeaders == False)
        buffer = QByteArray()
        buffer.append("HTTP/1.1 ")
        buffer.append(QByteArray.number(self.statusCode))
        buffer.append(' ')
        buffer.append(self.statusText)
        buffer.append("\r\n")
        for name in self.headers.keys():
            buffer.append(name)
            buffer.append(": ")
            buffer.append(self.headers[name])
            buffer.append("\r\n")

        for cookie in self.cookies.values():
            buffer.append("Set-Cookie: ")
            buffer.append(cookie.toByteArray())
            buffer.append("\r\n")

        buffer.append("\r\n")
        self.writeToSocket(buffer)
        self.sentHeaders = True

    #Write raw data to the socket. This method blocks until all bytes have been passed to the TCP buffer
    def writeToSocket(self, data):
        #remaining = data.size()
        #ptr = data.data()
        remaining = len(data)
        ptr = data
        while (self.socket.isOpen() and remaining > 0):
            #If the output buffer has become large, then wait until it has been sent.
            if (self.socket.bytesToWrite() > 16384):
                self.socket.waitForBytesWritten(-1)

            #written = self.socket.write(ptr, remaining)
            #written = self.socket.write(ptr)
            written = self.socket.write(QByteArray().append(ptr))
            if (written == -1):
                return False

            #ptr += written
            remaining -= written

        return True

    """
      Write body data to the socket.
      <p>
      The HTTP status line, headers and cookies are sent automatically before the body.
      <p>
      If the response contains only a single chunk (indicated by lastPart=true),
      then a Content-Length header is automatically set.
      <p>
      Chunked mode is automatically selected if there is no Content-Length header
      and also no Connection:close header.
      @param data Data bytes of the body
      @param lastPart Indicates that this is the last chunk of data and flushes the output buffer.
    """
    def write(self, data, lastPart = False):
        #Q_ASSERT(self.sentLastPart == False)

        #Send HTTP headers, if not already done (that happens only on the first call to write())
        if (self.sentHeaders == False):
            #If the whole response is generated with a single call to write(), then we know the total
            #size of the response and therefore can set the Content-Length header automatically.
            if (lastPart):
                #Automatically set the Content-Length header
                self.headers["Content-Length"] = QByteArray.number(len(data))

            #else if we will not close the connection at the end, them we must use the chunked mode.
            else:
                #connectionClose = QString.compare(self.headers["Connection"], "close", Qt.CaseInsensitive) == 0
                connectionClose = "Connection" in self.headers and self.headers["Connection"].lower() == "close"
                if (not connectionClose):
                    self.headers["Transfer-Encoding"] = "chunked"
                    self.chunkedMode = True

            self.writeHeaders()

        #Send data
        if (len(data) > 0):
            if (self.chunkedMode):
                if (len(data) > 0):
                    size = QByteArray.number(len(data), 16)
                    self.writeToSocket(size)
                    self.writeToSocket("\r\n")
                    self.writeToSocket(data)
                    self.writeToSocket("\r\n")
            else:
                self.writeToSocket(data)

        #Only for the last chunk, send the terminating marker and flush the buffer.
        if (lastPart):
            if (self.chunkedMode):
                self.writeToSocket("0\r\n\r\n")
            self.socket.flush()
            self.sentLastPart = True

    #Indicates whether the body has been sent completely (write() has been called with lastPart=true).
    def hasSentLastPart(self):
        return self.sentLastPart

    """
      Set a cookie.
      You must call this method before the first write().
    """
    def setCookie(self, cookie):
        #Q_ASSERT(self.sentHeaders == False)
        if (cookie.getName()):
            self.cookies.insert(cookie.getName(), cookie)

    #Get the map of cookies
    def getCookies(self):
        return self.cookies

    """
      Send a redirect response to the browser.
      Cannot be combined with write().
      @param url Destination URL
    """
    def redirect(self, url):
        self.setStatus(303, "See Other")
        self.setHeader("Location", url)
        self.write("Redirect", true)

    """
    Flush the output buffer (of the underlying socket).
    You normally don't need to call this method because flush is
    automatically called after HttpRequestHandler::service() returns.
    """
    def flush(self):
        self.socket.flush()

    """
    May be used to check whether the connection to the web client has been lost.
    This might be useful to cancel the generation of large or slow responses.
    """
    def isConnected(self):
        return self.socket.isOpen()
