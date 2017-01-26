#include <QtGlobal>
#include <QDateTime>
#include <QHash>
#include "logglobal.h"

"""
  Represents a single log message together with some data
  that are used to decorate the log message.

  The following variables may be used in the message and in msgFormat:

  - {timestamp} Date and time of creation
  - {typeNr}    Type of the message in numeric format (0-3)
  - {type}      Type of the message in string format (DEBUG, WARNING, CRITICAL, FATAL)
  - {thread}    ID number of the thread
  - {msg}       Message text
  - {xxx}       For any user-defined logger variable

  Plus some new variables since QT 5.0, only filled when compiled in debug mode:

  - {file}      Filename where the message was generated
  - {function}  Function where the message was generated
  - {line}      Line number where the message was generated
"""
#ID number of the thread
#Qt::HANDLE threadId;

#include "logmessage.h"
#include <QThread>
class LogMessage():
    """
      Constructor. All parameters are copied, so that later changes to them do not
      affect this object.
      @param type Type of the message
      @param message Message text
      @param logVars Logger variables, 0 is allowed
      @param file Name of the source file where the message was generated
      @param function Name of the function where the message was generated
      @param line Line Number of the source file, where the message was generated
    """
    def __init__(self, type, message, logVars, file, function, line):
        self.type = type
        self.message = message
        self.file = file
        self.function = function
        self.line = line
        self.timestamp = QDateTime.currentDateTime()
        self.threadId = QThread.currentThreadId()

        #Copy the logVars if not null,
        #so that later changes in the original do not affect the copy
        if (logVars):
            self.logVars = logVars

    """
      Returns the log message as decorated string.
      @param msgFormat Format of the decoration. May contain variables and static text,
          e.g. "{timestamp} {type} thread={thread}: {msg}".
      @param timestampFormat Format of timestamp, e.g. "dd.MM.yyyy hh:mm:ss.zzz", see QDateTime::toString().
      @see QDatetime for a description of the timestamp format pattern
    """
    def toString(self, msgFormat, timestampFormat):
        decorated = QString(msgFormat + "\n")
        decorated.replace("{msg}", self.message)

        if (decorated.contains("{timestamp}")):
            decorated.replace("{timestamp}", self.timestamp.toString(timestampFormat))

        typeNr = QString()
        typeNr.setNum(self.type)
        decorated.replace("{typeNr}", typeNr)

        if (self.type == QtDebugMsg):
            decorated.replace("{type}", "DEBUG")
        elif (self.type == QtWarningMsg):
            decorated.replace("{type}", "WARNING")
        elif (self.type == QtCriticalMsg):
            decorated.replace("{type}", "CRITICAL")
        elif (self.type == QtFatalMsg):
            decorated.replace("{type}", "FATAL")
        else:
            decorated.replace("{type}", typeNr)

        decorated.replace("{file}", self.file)
        decorated.replace("{function}", self.function)
        decorated.replace("{line}", QString.number(self.line))

        threadId = QString()
        threadId.setNum(QThread.currentThreadId())
        decorated.replace("{thread}", threadId)

        #Fill in variables
        if (decorated.contains("{") and logVars):
            keys = self.logVars.keys()
            for key in keys:
                decorated.replace("{" + key + "}", self.logVars.value(key))

        return decorated

    #Get the message type.
    def getType(self):
        return self.type
