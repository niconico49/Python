"""
  Caching template loader, reduces the amount of I/O and improves performance
  on remote file systems. The cache has a limited size, it prefers to keep
  the last recently used files. Optionally, the maximum time of cached entries
  can be defined to enforce a reload of the template file after a while.
  <p>
  In case of local file system, the use of this cache is optionally, since
  the operating system caches files already.
  <p>
  Loads localized versions of template files. If the caller requests a file with the
  name "index" and the suffix is ".tpl" and the requested locale is "de_DE, de, en-US",
  then files are searched in the following order:

  - index-de_DE.tpl
  - index-de.tpl
  - index-en_US.tpl
  - index-en.tpl
  - index.tpl
  <p>
  The following settings are required:
  <code><pre>
  path=../templates
  suffix=.tpl
  encoding=UTF-8
  cacheSize=1000000
  cacheTime=60000
  </pre></code>
  The path is relative to the directory of the config file. In case of windows, if the
  settings are in the registry, the path is relative to the current working directory.
  <p>
  Files are cached as long as possible, when cacheTime=0.
  @see TemplateLoader
"""

from PyQt5.QtCore import (QDateTime, qDebug)

from TemplateLoader import *

#include "templateloader.h"

class TemplateCache(TemplateLoader):

    def __init__(self, settings, parent):
        super(TemplateCache, self).__init__(settings, parent)
        self.cache = {}
        #self.cache.setMaxCost(settings.value("cacheSize", "1000000").toInt())
        #self.cacheTimeout = settings.value("cacheTime", "60000").toInt()
        self.cacheTimeout = int(settings.value("cacheTime", "60000"))
        #qDebug("TemplateCache: timeout=%i, size=%i" % (self.cacheTimeout, self.cache.maxCost())
        qDebug("TemplateCache: timeout=%i" % (self.cacheTimeout))

    def tryFile(self, localizedName):
        now = QDateTime.currentMSecsSinceEpoch()
        #search in cache
        qDebug("TemplateCache: trying cached %s" % (localizedName))
        entry = self.cache[localizedName]
        if (entry and (self.cacheTimeout == 0 or entry.created > now - self.cacheTimeout)):
            return entry.document
        #search on filesystem
        entry = {}
        entry["created"] = now
        entry["document"] = TemplateLoader.tryFile(localizedName)
        #Store in cache even when the file did not exist, to remember that there is no such file
        self.cache[localizedName] = entry
        return entry.document
