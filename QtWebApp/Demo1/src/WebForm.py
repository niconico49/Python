#include <QtWebEngineWidgets>

from PyQt5.QtCore import (pyqtSignal, pyqtSlot)
from PyQt5.QtWebEngineWidgets import (QWebEngineView)
from PyQt5.QtGui import (QCloseEvent)

#gui component holder which will be moved to main thread
class WebForm(QWebEngineView): 
  closeEvent = pyqtSignal(QCloseEvent)

  @pyqtSlot()
  def finish(self):
    self.closeEvent.emit(QCloseEvent())
