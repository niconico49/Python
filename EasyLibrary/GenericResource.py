class GenericResource:

    def execute(jsonData):
        ComponentServer.addParameter("WebService.type", "Classic")
        ComponentServer.addParameter("WebService.path", "webresources/api/execute")

        path = $_SERVER['DOCUMENT_ROOT']
        operationType = "Execute"
        return Engine.interact(jsonData, new WebSession($_SESSION), path, operationType)
