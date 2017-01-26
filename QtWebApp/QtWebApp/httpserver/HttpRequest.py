#include <QByteArray>
#include <QHostAddress>
#include <QTcpSocket>
#include <QMap>
#include <QMultiMap>
#include <QSettings>
#include <QTemporaryFile>
#include <QUuid>
#include "httpglobal.h"

"""
  This object represents a single HTTP request. It reads the request
  from a TCP socket and provides getters for the individual parts
  of the request.
  <p>
  The follwing config settings are required:
  <code><pre>
  maxRequestSize=16000
  maxMultiPartSize=1000000
  </pre></code>
  <p>
  MaxRequestSize is the maximum size of a HTTP request. In case of
  multipart/form-data requests (also known as file-upload), the maximum
  size of the body must not exceed maxMultiPartSize.
  The body is always a little larger than the file itself.
"""
"""
    #Request headers
    QMultiMap<QByteArray, QByteArray> headers;

    #Parameters of the request
    QMultiMap<QByteArray, QByteArray> parameters;

    #Uploaded files of the request, key is the field name.
    QMap<QByteArray, QTemporaryFile*> uploadedFiles;

    #Received cookies
    QMap<QByteArray, QByteArray> cookies;
"""
#include "httprequest.h"
#include <QList>
#include <QDir>
#include "httpcookie.h"

from enum import Enum
from PyQt5.QtCore import (QTemporaryFile, qDebug, QByteArray, qWarning)
from collections import defaultdict
from collections import defaultdict

class RequestStatus(Enum):
    waitForRequest = 0
    waitForHeader = 1
    waitForBody = 2
    complete = 3
    abort = 4

