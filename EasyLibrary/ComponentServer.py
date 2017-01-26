class ComponentServer:
  __componentServer = {"languageProgramming" : "Python"}

  @staticmethod
  def getDictionary():  
    return ComponentServer.__componentServer   
  
  @staticmethod
  def addParameter(key, value):  
    ComponentServer.__componentServer[key] = value  
  
  @staticmethod
  def getParameter(key):  
    return ComponentServer.__componentServer[key]  
  
  @staticmethod
  def removeParameter(key):
    del ComponentServer.__componentServer[key]  
  
  @staticmethod
  def clearParameter():
    ComponentServer.__componentServer.clear()
