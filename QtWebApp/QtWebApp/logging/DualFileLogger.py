#include <QString>
#include <QSettings>
#include <QtGlobal>
#include "logglobal.h"
#include "logger.h"
#include "filelogger.h"

"""
  Logs messages into two log files simultaneously.
  May be used to create two logfiles with different configuration settings.
  @see FileLogger for a description of the two underlying loggers.
"""
#include "dualfilelogger.h"
class DualFileLogger(Logger):

    """
      Constructor.
      @param firstSettings Configuration settings for the first log file, usually stored in an INI file.
      Must not be 0.
      Settings are read from the current group, so the caller must have called settings->beginGroup().
      Because the group must not change during runtime, it is recommended to provide a
      separate QSettings instance to the logger that is not used by other parts of the program.
      @param secondSettings Same as firstSettings, but for the second log file.
      @param refreshInterval Interval of checking for changed config settings in msec, or 0=disabled
      @param parent Parent object.
    """
    def __init__(self, firstSettings, secondSettings, refreshInterval = 10000, parent = None):
        super(DualFileLogger, self).__init__(parent)

        self.firstLogger = FileLogger(firstSettings, refreshInterval, self)
        self.secondLogger = FileLogger(secondSettings, refreshInterval, self)

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
        self.firstLogger.log(type, message, file, function, line)
        self.secondLogger.log(type, message, file, function, line)

    """
      Clear the thread-local data of the current thread.
      This method is thread safe.
      @param buffer Whether to clear the backtrace buffer
      @param variables Whether to clear the log variables
    """
    def clear(self, buffer = True, variables = True):
        self.firstLogger.clear(buffer, variables)
        self.secondLogger.clear(buffer, variables)