class HttpRequest():
    """
      Constructor.
      @param settings Configuration settings
    """
    def __init__(self, settings):
        #Values for getStatus()
        #self.RequestStatus = Enum(waitForRequest = 0, waitForHeader = 1, waitForBody = 2, complete = 3, abort = 4)
        self.RequestStatus = RequestStatus 
        self.status = self.RequestStatus.waitForRequest
        self.currentSize = 0
        self.expectedBodySize = 0
        self.maxSize = int(settings.value("maxRequestSize", "16000"))
        self.maxMultiPartSize = int(settings.value("maxMultiPartSize", "1000000"))
        self.tempFile = QTemporaryFile()
        self.lineBuffer = QByteArray()
        self.boundary = QByteArray()
        self.headers = defaultdict(list)
        self.uploadedFiles = {}
        self.bodyData = QByteArray()

    #Destructor.
    def __del__(self):
        for key in self.uploadedFiles.keys():
            File = QTemporaryFile(self.uploadedFiles.value(key))
            file.close()
            del file

    #Sub-procedure of readFromSocket(), read the first line of a request.
    def readRequest(self, socket):
        #ifdef SUPERVERBOSE
        qDebug("HttpRequest: read request")
        #endif
        toRead = self.maxSize - self.currentSize + 1 #allow one byte more to be able to detect overflow
        self.lineBuffer.append(socket.readLine(toRead))
        self.currentSize += self.lineBuffer.size()
        if (not self.lineBuffer.contains(b'\r') and not self.lineBuffer.contains(b'\n')):
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: collecting more parts until line break")
            #endif
            return

        #newData = QByteArray(self.lineBuffer.trimmed())
        newData = self.lineBuffer.trimmed()
        self.lineBuffer.clear()
        if (newData):
            list = newData.split(' ')
            print("list: ", list)
            if (len(list) != 3 or not list[2].contains(b"HTTP")):
                qWarning("HttpRequest: received broken HTTP request, invalid first line")
                self.status = self.RequestStatus.abort
            else:
                self.method = list[0].trimmed()
                self.path = list[1]
                self.version = list[2]
                self.peerAddress = socket.peerAddress()
                self.status = self.RequestStatus.waitForHeader

    #Sub-procedure of readFromSocket(), read header lines.
    def readHeader(self, socket):
        #ifdef SUPERVERBOSE
        qDebug("HttpRequest: read header")
        #endif
        toRead = self.maxSize - self.currentSize + 1 #allow one byte more to be able to detect overflow
        self.lineBuffer.append(socket.readLine(toRead))
        self.currentSize += self.lineBuffer.size()
        if (not self.lineBuffer.contains(b'\r') or not self.lineBuffer.contains(b'\n')):
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: collecting more parts until line break")
            #endif
            return

        #newData = QByteArray(self.lineBuffer.trimmed())
        newData = self.lineBuffer.trimmed()
        self.lineBuffer.clear()
        colon = newData.indexOf(':')
        if (colon > 0):
            #Received a line with a colon - a header
            self.currentHeader = newData.left(colon)
            value = QByteArray(newData.mid(colon+1).trimmed())
            self.headers[self.currentHeader].append(value)
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: received header %s: %s" % (self.currentHeader.data(), value.data()))
            #endif
        elif (not newData.isEmpty()):
            #received another line - belongs to the previous header
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: read additional line of header")
            #endif
            #Received additional line of previous header
            if (self.headers.contains(self.currentHeader)):
                self.headers[self.currentHeader] = self.headers[self.currentHeader] + " " + newData
        else:
            #received an empty line - end of headers reached
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: headers completed")
            #endif
            #Empty line received, that means all headers have been received
            #Check for multipart/form-data
            contentType = self.headers[QByteArray(b"Content-Type")][0]
            if (contentType.startsWith(b"multipart/form-data")):
                posi = contentType.indexOf(b"boundary=")
                if (posi >= 0):
                    self.boundary = contentType.mid(posi + 9)
                    if  (self.boundary.startsWith('"') and self.boundary.endsWith('"')):
                        self.boundary = self.boundary.mid(1, self.boundary.length() - 2)
    
            contentLength = self.getHeader(b"Content-Length")[0]
            if (contentLength):
                self.expectedBodySize = int(contentLength)
            if (self.expectedBodySize == 0):
                #ifdef SUPERVERBOSE
                qDebug("HttpRequest: expect no body")
                #endif
                self.status = self.RequestStatus.complete
            elif (not self.boundary and self.expectedBodySize + self.currentSize > self.maxSize):
                qWarning("HttpRequest: expected body is too large")
                self.status = self.RequestStatus.abort
            elif (self.boundary and self.expectedBodySize > self.maxMultiPartSize):
                qWarning("HttpRequest: expected multipart body is too large")
                self.status = self.RequestStatus.abort
            else:
                #ifdef SUPERVERBOSE
                qDebug("HttpRequest: expect %i bytes body" % (self.expectedBodySize))
                #endif
                self.status = self.RequestStatus.waitForBody

    #Sub-procedure of readFromSocket(), read the request body.
    def readBody(self, socket):
        #Q_ASSERT(self.expectedBodySize != 0)
        if (not self.boundary):
            #normal body, no multipart
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: receive body")
            #endif
            toRead = self.expectedBodySize - self.bodyData.size()
            newData = QByteArray(socket.read(toRead))
            self.currentSize += newData.size()
            self.bodyData.append(newData)
            if (self.bodyData.size() >= self.expectedBodySize):
                self.status = self.RequestStatus.complete
        else:
            #multipart body, store into temp file
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: receiving multipart body")
            #endif
            if (not self.tempFile.isOpen()):
                self.tempFile.open()

            #Transfer data in 64kb blocks
            fileSize = self.tempFile.size()
            toRead = self.expectedBodySize - fileSize
            if (toRead > 65536):
                toRead = 65536

            fileSize += self.tempFile.write(socket.read(toRead))
            if (fileSize >= self.maxMultiPartSize):
                qWarning("HttpRequest: received too many multipart bytes")
                self.status = self.RequestStatus.abort
            elif (fileSize >= self.expectedBodySize):
                #ifdef SUPERVERBOSE
                qDebug("HttpRequest: received whole multipart body")
                #endif
                self.tempFile.flush()
                if (self.tempFile.error()):
                    qCritical("HttpRequest: Error writing temp file for multipart body")
                self.parseMultiPartFile()
                self.tempFile.close()
                self.status = self.RequestStatus.complete

    #Sub-procedure of readFromSocket(), extract and decode request parameters.
    def decodeRequestParams(self):
        #ifdef SUPERVERBOSE
        qDebug("HttpRequest: extract and decode request parameters")
        #endif
        #Get URL parameters
        rawParameters = QByteArray()
        questionMark = self.path.indexOf('?')
        if (questionMark >= 0):
            rawParameters = self.path.mid(questionMark + 1)
            self.path = self.path.left(questionMark)
        #Get request body parameters
        contentType = self.headers[QByteArray(b"Content-Type")][0]
        if (self.bodyData and (not contentType or contentType.startsWith(b"application/x-www-form-urlencoded"))):
            if (rawParameters):
                rawParameters.append('&')
                rawParameters.append(self.bodyData)
            else:
                rawParameters = self.bodyData

        #Split the parameters into pairs of value and name
        list = rawParameters.split('&')
        for part in list:
            equalsChar = part.indexOf('=')
            if (equalsChar >= 0):
                name = QByteArray(part.left(equalsChar).trimmed())
                value = QByteArray(part.mid(equalsChar + 1).trimmed())
                parameters.insert(self.urlDecode(name), self.urlDecode(value))
            elif (part):
                #Name without value
                parameters.insert(self.urlDecode(part), "")

    #Sub-procedure of readFromSocket(), extract cookies from headers
    def extractCookies(self):
        #ifdef SUPERVERBOSE
        qDebug("HttpRequest: extract cookies")
        #endif
        #for cookieStr in self.headers["Cookie"]:
        for cookieStr in self.headers[QByteArray(b"Cookie")]:
            list = HttpCookie.splitCSV(cookieStr)
            for part in list:
                #ifdef SUPERVERBOSE
                qDebug("HttpRequest: found cookie %s", part.data())
                #endif                // Split the part into name and value
                name = QByteArray()
                value = QByteArray()
                posi = part.indexOf('=')
                if (posi):
                    name = part.left(posi).trimmed()
                    value = part.mid(posi + 1).trimmed()
                else:
                    name = part.trimmed()
                    value = ""
                cookies.insert(name, value)
        del self.headers[QByteArray(b"Cookie")]

    """
      Read the HTTP request from a socket.
      This method is called by the connection handler repeatedly
      until the status is RequestStatus::complete or RequestStatus::abort.
      @param socket Source of the data
    """
    def readFromSocket(self, socket):
        #Q_ASSERT(self.status != complete)
        if (self.status == self.RequestStatus.waitForRequest):
            self.readRequest(socket)
        elif (self.status == self.RequestStatus.waitForHeader):
            self.readHeader(socket)
        elif (self.status == self.RequestStatus.waitForBody):
            self.readBody(socket)

        if ((not self.boundary and self.currentSize > self.maxSize) or (self.boundary and self.currentSize > self.maxMultiPartSize)):
            qWarning("HttpRequest: received too many bytes")
            self.status = self.RequestStatus.abort

        if (self.status == self.RequestStatus.complete):
            #Extract and decode request parameters from url and body
            self.decodeRequestParams()
            #Extract cookies from headers
            self.extractCookies()

    """
      Get the status of this reqeust.
      @see RequestStatus
    """
    def getStatus(self):
        return self.status

    #Get the method of the HTTP request  (e.g. "GET")
    def getMethod(self):
        return self.method

    #Get the decoded path of the HTPP request (e.g. "/index.html")
    def getPath(self):
        return self.urlDecode(self.path)

    #Get the raw path of the HTTP request (e.g. "/file%20with%20spaces.html")
    def getRawPath(self):
        return self.path

    #Get the version of the HTPP request (e.g. "HTTP/1.1")
    def getVersion(self):
        return self.version

    """
      Get the value of a HTTP request header.
      @param name Name of the header
      @return If the header occurs multiple times, only the last
      one is returned.
    """
    def getHeader(self, name):
        return self.headers[QByteArray(name)]

    """
      Get the values of a HTTP request header.
      @param name Name of the header
    """
    def getHeaders(self, name):
        return self.headers[name]

    #Get all HTTP request headers
    def getHeaderMap(self):
        return self.headers

    """
      Get the value of a HTTP request parameter.
      @param name Name of the parameter
      @return If the parameter occurs multiple times, only the last
      one is returned.
    """
    def getParameter(self, name):
        return parameters.value(name)

    """
      Get the values of a HTTP request parameter.
      @param name Name of the parameter
    """
    def getParameters(self, name):
        return parameters.values(name)

    #Get all HTTP request parameters.
    def getParameterMap(self):
        return parameters

    #Get the HTTP request body.
    def getBody(self):
        return self.bodyData

    """
      Decode an URL parameter.
      E.g. replace "%23" by '#' and replace '+' by ' '.
      @param source The url encoded strings
      @see QUrl::toPercentEncoding for the reverse direction
    """
    def urlDecode(self, source):
        buffer = QByteArray(source)
        buffer.replace(b'+', b' ')
        percentChar = buffer.indexOf('%')
        while (percentChar >= 0):
            ok = True
            byte = buffer.mid(percentChar + 1, 2).toInt(ok, 16)
            if (ok):
                buffer.replace(percentChar, 3, byte, 1)

            percentChar = buffer.indexOf('%', percentChar + 1)

        return buffer

    #Parset he multipart body, that has been stored in the temp file.
    def parseMultiPartFile(self):
        qDebug("HttpRequest: parsing multipart temp file")
        self.tempFile.seek(0)
        finished = False
        while (not self.tempFile.atEnd() and not finished and not self.tempFile.error()):
            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: reading multpart headers")
            #endif
            fieldName = QByteArray()
            fileName = QByteArray()
            while (not self.tempFile.atEnd() and not finished and not self.tempFile.error()):
                line = QByteArray(self.tempFile.readLine(65536).trimmed())
                if (line.startsWith("Content-Disposition:")):
                    if (line.contains("form-data")):
                        start = line.indexOf(" name=\"")
                        end = line.indexOf("\"", start + 7)
                        if (start >= 0 and end >= start):
                            fieldName = line.mid(start + 7, end - start - 7)

                        start = line.indexOf(" filename=\"")
                        end = line.indexOf("\"", start + 11)
                        if (start >= 0 and end >= start):
                            fileName = line.mid(start + 11, end - start - 11)

                        #ifdef SUPERVERBOSE
                        qDebug("HttpRequest: multipart field=%s, filename=%s" % (fieldName.data(), fileName.data()))
                        #endif
                    else:
                        qDebug("HttpRequest: ignoring unsupported content part %s" % (line.data()))
                elif (not line):
                    break

            #ifdef SUPERVERBOSE
            qDebug("HttpRequest: reading multpart data")
            #endif
            uploadedFile = QTemporaryFile()
            fieldValue = QByteArray()
            while (not self.tempFile.atEnd() and not finished and self.tempFile.error()):
                line = QByteArray(self.tempFile.readLine(65536))
                if (line.startsWith("--" + self.boundary)):
                    #Boundary found. Until now we have collected 2 bytes too much,
                    #so remove them from the last result
                    if (not fileName and fieldName):
                        #last field was a form field
                        fieldValue.remove(fieldValue.size() - 2, 2)
                        parameters.insert(fieldName, fieldValue)
                        qDebug("HttpRequest: set parameter %s=%s" % (fieldName.data(), fieldValue.data()))
                    elif (fileName and fieldName):
                        #last field was a file
                        #ifdef SUPERVERBOSE
                        qDebug("HttpRequest: finishing writing to uploaded file")
                        #endif
                        uploadedFile.resize(uploadedFile.size() - 2)
                        uploadedFile.flush()
                        uploadedFile.seek(0)
                        parameters.insert(fieldName, fileName)
                        qDebug("HttpRequest: set parameter %s=%s" % (fieldName.data(), fileName.data()))
                        self.uploadedFiles.insert(fieldName, uploadedFile)
                        qDebug("HttpRequest: uploaded file size is %i" % (uploadedFile.size()))

                    if (line.contains(self.boundary + "--")):
                        finished = True
                    break
                else:
                    if (not fileName and fieldName):
                        #this is a form field.
                        self.currentSize += line.size()
                        fieldValue.append(line)
                    elif (fileName and fieldName):
                        #this is a file
                        if (not uploadedFile):
                            uploadedFile = QTemporaryFile()
                            uploadedFile.open()
                        uploadedFile.write(line)
                        if (uploadedFile.error()):
                            qCritical("HttpRequest: error writing temp file, %s" % (uploadedFile.errorString()))

        if (self.tempFile.error()):
            qCritical("HttpRequest: cannot read temp file, %s" % (self.tempFile.errorString()))
        #ifdef SUPERVERBOSE
        qDebug("HttpRequest: finished parsing multipart temp file")
        #endif

    """
      Get an uploaded file. The file is already open. It will
      be closed and deleted by the destructor of this HttpRequest
      object (after processing the request).
      <p>
      For uploaded files, the method getParameters() returns
      the original fileName as provided by the calling web browser.
    """
    def getUploadedFile(self, fieldName):
        return self.uploadedFiles.value(fieldName)

    """
      Get the value of a cookie.
      @param name Name of the cookie
    """
    def getCookie(self, name):
        return cookies.value(name)

    #Get the map of cookies
    def getCookieMap(self):
        return cookies

    """
    Get the address of the connected client.
    Note that multiple clients may have the same IP address, if they
    share an internet connection (which is very common).
    """
    def getPeerAddress(self):
        return self.peerAddress
