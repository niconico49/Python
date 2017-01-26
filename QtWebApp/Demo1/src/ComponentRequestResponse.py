#include <QObject>
"""
class ComponentRequestResponse : public QObject {
    Q_OBJECT
private:
    QString request;
    QString response;
public:
    Q_INVOKABLE void setRequest(QString value);
    Q_INVOKABLE QString getRequest();
    Q_INVOKABLE void setResponse(QString value);
    Q_INVOKABLE QString getResponse();
};
"""
#include "ComponentRequestResponse.h"
from PyQt5.QtCore import (QObject, pyqtSlot)

class ComponentRequestResponse(QObject):

    @pyqtSlot(str)
    def setRequest(self, value):
        self.request = value

    @pyqtSlot(result = str)
    def getRequest(self):
        return self.request

    @pyqtSlot(str)
    def setResponse(self, value):
        self.response = value

    @pyqtSlot(result = str)
    def getResponse(self):
        return self.response
