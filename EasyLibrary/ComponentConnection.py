import pyodbc

class ComponentConnection:
    def getInstance(self):
        self = ComponentConnection()
        self.__arrayList = []
        return self   

    def open(self, connectionString):
        self.__connection = pyodbc.connect(connectionString)

    def bindParameter(self, i, value):
        self.__arrayList.append(value)

    def prepareStatement(self, sql):
        self.__sql = sql

    def execute(self):
        self.__cursor = self.__connection.cursor()
        self.__cursor.execute(self.__sql, self.__arrayList)

    def executeQuery(self):
        self.execute()

    def executeNonQuery(self):
        rowCount = -1
        self.execute()
        rowCount = self.__cursor.rowcount
        return rowCount

    def close(self):
        if(self.__cursor):
            self.__cursor.close()
    
        self.__connection.close()

    def isBof(self):
        result = True
        if (self.__cursor):
          result = False
        return result

    def isEof(self):
        result = True
        if (self.__cursor):
          result = False
        return result

    def moveNext(self):
        self.__row = self.__cursor.fetchone()

        result = False
        if (self.__row):
          result = True

        return result

    def columnCount(self):
        return len(self.__cursor.description)

    def columnName(self, i):
        return str(self.__cursor.description[i][0]) 

    def columnType(self, i):
        return str(self.__cursor.description[i][1]) 
    
    def columnValue(self, i):
        #return self.__row[i]

        fieldName = self.columnName(i)
        value = self.__row[i]

        if (value):
            columnType = self.columnType(i)
            
            import datetime
            if (columnType == "<class 'datetime.datetime'>"):
                value = value.isoformat()
            elif (columnType == "<class 'datetime.date'>"):
                value = value.isoformat()
            elif (columnType == "<class 'datetime.time'>"):
                value = value.isoformat()

        if (value == None):
            value = ""

        return value
