#include <QByteArray>
#include <QVariant>
#include <QReadWriteLock>
#include "httpglobal.h"

"""
  This class stores data for a single HTTP session.
  A session can store any number of key/value pairs. This class uses implicit
  sharing for read and write access. This class is thread safe.
  @see HttpSessionStore should be used to create and get instances of this class.
"""
class DECLSPEC HttpSession {

public:
    """
      Constructor.
      @param canStore The session can store data, if this parameter is true.
      Otherwise all calls to set() and remove() do not have any effect.
    """
    HttpSession(bool canStore = false);

    """
      Copy constructor. Creates another HttpSession object that shares the
      data of the other object.
    """
    HttpSession(const HttpSession& other);

    """
      Copy operator. Detaches from the current shared data and attaches to
      the data of the other object.
    """
    HttpSession& operator= (const HttpSession& other);


    #Destructor. Detaches from the shared data.
    virtual ~HttpSession();

    #Get the unique ID of this session. This method is thread safe.
    QByteArray getId() const;

    """
      Null sessions cannot store data. All calls to set() and remove() 
      do not have any effect.This method is thread safe.
    """
    bool isNull() const;

    #Set a value. This method is thread safe.
    void set(const QByteArray& key, const QVariant& value);

    #Remove a value. This method is thread safe.
    void remove(const QByteArray& key);

    #Get a value. This method is thread safe.
    QVariant get(const QByteArray& key) const;

    #Check if a key exists. This method is thread safe.
    bool contains(const QByteArray& key) const;

    """
      Get a copy of all data stored in this session.
      Changes to the session do not affect the copy and vice versa.
      This method is thread safe.
    """
    QMap<QByteArray,QVariant> getAll() const;

    """
      Get the timestamp of last access. That is the time when the last
      HttpSessionStore::getSession() has been called.
      This method is thread safe.
    """
    qint64 getLastAccess() const;

    """
      Set the timestamp of last access, to renew the timeout period.
      Called by  HttpSessionStore::getSession().
      This method is thread safe.
    """
    void setLastAccess();

private:
    struct HttpSessionData {

        #Unique ID
        QByteArray id;

        #Timestamp of last access, set by the HttpSessionStore
        qint64 lastAccess;

        #Reference counter
        int refCount;

        #Used to synchronize threads
        QReadWriteLock lock;

        #Storage for the key/value pairs;
        QMap<QByteArray,QVariant> values;
    };

    #Pointer to the shared data.
    HttpSessionData* dataPtr;
};

#include "httpsession.h"
#include <QDateTime>
#include <QUuid>

def HttpSession::HttpSession(bool canStore):
    if (canStore):
        dataPtr = HttpSessionData()
        dataPtr.refCount = 1
        dataPtr.lastAccess = QDateTime.currentMSecsSinceEpoch()
        dataPtr.id = QUuid.createUuid().toString().toLocal8Bit()
        #ifdef SUPERVERBOSE
        qDebug("HttpSession: created new session data with id %s" % (dataPtr.id.data()))
        #endif
    else:
        dataPtr = 0

def HttpSession::HttpSession(const HttpSession& other):
    dataPtr = other.dataPtr
    if (dataPtr):
        dataPtr.lock.lockForWrite()
        dataPtr.refCount++
        #ifdef SUPERVERBOSE
        qDebug("HttpSession: refCount of %s is %i" % (dataPtr.id.data(), dataPtr.refCount))
        #endif
        dataPtr.lock.unlock()

def HttpSession& HttpSession::operator= (const HttpSession& other):
    HttpSessionData* oldPtr = dataPtr
    dataPtr = other.dataPtr
    if (dataPtr):
        dataPtr.lock.lockForWrite()
        dataPtr.refCount++
        #ifdef SUPERVERBOSE
        qDebug("HttpSession: refCount of %s is %i" % (dataPtr.id.data(), dataPtr.refCount))
        #endif
        dataPtr.lastAccess = QDateTime.currentMSecsSinceEpoch()
        dataPtr.lock.unlock()
    if (oldPtr):
        oldPtr.lock.lockForRead()
        refCount = oldPtr.refCount--
        #ifdef SUPERVERBOSE
        qDebug("HttpSession: refCount of %s is %i" % (oldPtr.id.data(), oldPtr.refCount))
        #endif
        oldPtr.lock.unlock()
        if (refCount == 0):
            del oldPtr
    return self

def HttpSession::~HttpSession():
    if (dataPtr):
        dataPtr.lock.lockForRead()
        refCount = --dataPtr.refCount
        #ifdef SUPERVERBOSE
        qDebug("HttpSession: refCount of %s is %i" % (dataPtr.id.data(), dataPtr.refCount))
        #endif
        dataPtr.lock.unlock()
        if (refCount == 0):
            qDebug("HttpSession: deleting data")
            del dataPtr

def QByteArray HttpSession::getId() const:
    if (dataPtr):
        return dataPtr.id
    else:
        return QByteArray()

def bool HttpSession::isNull() const:
    return dataPtr == 0

def void HttpSession::set(const QByteArray& key, const QVariant& value):
    if (dataPtr):
        dataPtr.lock.lockForWrite()
        dataPtr.values.insert(key, value)
        dataPtr.lock.unlock()

def void HttpSession::remove(const QByteArray& key):
    if (dataPtr):
        dataPtr.lock.lockForWrite()
        dataPtr.values.remove(key)
        dataPtr.lock.unlock()

def QVariant HttpSession::get(const QByteArray& key) const:
    QVariant value
    if (dataPtr):
        dataPtr.lock.lockForRead()
        value = dataPtr.values.value(key)
        dataPtr.lock.unlock()
    return value

def bool HttpSession::contains(const QByteArray& key) const:
    found = False
    if (dataPtr):
        dataPtr.lock.lockForRead()
        found = dataPtr.values.contains(key)
        dataPtr.lock.unlock()
    return found

def QMap<QByteArray,QVariant> HttpSession::getAll() const:
    QMap<QByteArray,QVariant> values
    if (dataPtr):
        dataPtr.lock.lockForRead()
        values = dataPtr.values
        dataPtr.lock.unlock()
    return values

def qint64 HttpSession::getLastAccess() const:
    qint64 value = 0
    if (dataPtr):
        dataPtr.lock.lockForRead()
        value = dataPtr.lastAccess
        dataPtr.lock.unlock()
    return value

def void HttpSession::setLastAccess():
    if (dataPtr):
        dataPtr.lock.lockForRead()
        dataPtr.lastAccess = QDateTime.currentMSecsSinceEpoch()
        dataPtr.lock.unlock()
