#include <QList>
#include <QByteArray>
#include "httpglobal.h"
#include "httpcookie.h"

"""
  HTTP cookie as defined in RFC 2109. This class can also parse
  RFC 2965 cookies, but skips fields that are not defined in RFC
  2109.
"""
class HttpCookie():

    #Creates an empty cookie
    def __init__(self):
        self.version = 1
        self.maxAge = 0
        self.secure = False

    """
      Create a cookie and set name/value pair.
      @param name name of the cookie
      @param value value of the cookie
      @param maxAge maximum age of the cookie in seconds. 0=discard immediately
      @param path Path for that the cookie will be sent, default="/" which means the whole domain
      @param comment Optional comment, may be displayed by the web browser somewhere
      @param domain Optional domain for that the cookie will be sent. Defaults to the current domain
      @param secure If true, the cookie will only be sent on secure connections
    """
    def __init__(self, name, value, maxAge, path, comment, domain, secure):
        self.name = name
        self.value = value
        self.maxAge = maxAge
        self.path = path
        self.comment = comment
        self.domain = domain
        self.secure = secure
        self.version = 1

    """
      Create a cookie from a string.
      @param source String as received in a HTTP Cookie2 header.
    """
    def __init__(self, source):
        self.version = 1
        self.maxAge = 0
        self.secure = False
        list = self.splitCSV(source)
        for part in list:
            #Split the part into name and value
            name = QByteArray()
            value = QByteArray()
            posi = part.indexOf('=')
            if (posi):
                name = part.left(posi).trimmed()
                value = part.mid(posi + 1).trimmed()
            else:
                name = part.trimmed()
                value = ""

            #Set fields
            if (name == "Comment"):
                self.comment = value
            elif (name == "Domain"):
                self.domain = value
            elif (name == "Max-Age"):
                self.maxAge = int(value)
            elif (name == "Path"):
                self.path = value
            elif (name == "Secure"):
                self.secure = True
            elif (name == "Version"):
                self.version = int(value)
            else:
                if (not self.name):
                    self.name = name
                    self.value = value
                else:
                    qWarning("HttpCookie: Ignoring unknown %s=%s" % (name.data(), value.data()))

    #Convert this cookie to a string that may be used in a Set-Cookie header.
    def toByteArray(self):
        buffer = QByteArray(self.name)
        buffer.append('=')
        buffer.append(self.value)
        if (self.comment):
            buffer.append("; Comment=")
            buffer.append(self.comment)
        if (self.domain):
            buffer.append("; Domain=")
            buffer.append(self.domain)
        if (self.maxAge != 0):
            buffer.append("; Max-Age=")
            buffer.append(QByteArray.number(self.maxAge))
        if (self.path):
            buffer.append("; Path=")
            buffer.append(self.path)
        if (self.secure):
            buffer.append("; Secure")

        buffer.append("; Version=")
        buffer.append(QByteArray.number(self.version))
        return buffer

    #Set the name of this cookie
    def setName(self, name):
        self.name = name

    #Set the value of this cookie
    def setValue(self, value):
        self.value = value

    #Set the comment of this cookie
    def setComment(self, comment):
        self.comment = comment

    #Set the domain of this cookie
    def setDomain(self, domain):
        self.domain = domain

    #Set the maximum age of this cookie in seconds. 0=discard immediately
    def setMaxAge(self, maxAge):
        self.maxAge = maxAge

    #Set the path for that the cookie will be sent, default="/" which means the whole domain
    def setPath(self, path):
        self.path = path

    #Set secure mode, so that the cookie will only be sent on secure connections
    def setSecure(self, secure):
        self.secure = secure

    #Get the name of this cookie
    def getName(self):
        return self.name

    #Get the value of this cookie
    def getValue(self):
        return self.value

    #Get the comment of this cookie
    def getComment(self):
        return self.comment

    #Get the domain of this cookie
    def getDomain(self):
        return self.domain

    #Set the maximum age of this cookie in seconds.
    def getMaxAge(self):
        return self.maxAge

    #Set the path of this cookie
    def getPath(self):
        return self.path

    #Get the secure flag of this cookie
    def getSecure(self):
        return self.secure

    #Returns always 1
    def getVersion(self):
        return self.version

    """
      Split a string list into parts, where each part is delimited by semicolon.
      Semicolons within double quotes are skipped. Double quotes are removed.
    """
    def splitCSV(self, source):
        inString = False
        list = []
        buffer = QByteArray()
        for (i = 0; i < source.size(); ++i):
            c = source.at(i)
            if (inString == False):
                if (c == '\"'):
                    inString = True
                elif (c == ';'):
                    trimmed = QByteArray(buffer.trimmed())
                    if (trimmed):
                        list.append(trimmed)
                    buffer.clear()
                else:
                    buffer.append(c)
            else:
                if (c == '\"'):
                    inString = False
                else:
                    buffer.append(c)
        trimmed = QByteArray(buffer.trimmed())
        if (trimmed):
            list.append(trimmed)
        return list
