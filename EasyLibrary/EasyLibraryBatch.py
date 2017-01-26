import os

class EasyLibraryBatch:

    @staticmethod
    def main(args):
        jsonData = ""
        operationType = "StarterAndExecute"
        path = os.getcwd()
        Engine.interact(jsonData, BatchSession({}), path, operationType)
