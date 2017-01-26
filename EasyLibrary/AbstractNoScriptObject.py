class AbstractNoScriptObject:

    def getComponentConnection(self):
        return self.__componentConnection

    def setComponentConnection(self, componentConnection):
        self.__componentConnection = componentConnection

    def getComponentDevelopment(self):
        return self.__componentDevelopment

    def setComponentDevelopment(self, componentDevelopment):
        self.__componentDevelopment = componentDevelopment

    def getComponentFile(self):
        return self.__componentFile

    def setComponentFile(self, componentFile):
        self.__componentFile = componentFile

    def getComponentMail(self):
        return self.__componentMail

    def setComponentMail(self, componentMail):
        self.__componentMail = componentMail

    def getComponentServer(self):
        return self.__componentServer

    def setComponentServer(self, componentServer):
        self.__componentServer = componentServer

    def getComponentThread(self):
        return self.__componentThread

    def setComponentThread(self, componentThread):
        self.__componentThread = componentThread

    def getComponentSession(self):
        return self.__iSession

    def setComponentSession(self, iSession):
        self.__iSession = iSession

    def getComponentEngine(self):
        return self.__iEngine;

    def setComponentEngine(self, iEngine):
        self.__iEngine = iEngine
