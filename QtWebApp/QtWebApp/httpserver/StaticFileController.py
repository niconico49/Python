#include <QCache>
#include <QMutex>
#include "httpglobal.h"
#include "httprequest.h"
#include "httpresponse.h"
#include "httprequesthandler.h"

"""
  Delivers static files. It is usually called by the applications main request handler when
  the caller requests a path that is mapped to static files.
  <p>
  The following settings are required in the config file:
  <code><pre>
  path=../docroot
  encoding=UTF-8
  maxAge=60000
  cacheTime=60000
  cacheSize=1000000
  maxCachedFileSize=65536
  </pre></code>
  The path is relative to the directory of the config file. In case of windows, if the
  settings are in the registry, the path is relative to the current working directory.
  <p>
  The encoding is sent to the web browser in case of text and html files.
  <p>
  The cache improves performance of small files when loaded from a network
  drive. Large files are not cached. Files are cached as long as possible,
  when cacheTime=0. The maxAge value (in msec!) controls the remote browsers cache.
  <p>
  Do not instantiate this class in each request, because this would make the file cache
  useless. Better create one instance during start-up and call it when the application
  received a related HTTP request.
"""

from PyQt5.QtCore import (QMutex, QDir, QSettings, QFileInfo, qDebug)

from HttpRequestHandler import *

#include "staticfilecontroller.h"
#include <QFileInfo>
#include <QDir>
#include <QDateTime>
class StaticFileController(HttpRequestHandler):
    def __init__(self, settings, parent = None):
        super(StaticFileController, self).__init__(parent)
        self.mutex = QMutex()
        self.maxAge = int(settings.value("maxAge", "60000"))
        self.encoding = settings.value("encoding", "UTF-8")
        self.docroot = settings.value("path", ".")
        self.cache = {}
        if(not self.docroot.startswith(":/") and not self.docroot.startswith("qrc://")):
            #Convert relative path to absolute, based on the directory of the config file.
            #ifdef Q_OS_WIN32
            if (QDir.isRelativePath(self.docroot) and settings.format() != QSettings.NativeFormat):
            #else
            #if (QDir.isRelativePath(self.docroot)):
            #endif
                configFile = QFileInfo(settings.fileName())
                self.docroot = QFileInfo(QDir(configFile.absolutePath()), self.docroot).absoluteFilePath()
        qDebug("StaticFileController: docroot=%s, encoding=%s, maxAge=%i" % (self.docroot, self.encoding, self.maxAge))
        self.maxCachedFileSize = int(settings.value("maxCachedFileSize", "65536"))
        #cache.setMaxCost(int(settings.value("cacheSize", "1000000")))
        self.cacheTimeout = int(settings.value("cacheTime", "60000"))
        #qDebug("StaticFileController: cache timeout=%i, size=%i" % (self.cacheTimeout, cache.maxCost()))
        qDebug("StaticFileController: cache timeout=%i" % (self.cacheTimeout))

    def service(self, request, response):
        path = request.getPath()
        #Check if we have the file in cache
        now = QDateTime.currentMSecsSinceEpoch()
        self.mutex.lock()
        entry = self.cache[path]
        if (entry and (self.cacheTimeout == 0 or entry.created > now - self.cacheTimeout)):
            #QByteArray document = entry.document #copy the cached document, because other threads may destroy the cached entry immediately after mutex unlock.
            #QByteArray filename = entry.filename
            document = entry.document #copy the cached document, because other threads may destroy the cached entry immediately after mutex unlock.
            filename = entry.filename
            self.mutex.unlock()
            qDebug("StaticFileController: Cache hit for %s" % (path.data()))
            self.setContentType(filename, response)
            response.setHeader("Cache-Control", "max-age=" + QByteArray.number(self.maxAge / 1000))
            response.write(document)
        else:
            self.mutex.unlock()
            #The file is not in cache.
            qDebug("StaticFileController: Cache miss for %s" % path.data())
            #Forbid access to files outside the docroot directory
            if (path.contains("/..")):
                qWarning("StaticFileController: detected forbidden characters in path %s" % path.data())
                response.setStatus(403, "forbidden")
                response.write("403 forbidden", true)
                return
            #If the filename is a directory, append index.html.
            if (QFileInfo(self.docroot + path).isDir()):
                path += "/index.html"
            #Try to open the file
            file = QFile(self.docroot + path)
            qDebug("StaticFileController: Open file %s" % (file.fileName()))
            if (file.open(QIODevice.ReadOnly)):
                self.setContentType(path, response)
                response.setHeader("Cache-Control", "max-age=" + QByteArray.number(self.maxAge / 1000))
                if (file.size() <= self.maxCachedFileSize):
                    # Return the file content and store it also in the cache
                    entry = {}
                    entry["document"] = ""
                    while (not file.atEnd() and not file.error()):
                        buffer = file.read(65536)
                        response.write(buffer)
                        entry["document"] += buffer
                    entry["created"] = now
                    entry["filename"] = path
                    self.mutex.lock()
                    self.cache[request.getPath()] = entry
                    self.mutex.unlock()
                else:
                    #Return the file content, do not store in cache
                    while (not file.atEnd() and not file.error()):
                        response.write(file.read(65536))
                file.close()
            else:
                if (file.exists()):
                    qWarning("StaticFileController: Cannot open existing file %s for reading" % (file.fileName()))
                    response.setStatus(403, "forbidden")
                    response.write("403 forbidden", true)
                else:
                    response.setStatus(404, "not found")
                    response.write("404 not found", true)

    def setContentType(self, fileName, response):
        if (fileName.endsWith(".png")):
            response.setHeader("Content-Type", "image/png")
        elif (fileName.endsWith(".jpg")):
            response.setHeader("Content-Type", "image/jpeg")
        elif (fileName.endsWith(".gif")):
            response.setHeader("Content-Type", "image/gif")
        elif (fileName.endsWith(".pdf")):
            response.setHeader("Content-Type", "application/pdf")
        elif (fileName.endsWith(".txt")):
            response.setHeader("Content-Type" % ("text/plain; charset=" + self.encoding))
        elif (fileName.endsWith(".html") or fileName.endsWith(".htm")):
            response.setHeader("Content-Type" % ("text/html; charset=" + self.encoding))
        elif (fileName.endsWith(".css")):
            response.setHeader("Content-Type", "text/css")
        elif (fileName.endsWith(".js")):
            response.setHeader("Content-Type", "text/javascript")
        elif (fileName.endsWith(".svg")):
            response.setHeader("Content-Type", "image/svg+xml")
        elif (fileName.endsWith(".woff")):
            response.setHeader("Content-Type", "font/woff")
        elif (fileName.endsWith(".woff2")):
            response.setHeader("Content-Type", "font/woff2")
        elif (fileName.endsWith(".ttf")):
            response.setHeader("Content-Type", "application/x-font-ttf")
        elif (fileName.endsWith(".eot")):
            response.setHeader("Content-Type", "application/vnd.ms-fontobject")
        elif (fileName.endsWith(".otf")):
            response.setHeader("Content-Type", "application/font-otf")
        #Todo: add all of your content types
        else:
            qDebug("StaticFileController: unknown MIME type for filename '%s'" % (fileName))
