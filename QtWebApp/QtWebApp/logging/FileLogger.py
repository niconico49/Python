#include <QtGlobal>
#include <QSettings>
#include <QFile>
#include <QMutex>
#include <QBasicTimer>
#include "logglobal.h"
#include "logger.h"

"""
  Logger that uses a text file for output. Settings are read from a
  config file using a QSettings object. Config settings can be changed at runtime.
  <p>
  Example for the configuration settings:
  <code><pre>
  fileName=logs/QtWebApp.log
  maxSize=1000000
  maxBackups=2
  minLevel=0
  msgformat={timestamp} {typeNr} {type} thread={thread}: {msg}
  timestampFormat=dd.MM.yyyy hh:mm:ss.zzz
  bufferSize=0
  </pre></code>

  - fileName is the name of the log file, relative to the directory of the settings file.
    In case of windows, if the settings are in the registry, the path is relative to the current
    working directory.
  - maxSize is the maximum size of that file in bytes. The file will be backed up and
    replaced by a new file if it becomes larger than this limit. Please note that
    the actual file size may become a little bit larger than this limit. Default is 0=unlimited.
  - maxBackups defines the number of backup files to keep. Default is 0=unlimited.
  - minLevel defines the minimum type of messages that are written (together with buffered messages) into the file. Defaults is 0=debug.
  - msgFormat defines the decoration of log messages, see LogMessage class. Default is "{timestamp} {type} {msg}".
  - timestampFormat defines the format of timestamps, see QDateTime::toString(). Default is "yyyy-MM-dd hh:mm:ss.zzz".
  - bufferSize defines the size of the buffer. Default is 0=disabled.

  @see set() describes how to set logger variables
  @see LogMessage for a description of the message decoration.
  @see Logger for a descrition of the buffer.
"""

#include "filelogger.h"
#include <QTime>
#include <QStringList>
#include <QThread>
#include <QtGlobal>
#include <QFile>
#include <QTimerEvent>
#include <QDir>
#include <QFileInfo>
#include <stdio.h>

class FileLogger(Logger):

    """
      Constructor.
      @param settings Configuration settings, usually stored in an INI file. Must not be 0.
      Settings are read from the current group, so the caller must have called settings->beginGroup().
      Because the group must not change during runtime, it is recommended to provide a
      separate QSettings instance to the logger that is not used by other parts of the program.
      @param refreshInterval Interval of checking for changed config settings in msec, or 0=disabled
      @param parent Parent object
    """
    def __init__(self, settings, refreshInterval = 10000, parent = None):
        super(FileLogger, self).__init__(parent)
        #Q_ASSERT(settings != 0)
        #Q_ASSERT(refreshInterval >= 0)
        self.settings = settings
        self.file = 0
        if (refreshInterval > 0):
            self.refreshTimer.start(refreshInterval, self)

        self.flushTimer.start(1000, self)
        self.refreshSettings()

    #Destructor. Closes the file.
    def __del__(self):
        self.close()

    """
      Refreshes the configuration settings.
      This method is thread-safe.
    """
    def refreshSettings(self):
        mutex.lock()
        #Save old file name for later comparision with new settings
        oldFileName = self.fileName

        #Load new config settings
        self.settings.sync()
        self.fileName = self.settings.value("fileName").toString()
        #Convert relative fileName to absolute, based on the directory of the config file.
        #ifdef Q_OS_WIN32
        if (QDir.isRelativePath(self.fileName) and self.settings.format() != QSettings.NativeFormat):
        #else
        #if (QDir.isRelativePath(self.fileName)):
        #endif
            configFile = QFileInfo(self.settings.fileName())
            self.fileName = QFileInfo(configFile.absolutePath(), self.fileName).absoluteFilePath()

        self.maxSize = self.settings.value("maxSize", 0).toLongLong()
        self.maxBackups = self.settings.value("maxBackups", 0).toInt()
        msgFormat = self.settings.value("msgFormat", "{timestamp} {type} {msg}").toString()
        timestampFormat = self.settings.value("timestampFormat", "yyyy-MM-dd hh:mm:ss.zzz").toString()
        minLevel = self.settings.value("minLevel", 0).toInt()
        bufferSize = self.settings.value("bufferSize", 0).toInt()

        #Create new file if the filename has been changed
        if (oldFileName != self.fileName):
            fprintf(stderr, "Logging to %s\n", qPrintable(self.fileName))
            self.close()
            self.open()

        mutex.unlock()

    #Write a message to the log file
    def write(self, logMessage):
        #Try to write to the file
        if (self.file):
            #Write the message
            self.file.write(qPrintable(logMessage.toString(msgFormat, timestampFormat)))

            #Flush error messages immediately, to ensure that no important message
            #gets lost when the program terinates abnormally.
            if (logMessage.getType() >= QtCriticalMsg):
                self.file.flush()

            #Check for success
            if (self.file.error()):
                close()
                qWarning("Cannot write to log file %s: %s" % (self.fileName, self.file.errorString()))

        #Fall-back to the super class method, if writing failed
        if (not self.file):
            Logger.write(logMessage)

    #Open the output file
    def open(self):
        if (not self.fileName):
            qWarning("Name of logFile is empty")
        else:
            self.file = QFile(self.fileName)
            if (not self.file.open(QIODevice.WriteOnly or QIODevice.Append or QIODevice.Text)):
                qWarning("Cannot open log file %s: %s" % (self.fileName, self.file.errorString()))
                self.file = 0

    #Close the output file
    def close(self):
        if (self.file):
            self.file.close()
            del self.file
            self.file = 0

    #Rotate files and delete some backups if there are too many
    def rotate(self):
        #count current number of existing backup files
        count = 0
        while(True):
            bakfile = QFile(QString("%1.%2").arg(self.fileName).arg(count + 1))
            if (bakFile.exists()):
                ++count
            else:
                break

    #Remove all old backup files that exceed the maximum number
    while (self.maxBackups > 0 and count >= self.maxBackups):
        QFile.remove(QString("%1.%2").arg(self.fileName).arg(count))
        --count

    #Rotate backup files
    for (i = count; i > 0; --i):
        QFile::rename(QString("%1.%2").arg(self.fileName).arg(i), QString("%1.%2").arg(self.fileName).arg(i + 1))

    #Backup the current logfile
    QFile.rename(self.fileName, self.fileName + ".1")

    """
      Handler for timer events.
      Refreshes config settings or synchronizes I/O buffer, depending on the event.
      This method is thread-safe.
      @param event used to distinguish between the two timers.
    """
    def timerEvent(self, event):
        if (not event):
            return
        elif (event.timerId() == self.refreshTimer.timerId()):
            self.refreshSettings()
        elif (event.timerId() == self.flushTimer.timerId() and self.file):
            mutex.lock()

            #Flush the I/O buffer
            self.file.flush()

            #Rotate the file if it is too large
            if (self.maxSize > 0 and self.file.size() >= self.maxSize):
                self.close()
                self.rotate()
                self.open()

            mutex.unlock()
