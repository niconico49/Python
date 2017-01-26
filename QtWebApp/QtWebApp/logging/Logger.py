#include <QtGlobal>
#include <QThreadStorage>
#include <QHash>
#include <QStringList>
#include <QMutex>
#include <QObject>
#include "logglobal.h"
#include "logmessage.h"

"""
  Decorates and writes log messages to the console, stderr.
  <p>
  The decorator uses a predefined msgFormat string to enrich log messages
  with additional information (e.g. timestamp).
  <p>
  The msgFormat string and also the message text may contain additional
  variable names in the form  <i>{name}</i> that are filled by values
  taken from a static thread local dictionary.
  <p>
  The logger keeps a configurable number of messages in a ring-buffer.
  A log message with a severity >= minLevel flushes the buffer,
  so the stored messages get written out. If the buffer is disabled, then
  only messages with severity >= minLevel are written out.
  <p>
  If you enable the buffer and use minLevel=2, then the application logs
  only errors together with some buffered debug messages. But as long no
  error occurs, nothing gets written out.
  <p>
  Each thread has it's own buffer.
  <p>
  The logger can be registered to handle messages from
  the static global functions qDebug(), qWarning(), qCritical() and qFatal().

  @see set() describes how to set logger variables
  @see LogMessage for a description of the message decoration.
  @warning You should prefer a derived class, for example FileLogger,
  because logging to the console is less useful.
"""

class DECLSPEC Logger : public QObject {
private:
    #Thread local backtrace buffers
    QThreadStorage<QList<LogMessage*>*> buffers;
};

#include "logger.h"
#include <stdio.h>
#include <stdlib.h>
#include <QMutex>
#include <QDateTime>
#include <QThread>
#include <QObject>

QThreadStorage<QHash<QString,QString>*> Logger::logVars;

