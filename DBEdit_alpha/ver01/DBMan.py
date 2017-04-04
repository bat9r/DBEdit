#Import module for MySQL
import pymysql
#Import module for graphs
from graphviz import Digraph

class MySQL:
    '''
    Class for working with MySQL
    '''
    #Cursor for working with database
    __conn = pymysql.connect(host='localhost', user='root', passwd='', db='mysql')
    __lastExecute = None
    
    def __init__(self):
        pass
        
    def do (self, command):
        '''
        Function execute commands for databases
        '''
        #Open cursor for working with database
        cur = self.__conn.cursor()
        #Execute command
        cur.execute(command)
        #Save last result from command
        self.__lastExecute = cur
        #Closing cursor
        cur.close()
        
    def done (self):
        '''
        Function return result of last command
        '''
        return self.__lastExecute

class Relationship:
    __listOfRelationships = []
    __tablesList = []
    
    def __init__(self, tablesList):
        #Create atribute class
        self.__tablesList = tablesList
        self.__listOfRelationships = [j for x in [self.findRelationship(i) for i in tablesList if self.findRelationship(i)] for j in x]

    def getListOfRelationships(self):
        return self.__listOfRelationships
        
    def drawGraph(self):
        '''
        Function draws graph using graphviz module
        '''
        print (self.__listOfRelationships)
        graphRelationships = Digraph('Relationships', filename='Relationships.gv')
        graphRelationships.body.append('nodesep="2.0"')
        graphRelationships.body.append('ranksep="2.0"')
        graphRelationships.body.append('lblstyle="above"')
        graphRelationships.attr('node', shape = 'box')
        for name in self.__tablesList:
            graphRelationships.node(name)
        for relationship in self.__listOfRelationships:
            graphRelationships.edge(relationship[0], relationship[2], label = relationship[1])

        graphRelationships.view()

    def formatWord(self, word):
        '''
        Function delete from string bad symbols and new linew, tabs ...
        '''
        badSymbols = "!@.,/#$%:;'?()-`"
        for char in badSymbols:
            word = word.replace(char, "")
        return word.strip()

    def findOutRelationshipBetweenColumns (self, column1, column2):
        '''
        Function check relationships between two input columns and return list
        with type of relationship.
        '''
        def manyOrOne(checkList):
            for i in checkList:
                if i > 1:
                    return (u"\u221E")
            else:
                return ('1')

        checkListForColumn1 = [0 for i in column1]
        checkListForColumn2 = [0 for i in column2]
        for i in range(len(column1)):
            for j in range(len(column2)):
                if column1[i] == column2[j]:
                    checkListForColumn1[i]+=1
        for i in range(len(column2)):
            for j in range(len(column1)):
                if column2[i] == column1[j]:
                    checkListForColumn2[i]+=1
        resultList = []
        resultList.append(manyOrOne(checkListForColumn2))
        resultList.append(manyOrOne(checkListForColumn1))
        return resultList

    def findAllForeignKeyTables(self, tableName):
        '''
        Function accepts name of the table, return foreign tables and columns.
        tableName -> [[tableName,foreignCol], [tableName2, referencesCol] ...]
        '''
        cursor = MySQL()
        resultList = []
        cursor.do("show create table " + tableName + ";")
        showCreateTableList = list([i for i in cursor.done()][0])[1].split(" ");
        for i in range(len(showCreateTableList)):
            if showCreateTableList[i] == 'FOREIGN':
                resultList.append([tableName,self.formatWord(showCreateTableList[i+2])])
            if showCreateTableList[i] == 'REFERENCES':
                resultList.append([self.formatWord(showCreateTableList[i+1]), self.formatWord(showCreateTableList[i+2])])
        return resultList

    def findRelationship (self, tableName):
        '''
        Function findAllForeignKeyTables get columns from tables and compare their
        using function findOutRelationshipBetweenColumns.
        return [table1, [relationships, ..], table2]
        '''
        cursor = MySQL()
        names= self.findAllForeignKeyTables(tableName)
        finalList = []
        if len(names) > 1:
            for i in range(0,len(names),2):
                List = []
                cursor.do("select " + names[i][1] + " from " + names[i][0] + ";")
                column1 = [i for i in cursor.done()]
                cursor.do("select " + names[i+1][1] + " from " + names[i+1][0] + ";")
                column2 = [i for i in cursor.done()]
                List.append(names[i][0])
                List.append(" -> ".join(self.findOutRelationshipBetweenColumns(column1, column2)))
                List.append(names[i+1][0])
                finalList.append(List)

        return finalList
  
