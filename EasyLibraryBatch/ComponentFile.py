import os
import distutils.core
import urllib.request
import urllib.parse

class ComponentFile:

  @staticmethod
  def getTxtFromFile(path):
    #urllib..parse.quote_plus(url)
    #response = urllib.request.urlopen(path)
    #html = response.read()
    in_file = open(path, "r")
    text = in_file.read()
    in_file.close()
    return text

  @staticmethod
  def writeFileFromTxt(path, value):
    in_file = open(path, "w")
    in_file.write(value)
    in_file.close()
    return

  @staticmethod
  def getTxtFromFileByUrl(url):
    #urllib..parse.quote_plus(url)
    response = urllib.request.urlopen(url)
    html = response.read()
    return html

  @staticmethod
  def fileRename(pathSource, pathDest):
    os.rename(pathSource, pathDest)

  @staticmethod
  def fileDelete(path):
    os.remove(path)  
    #os.unlink(path)  

  @staticmethod
  def fileExist(path):
    return os.path.isfile(path)  

  @staticmethod
  def directoryExist(folderSource):
    return os.path.isdir(folderSource)  

  @staticmethod
  def copyDirectory(folderSource, folderDest):
    distutils.dir_util.copy_tree(folderSource, folderDest)
