#include "httpglobal.h"
#include "httprequest.h"
#include "httpresponse.h"

"""
   The request handler generates a response for each HTTP request. Web Applications
   usually have one central request handler that maps incoming requests to several
   controllers (servlets) based on the requested path.
   <p>
   You need to override the service() method or you will always get an HTTP error 501.
   <p>
   @warning Be aware that the main request handler instance must be created on the heap and
   that it is used by multiple threads simultaneously.
   @see StaticFileController which delivers static local files.
"""

from PyQt5.QtCore import (QObject)

#include "httprequesthandler.h"

class HttpRequestHandler(QObject):
    def __init__(self, parent = None):
        super(HttpRequestHandler, self).__init__(parent)

    """
      Generate a response for an incoming HTTP request.
      @param request The received HTTP request
      @param response Must be used to return the response
      @warning This method must be thread safe
    """
    def service(self, request, response):
        qCritical("HttpRequestHandler: you need to override the service() function")
        qDebug("HttpRequestHandler: request=%s %s %s" % (request.getMethod().data(), request.getPath().data(), request.getVersion().data()))
        response.setStatus(501, "not implemented")
        response.write("501 not implemented", true)
