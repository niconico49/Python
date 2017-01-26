import PyV8
from AbstractNoScriptObject import *
from ComponentServer import *
from ComponentThread import *
from ComponentFile import *
from ComponentConnection import *
from ComponentDevelopment import *
from ComponentMail import *

class Engine:
    __iEngine = None

    __firstTime = True
    __scriptingCode = ""

    @staticmethod
    def starter(abstractNoScriptObject):

        path = ComponentServer.getParameter('serverPathInfo')
        languageProgramming = ComponentServer.getParameter('languageProgramming')

        scriptCode = ComponentFile.getTxtFromFile(path + "/Scripts/Deployer.js")

        self = Engine
        abstractNoScriptObject.setComponentEngine(self.__iEngine)
        #g = Global()
        #g.setAbstractNoScriptObject(abstractNoScriptObject)
        #self.__iEngine = PyV8.JSContext(g) 
        self.__iEngine = PyV8.JSContext() 
        self.__iEngine.enter()

        self.__iEngine.locals.AbstractNoScriptObject = abstractNoScriptObject
        self.__iEngine.locals.languageProgramming = languageProgramming

        self.__iEngine.eval(scriptCode)

        scriptCode = self.__iEngine.eval('starter(languageProgramming)')
        #self.__iEngine.leave()
        
        #print (scriptCode)

        self.__scriptingCode = scriptCode

    @staticmethod
    def execute(functionName, abstractNoScriptObject, parameters):
        result = None

        self = Engine

        if (self.__firstTime):
            abstractNoScriptObject.setComponentEngine(self.__iEngine)

            self.__firstTime = False
            self.__iEngine.locals.AbstractNoScriptObject = abstractNoScriptObject
            self.__iEngine.locals.parameters = str(parameters)
            self.__iEngine.eval(self.__scriptingCode)
            result = self.__iEngine.eval(functionName + '(parameters)')
        else:
            self.__iEngine.locals.AbstractNoScriptObject = abstractNoScriptObject
            self.__iEngine.locals.parameters = str(parameters)
            result = self.__iEngine.eval(functionName + '(parameters)')
        return result
    
    @staticmethod
    def scriptEngine(operationType, functionName, abstractNoScriptObject, parameters):
        result = ""
        
        if (operationType == "StarterAndExecute"):
            Engine.starter(abstractNoScriptObject)
            result = Engine.execute(functionName, abstractNoScriptObject, parameters)
        elif (operationType == "Starter"):
            Engine.starter(abstractNoScriptObject)
        elif (operationType == "Execute"):
            result = Engine.execute(functionName, abstractNoScriptObject, parameters)

        return result

    @staticmethod
    def dynamicInvoke(operationType, functionName, abstractNoScriptObject, args):
        result = Engine.scriptEngine(operationType, functionName, abstractNoScriptObject, args)
        return result

    @staticmethod
    def interact(jsonData, iSession, path, operationType):
      ComponentServer.addParameter('serverPathInfo', path)
      
      result = ""
      
      abstractNoScriptObject = AbstractNoScriptObject()
      abstractNoScriptObject.setComponentConnection(ComponentConnection())
      abstractNoScriptObject.setComponentDevelopment(ComponentDevelopment())
      abstractNoScriptObject.setComponentFile(ComponentFile())
      abstractNoScriptObject.setComponentMail(ComponentMail())
      abstractNoScriptObject.setComponentServer(ComponentServer())
      abstractNoScriptObject.setComponentThread(ComponentThread())
      abstractNoScriptObject.setComponentSession(iSession)
      
      internal = Engine.dynamicInvoke(operationType, "execute", abstractNoScriptObject, jsonData)
      
      #result = (string)internal
      result = internal
      
      return result