class TableProcessor:
    
    def __init__(self, databaseObj):
        self.matrix = databaseOnj.getTable()
        
    def identifyType (self, value):
        '''
        Function: ident type of value for MySQL
        Takes: argument string value,
        Returns: type of this argument (like in MySQL)
        TODO: (may be mistake in date 2017-19-39)
        '''
        #Check numbers
        if ( value.replace(',', '.', 1).replace('.', '', 1).isdigit() ):
            #Check integer of float
            if (value.isdigit()):
                value = int(value)
                #Choosing type of integer
                if ( -127 < value and value < 127):
                    return "TINYINT"
                if ( value == '0' or value == '1'):
                    return "BOOL"
                if ( -32768 < value and value < 32767):
                    return "SMALLINT"
                if ( -8388608 < value and value < 8388607):
                    return "MEDIUMINT"
                if ( -2147483648 < value and value < 2147483647):
                    return "INT"
                if ( -9223372036854775808 < value and value < 9223372036854775807):
                    return "BIGINT"
                
            else:
                value = float(value.replace(',', '.', 1))
                if ( (-3.402823466E+38 < value and value < -1.175494351E-38) or
                     ( 1.175494351E-38 < value and value <  3.402823466E+38) ):
                    return "FLOAT"
                if ( (-1.7976931348623157E+308 < value and value < -2.2250738585072014E-308) or
                     ( 2.2250738585072014E-308 < value and value <  1.7976931348623157E+308) ):
                    return "DOUBLE"
        #Check dates
        if (value.isalpha() == False):
            patternDate = re.compile(r"^[1-9][0-9][0-9][0-9][-][0-1][0-9][-][0-3][0-9]$")
            patternDatetime = re.compile(r"^[1-9][0-9][0-9][0-9][-][0-1][0-9][-][0-3][0-9] [0-2][0-3][:][0-5][0-9][:]?[0-5]?[0-9]?[.]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?$")
            patternTime = re.compile(r"^[-]?[0-7]?[0-9]?[0-9]?[:][0-5][0-9][:]?[0-5]?[0-9]?[.]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?$")
            if ( patternDate.search(value) ):
                return "DATE"
            if ( patternDatetime.search(value) ):
                return "DATETIME"
            if ( patternTime.search(value) ):
                return "TIME"
        #Check strings
        if (value == ""):
            return "NULL"
        else:
            return "VARCHAR("+str(len(value))+")"

    def transformForPrinting():
        pass

class DBM (Relationship):
    __nameDatabase = ""
    __nameTable = ""

    def __init__ (self):
        #Opening cursor for working with database
        self.cursor = MySQL()
        
    def relationshipsList (self):
        '''
        Function returns list with relationships of table
        '''
        Relationship.__init__(self, [self.__nameTable])
        return self.findAllForeignKeyTables(self.__nameTable)
    
    def relationshipsGraph (self, tablesList):
        '''
        Function build Graph which reflects the relationships
        between tablesList
        '''
        Relationship.__init__(self, tablesList)
        self.drawGraph()
        
    def database (self, nameDatabase):
        '''
        Function for choosing database
        '''
        self.__nameDatabase = nameDatabase
        self.cursor.do('use ' + self.__nameDatabase + ';')
    
    def table (self, nameTable):
        '''
        Function for edit name database
        '''
        self.__nameTable = nameTable
       
    def getListNamesTables (self):
        '''
        Function returns list of names all tables
        '''
        self.cursor.do("show tables;")
        return list( [ name[0] for name in self.cursor.done() ])
        
    def getListNamesDatabases (self):
        '''
        Function returns list of names all databases
        '''
        self.cursor.do("show databases;")
        return list([ name[0] for name in self.cursor.done() ])
        
    def getColumnsNames (self):
        '''
        Function returns list of columns names
        '''
        self.cursor.do('show columns from '+ self.__nameTable + ';')
        return list([ name[0] for name in self.cursor.done() ])
            
    def getTable (self):
        '''
        Function: get from MySQL and convert database table
        Takes: argument name of needed table,
        Returns: table in matrix view
        '''
        #MySQL command Get table
        self.cursor.do('select * from ' + self.__nameTable + ';')
        #Get table like matrix
        matrix = [list(row) for row in self.cursor.done()]
        #Returning table-matrix
        return matrix
        
    def getAmendedColumnsNames (self):
        '''
        Function return columns names with relationships (in text format,
        added in names)
        '''
        columnsNamesList = self.getColumnsNames()
        relationshipList = self.relationshipsList()
        for i in range(len(self.getColumnsNames())):
            for j in range(len(relationshipList)):
                if (columnsNamesList[i] == relationshipList[j][1]):
                    columnsNamesList[i] += " << "+str(relationshipList[j+1][1])+", "+str(relationshipList[j+1][0])
        return columnsNamesList

    def getAmendedTable (self):
        '''
        Function return matrix columns names with relationships and 
        table values in matrix look
        '''
        matrix = self.getTable()
        matrix.insert(0, self.getAmendedColumnsNames())
        return matrix
        
