# This project demonstrates how to use QtWebAppLib by including the
# sources into this project.

TARGET = Demo1
TEMPLATE = app
#QT = core network
QT       += core gui
QT       += network webenginewidgets webchannel

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += console

HEADERS += \
           src/requestmapper.h \
           src/controller/dumpcontroller.h \
           src/controller/templatecontroller.h \
           src/controller/formcontroller.h \
           src/controller/fileuploadcontroller.h \
           src/controller/sessioncontroller.h \
           src/controller/webservicecontroller.h \
    src/abstractnoscriptobject.h \
    src/ComponentDevelopment.h \
    src/ComponentRequestResponse.h \
    src/htmlpage.h \
    src/webform.h

SOURCES += src/main.cpp \
           src/requestmapper.cpp \
           src/controller/dumpcontroller.cpp \
           src/controller/templatecontroller.cpp \
           src/controller/formcontroller.cpp \
           src/controller/fileuploadcontroller.cpp \
           src/controller/sessioncontroller.cpp \
           src/controller/webservicecontroller.cpp \
    src/abstractnoscriptobject.cpp \
    src/ComponentDevelopment.cpp \
    src/ComponentRequestResponse.cpp \
    src/htmlpage.cpp

FORMS    += mainwindow.ui

RESOURCES += \
        resources.qrc

OTHER_FILES += etc/* etc/docroot/* etc/templates/* etc/ssl/* logs/* ../readme.txt

#---------------------------------------------------------------------------------------
# The following lines include the sources of the QtWebAppLib library
#---------------------------------------------------------------------------------------

include(../QtWebApp/logging/logging.pri)
include(../QtWebApp/httpserver/httpserver.pri)
include(../QtWebApp/templateengine/templateengine.pri)
# Not used: include(../QtWebApp/qtservice/qtservice.pri)