class Logger(QObject):
    #Used to synchronize access of concurrent threads
    #static
    mutex = QMutex()
    
    #Pointer to the default logger, used by msgHandler()
    #static
    defaultLogger = Logger(0)

    #Thread local variables to be used in log messages
    #static
    logVars = QThreadStorage<QHash<QString,QString>*>

    """
      Constructor.
      @param msgFormat Format of the decoration, e.g. "{timestamp} {type} thread={thread}: {msg}"
      @param timestampFormat Format of timestamp, e.g. "dd.MM.yyyy hh:mm:ss.zzz"
      @param minLevel Minimum severity that genertes an output (0=debug, 1=warning, 2=critical, 3=fatal).
      @param bufferSize Size of the backtrace buffer, number of messages per thread. 0=disabled.
      @param parent Parent object
      @see LogMessage for a description of the message decoration.
    """
    def __init__(self, msgFormat = "{timestamp} {type} {msg}", timestampFormat = "dd.MM.yyyy hh:mm:ss.zzz", minLevel = QtDebugMsg, bufferSize = 0, parent = None):
        super(Logger, self).__init__(parent)
        self.msgFormat = msgFormat
        self.timestampFormat = timestampFormat
        self.minLevel = minLevel
        self.bufferSize = bufferSize

    #Destructor
    def __del__(self):
        if (Logger.defaultLogger == self):
            qInstallMessageHandler(0)
            Logger.defaultLogger = 0

    """
      Message Handler for the global static logging functions (e.g. qDebug()).
      Forward calls to the default logger.
      <p>
      In case of a fatal message, the program will abort.
      Variables in the in the message are replaced by their values.
      This method is thread safe.
      @param type Message type (level)
      @param message Message text
      @param file Name of the source file where the message was generated (usually filled with the macro __FILE__)
      @param function Name of the function where the message was generated (usually filled with the macro __LINE__)
      @param line Line Number of the source file, where the message was generated (usually filles with the macro __func__ or __FUNCTION__)
    """
    def msgHandler(self, type, message, file = "", function = "", line = 0):
        recursiveMutex = QMutex(QMutex.Recursive)
        nonRecursiveMutex = QMutex(QMutex.NonRecursive)

        """
        Prevent multiple threads from calling this method simultaneoulsy.
        But allow recursive calls, which is required to prevent a deadlock
        if the logger itself produces an error message.
        """
        recursiveMutex.lock()

        #Fall back to stderr when this method has been called recursively.
        if (Logger.defaultLogger and nonRecursiveMutex.tryLock()):
            Logger.defaultLogger.log(type, message, file, function, line)
            nonRecursiveMutex.unlock()
        else:
            fputs(qPrintable(message), stderr)
            fflush(stderr)

        #Abort the program after logging a fatal message
        if (type >= QtFatalMsg):
            abort()

        recursiveMutex.unlock()

    """
      Wrapper for QT version 5.
      @param type Message type (level)
      @param context Message context
      @param message Message text
      @see msgHandler()
    """
    @staticmethod
    def msgHandler5(type, context, message):
        #suppress "unused parameter" warning
        msgHandler(type, message, context.file, context.function, context.line)

    """
      Decorate and write a log message to stderr. Override this method
      to provide a different output medium.
    """
    def write(self, logMessage):
        fputs(qPrintable(logMessage.toString(self.msgFormat, self.timestampFormat)), stderr)
        fflush(stderr)

    """
      Installs this logger as the default message handler, so it
      can be used through the global static logging functions (e.g. qDebug()).
    """
    def installMsgHandler(self):
        Logger.defaultLogger = self
        qInstallMessageHandler(msgHandler5)

    """
      Sets a thread-local variable that may be used to decorate log messages.
      This method is thread safe.
      @param name Name of the variable
      @param value Value of the variable
    """
    @staticmethod
    def set(name, value):
        Logger.mutex.lock()
        if (not Logger.logVars.hasLocalData()):
            Logger.logVars.setLocalData(new QHash<QString, QString>)
        Logger.logVars.localData().insert(name, value)
        Logger.mutex.unlock()

    """
      Clear the thread-local data of the current thread.
      This method is thread safe.
      @param buffer Whether to clear the backtrace buffer
      @param variables Whether to clear the log variables
    """
    def clear(self, buffer = True, variables = True):
        Logger.mutex.lock()
        if (buffer and buffers.hasLocalData()):
            buffer = buffers.localData()
            while (buffer):
                logMessage = buffer.takeLast()
                del logMessage

        if (variables and Logger.logVars.hasLocalData()):
            Logger.logVars.localData().clear()

        Logger.mutex.unlock()

    """
      Decorate and log the message, if type>=minLevel.
      This method is thread safe.
      @param type Message type (level)
      @param message Message text
      @param file Name of the source file where the message was generated (usually filled with the macro __FILE__)
      @param function Name of the function where the message was generated (usually filled with the macro __LINE__)
      @param line Line Number of the source file, where the message was generated (usually filles with the macro __func__ or __FUNCTION__)
      @see LogMessage for a description of the message decoration.
    """
    def log(self, type, message, file = "", function = "", line = 0):
        Logger.mutex.lock()

        #If the buffer is enabled, write the message into it
        if (self.bufferSize > 0):
            #Create new thread local buffer, if necessary
            if (not buffers.hasLocalData()):
                buffers.setLocalData(new QList<LogMessage*>())
        
            buffer = buffers.localData()
            #Append the decorated log message
            logMessage = LogMessage(type, message, Logger.logVars.localData(), file, function, line)
            buffer.append(logMessage)
            #Delete oldest message if the buffer became too large
            if (buffer.size() > self.bufferSize):
                del buffer.takeFirst()
            #If the type of the message is high enough, print the whole buffer
            if (type >= self.minLevel):
                while (buffer):
                    logMessage = buffer.takeFirst()
                    write(logMessage)
                    del logMessage

        #Buffer is disabled, print the message if the type is high enough
        else:
            if (type >= self.minLevel):
                logMessage = LogMessage(type, message, Logger.logVars.localData(), file, function, line)
                write(logMessage)

        Logger.mutex.unlock()
