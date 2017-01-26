#include <QObject>
#include <iostream>
"""
class ComponentDevelopment : public QObject {
    Q_OBJECT
public:
    Q_INVOKABLE static void displayValue(QString value);
};
"""
#include "ComponentDevelopment.h"
#include <QTextStream>
#include <string>
from PyQt5.QtCore import (QObject, pyqtSlot) 

class ComponentDevelopment(QObject):
    @staticmethod
    @pyqtSlot(str)
    def displayValue(value):
        QTextStream(stdout) << value << "\r\n";
