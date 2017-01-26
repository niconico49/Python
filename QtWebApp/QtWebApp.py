import os, sys

lib_path = os.path.abspath('../QtWebApp')
sys.path.append(lib_path)

from WebService import *

class QtWebApp:

  @staticmethod
  def main(args):
    WebService.start(os.getcwd())

QtWebApp.main("")
