class WebSession:
  
  def WebSession(session):
    self.__session = session

  def setSession(self, session):
    self.__session = session

  def getAttribute(self, key):
    value = None
    if (self.__session.has_key(key)):
      value = self.__session[key] 
    return value
    #return self.__session[key]
  
  def setAttribute(self, key, value):
    self.__session[key] = value
  
  def removeAllAttribute(self):
    self.__session.destroy()
