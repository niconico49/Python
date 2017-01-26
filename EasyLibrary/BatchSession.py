class BatchSession:

  def BatchSession(self, hashMap):
    self.__hashMap = hashMap

  def getAttribute(self, key):
    return self.__hashMap[key]
  
  def setAttribute(self, key, value):
    self.__hashMap[key] = value
  
  def removeAllAttribute(self):
    self.__hashMap.clear()
