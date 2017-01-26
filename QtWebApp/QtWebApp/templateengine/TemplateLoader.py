"""
  Loads localized versions of template files. If the caller requests a file with the
  name "index" and the suffix is ".tpl" and the requested locale is "de_DE, de, en-US",
  then files are searched in the following order:

  - index-de_DE.tpl
  - index-de.tpl
  - index-en_US.tpl  
  - index-en.tpl
  - index.tpl

  The following settings are required:
  <code><pre>
  path=../templates
  suffix=.tpl
  encoding=UTF-8
  </pre></code>
  The path is relative to the directory of the config file. In case of windows, if the
  settings are in the registry, the path is relative to the current working directory.
  @see TemplateCache
"""

#include <QString>
#include <>
#include <QTextCodec>
#include <QMutex>
#include "templateglobal.h"
#include "template.h"

#include "templateloader.h"
#include <QFile>
#include <>
#include <QStringList>
#include <QSet>

from PyQt5.QtCore import (QObject, QDir, QSettings, QFileInfo, QTextCodec, qDebug)

class TemplateLoader(QObject):

    def __init__(self, settings, parent):
        super(TemplateLoader, self).__init__(parent)
        self.templatePath = settings.value("path", ".")
        
        #Convert relative path to absolute, based on the directory of the config file.
        #ifdef Q_OS_WIN32
        if (QDir.isRelativePath(self.templatePath) and settings.format() != QSettings.NativeFormat):
        #else
        #if (QDir.isRelativePath(self.templatePath)):
        #endif
            configFile = QFileInfo(settings.fileName())
            self.templatePath = QFileInfo(QDir(configFile.absolutePath()), self.templatePath).absoluteFilePath()

        self.fileNameSuffix = settings.value("suffix", ".tpl")
        encoding = settings.value("encoding")
        if (not encoding):
            self.textCodec = QTextCodec.codecForLocale()
        else:
            #self.textCodec = QTextCodec.codecForName(encoding.toLocal8Bit())
            self.textCodec = QTextCodec.codecForName(encoding)
        qDebug("TemplateLoader: path=%s, codec=%s" % (self.templatePath, self.textCodec.name().data()))
        
    def tryFile(self, localizedName):
        fileName = self.templatePath + "/" + localizedName + self.fileNameSuffix
        qDebug("TemplateCache: trying file %s" % (fileName))
        file = QFile(fileName)
        if (file.exists()):
            file.open(QIODevice.ReadOnly)
            document = self.textCodec.toUnicode(file.readAll())
            file.close()
            if (file.error()):
                qCritical("TemplateLoader: cannot load file %s, %s" % (fileName, file.errorString()))
                return ""
            else:
                return document
        return ""

    """
      Get a template for a given locale.
      This method is thread safe.
      @param templateName base name of the template file, without suffix and without locale
      @param locales Requested locale(s), e.g. "de_DE, en_EN". Strings in the format of
      the HTTP header Accept-Locale may be used. Badly formatted parts in the string are silently
      ignored.
      @return If the template cannot be loaded, an error message is logged and an empty template is returned.
    """
    def getTemplate(self, templateName, locales = ""):
        self.mutex = QMutex()
        self.mutex.lock()
        #QSet<QString> tried #used to suppress duplicate attempts
        #QStringList locs = locales.split(',', QString.SkipEmptyParts)
        tried = {} #used to suppress duplicate attempts
        locs = locales.split(',', QString.SkipEmptyParts)

        #Search for exact match
        for loc in locs:
            loc.replace(QRegExp(";.*"), "")
            loc.replace('-', '_')
            localizedName = templateName + "-" + loc.trimmed()
            if (not tried.contains(localizedName)):
                document = self.tryFile(localizedName)
                if (not document.isEmpty()):
                    self.mutex.unlock()
                    return Template(document, localizedName)
                tried.insert(localizedName)

        #Search for correct language but any country
        for loc in locs:
            loc.replace(QRegExp("[;_-].*"), "")
            localizedName = templateName + "-" + loc.trimmed()
            if (not tried.contains(localizedName)):
                document = tryFile(localizedName)
                if (not document.isEmpty()):
                    self.mutex.unlock()
                    return Template(document, localizedName)
                tried.insert(localizedName)

        #Search for default file
        document = tryFile(templateName)
        if (not document.isEmpty()):
            self.mutex.unlock()
            return Template(document, templateName)

        qCritical("TemplateCache: cannot find template %s" % (templateName))
        self.mutex.unlock()
        return Template("", templateName)
