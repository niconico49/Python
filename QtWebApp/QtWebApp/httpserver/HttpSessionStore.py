#include <QObject>
#include <QMap>
#include <QTimer>
#include <QMutex>
#include "httpglobal.h"
#include "httpsession.h"
#include "httpresponse.h"
#include "httprequest.h"

"""
  Stores HTTP sessions and deletes them when they have expired.
  The following configuration settings are required in the config file:
  <code><pre>
  expirationTime=3600000
  cookieName=sessionid
  </pre></code>
  The following additional configurations settings are optionally:
  <code><pre>
  cookiePath=/
  cookieComment=Session ID
  ;cookieDomain=stefanfrings.de
  </pre></code>
"""

"""
class DECLSPEC HttpSessionStore : public QObject {
    Q_OBJECT
    Q_DISABLE_COPY(HttpSessionStore)
protected:
    #Storage for the sessions
    QMap<QByteArray,HttpSession> sessions;

private slots:
    void sessionTimerEvent();
};
"""

#include "httpsessionstore.h"
#include <QDateTime>
#include <QUuid>

from PyQt5.QtCore import (QObject, pyqtSlot, QMutex, QTimer, qDebug, QDateTime)

class HttpSessionStore(QObject):
    #Constructor.
    def __init__(self, settings, parent = None):
        super(HttpSessionStore, self).__init__(parent)
        self.sessions = {}
        self.mutex = QMutex()
        self.settings = settings
        self.cleanupTimer = QTimer()
        self.cleanupTimer.timeout.connect(self.sessionTimerEvent)

        #connect(self.cleanupTimer, SIGNAL(timeout()), this, SLOT(sessionTimerEvent()))
        self.cleanupTimer.start(60000)
        self.cookieName = str.encode(self.settings.value("cookieName", "sessionid"))
        self.expirationTime = int(self.settings.value("expirationTime", 3600000))
        qDebug("HttpSessionStore: Sessions expire after %i milliseconds" % (self.expirationTime))

    #Destructor
    def __del__(self):
        self.cleanupTimer.stop()

    """
       Get the ID of the current HTTP session, if it is valid.
       This method is thread safe.
       @warning Sessions may expire at any time, so subsequent calls of
       getSession() might return a new session with a different ID.
       @param request Used to get the session cookie
       @param response Used to get and set the new session cookie
       @return Empty string, if there is no valid session.
    """
    def getSessionId(self, request, response):
        #The session ID in the response has priority because this one will be used in the next request.
        self.mutex.lock()
        #Get the session ID from the response cookie
        sessionId = response.getCookies().value(self.cookieName).getValue()
        if (not sessionId):
            #Get the session ID from the request cookie
            sessionId = request.getCookie(self.cookieName)
        #Clear the session ID if there is no such session in the storage.
        if (sessionId):
            if (sessionId not in self.sessions):
                qDebug("HttpSessionStore: received invalid session cookie with ID %s" % (sessionId.data()))
                sessionId.clear()
        self.mutex.unlock()
        return sessionId

    """
       Get the session of a HTTP request, eventually create a new one.
       This method is thread safe. New sessions can only be created before
       the first byte has been written to the HTTP response.
       @param request Used to get the session cookie
       @param response Used to get and set the new session cookie
       @param allowCreate can be set to false, to disable the automatic creation of a new session.
       @return If autoCreate is disabled, the function returns a null session if there is no session.
       @see HttpSession::isNull()
    """
    def getSession(self, request, response, allowCreate):
        sessionId = getSessionId(request, response)
        self.mutex.lock()
        if (sessionId):
            session = self.sessions[sessionId]
            if (session):
                self.mutex.unlock()
                #Refresh the session cookie
                cookieName = self.settings.value("cookieName", "sessionid").toByteArray()
                cookiePath = self.settings.value("cookiePath").toByteArray()
                cookieComment = self.settings.value("cookieComment").toByteArray()
                cookieDomain = self.settings.value("cookieDomain").toByteArray()
                response.setCookie(HttpCookie(cookieName, session.getId(), self.expirationTime / 1000, cookiePath, cookieComment, cookieDomain))
                session.setLastAccess()
                return session
        #Need to create a new session
        if (allowCreate):
            cookieName = self.settings.value("cookieName", "sessionid").toByteArray()
            cookiePath = self.settings.value("cookiePath").toByteArray()
            cookieComment = self.settings.value("cookieComment").toByteArray()
            cookieDomain = self.settings.value("cookieDomain").toByteArray()
            session = HttpSession(true)
            qDebug("HttpSessionStore: create new session with ID %s" % (session.getId().data()))
            self.sessions[session.getId()] = session
            response.setCookie(HttpCookie(cookieName, session.getId(), self.expirationTime / 1000, cookiePath, cookieComment, cookieDomain))
            self.mutex.unlock()
            return session
        #Return a null session
        self.mutex.unlock()
        return HttpSession()

    """
       Get a HTTP session by it's ID number.
       This method is thread safe.
       @return If there is no such session, the function returns a null session.
       @param id ID number of the session
       @see HttpSession::isNull()
    """
    def getSession(self, id):
        self.mutex.lock()
        session = self.sessions[id]
        self.mutex.unlock()
        session.setLastAccess()
        return session

    #Called every minute to cleanup expired sessions.
    @pyqtSlot()
    def sessionTimerEvent(self):
        self.mutex.lock()
        now = QDateTime.currentMSecsSinceEpoch()
        
        for id in self.sessions.keys():
            session = sessions[id]
            lastAccess = session.getLastAccess()
            if (now - lastAccess > self.expirationTime):
                qDebug("HttpSessionStore: session %s expired" % (session.getId().data()))
                del self.sessions[id]
           
        self.mutex.unlock()

    #Delete a session *
    def removeSession(self, session):
        self.mutex.lock()
        del self.sessions[session.getId()]
        self.mutex.unlock()
