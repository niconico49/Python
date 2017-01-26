#include <QWebEngineView>
#include "ComponentDevelopment.h"
#include "ComponentRequestResponse.h"
"""
class AbstractNoScriptObject : public QWebEngineView {
    Q_OBJECT
private:
    ComponentDevelopment* componentDevelopment;
    ComponentRequestResponse* componentRequestResponse;
public:
    #AbstractNoScriptObject();
    static AbstractNoScriptObject* getInstance(QString value);
    void setComponentDevelopment(ComponentDevelopment* componentDevelopment);
    void setComponentRequestResponse(ComponentRequestResponse* componentRequestResponse);
#public slots:
    Q_INVOKABLE ComponentDevelopment* getComponentDevelopment();
    Q_INVOKABLE ComponentRequestResponse* getComponentRequestResponse();
    Q_INVOKABLE QString getTest(QString);
"""
#include "abstractnoscriptobject.h"
#include <QTextStream>
from PyQt5.QtWebEngineWidgets import (QWebEngineView)

from ComponentDevelopment import *
from ComponentRequestResponse import *

#AbstractNoScriptObject::AbstractNoScriptObject() {}

class AbstractNoScriptObject(QWebEngineView):

    @staticmethod
    def getInstance(value):
        abstractNoScriptObject = AbstractNoScriptObject()
        abstractNoScriptObject.setComponentDevelopment(ComponentDevelopment())
        componentRequestResponse = ComponentRequestResponse()
        componentRequestResponse.setRequest(value)
        abstractNoScriptObject.setComponentRequestResponse(componentRequestResponse)
        #connect(abstractNoScriptObject, SIGNAL(getComponentDevelopmentSignal()), abstractNoScriptObject, SLOT(getComponentDevelopment()));
        #connect(abstractNoScriptObject, &AbstractNoScriptObject::getComponentDevelopmentSignal, abstractNoScriptObject, &AbstractNoScriptObject::getComponentDevelopment);
        #connect(abstractNoScriptObject, &AbstractNoScriptObject::getTestSignal, abstractNoScriptObject, &AbstractNoScriptObject::getTest);
        return abstractNoScriptObject

    def getComponentDevelopment(self):
        #emit AbstractNoScriptObject::getComponentDevelopmentSignal();
        return self.componentDevelopment

    def setComponentDevelopment(self, componentDevelopment):
        self.componentDevelopment = componentDevelopment

    def getComponentRequestResponse(self):
        return self.componentRequestResponse

    def setComponentRequestResponse(self, componentRequestResponse):
        self.componentRequestResponse = componentRequestResponse
