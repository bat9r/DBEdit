#Import module for MySQL
import pymysql
#Import module for graphs
from graphviz import Digraph
#Module for regular expression
import re

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
        
    def commit (self):
        '''
        Function for saving changes
        '''
        self.__conn.commit()

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
    
    def nameTable (self):
        '''
        Function for get name database
        '''
        return self.__nameTable
        
    def nameDatabase (self):
        '''
        Function for get name database
        '''
        return self.__nameDatabase
        
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
        
class TableProcessor:
    
    def __init__(self, dbMan, matrix):
        self.cursor = MySQL()
        self.matrixNew = matrix
        self.matrixOld = dbMan.getAmendedTable()
        self.dbMan = dbMan
        self.checkMatrix()
        
    def identifyType (self, value):
        '''
        Function: ident type of value for MySQL
        Takes: argument string value,
        Returns: type of this argument (like in MySQL), and index 
        (index means how much big type is it)
        TODO: (may be mistake in date 2017-19-39)
        '''
        value = str(value)
        #Check numbers
        if ( value.replace(',', '.', 1).replace('.', '', 1).isdigit() ):
            #Check integer of float
            if (value.isdigit()):
                value = int(value)
                #Choosing type of integer
                if ( -127 < value and value < 127):
                    return ["TINYINT", '0']
                if ( value == '0' or value == '1'):
                    return ["BOOL", '1']
                if ( -32768 < value and value < 32767):
                    return ["SMALLINT", '2']
                if ( -8388608 < value and value < 8388607):
                    return ["MEDIUMINT", '3']
                if ( -2147483648 < value and value < 2147483647):
                    return ["INT", '4']
                if ( -9223372036854775808 < value and value < 9223372036854775807):
                    return ["BIGINT", '5']
                
            else:
                value = float(value.replace(',', '.', 1))
                if ( (-3.402823466E+38 < value and value < -1.175494351E-38) or
                     ( 1.175494351E-38 < value and value <  3.402823466E+38) ):
                    return ["FLOAT", '10']
                if ( (-1.7976931348623157E+308 < value and value < -2.2250738585072014E-308) or
                     ( 2.2250738585072014E-308 < value and value <  1.7976931348623157E+308) ):
                    return ["DOUBLE", '11']
        #Check dates
        if (value.isalpha() == False):
            patternDate = re.compile(r"^[1-9][0-9][0-9][0-9][-][0-1][0-9][-][0-3][0-9]$")
            patternDatetime = re.compile(r"^[1-9][0-9][0-9][0-9][-][0-1][0-9][-][0-3][0-9] [0-2][0-3][:][0-5][0-9][:]?[0-5]?[0-9]?[.]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?$")
            patternTime = re.compile(r"^[-]?[0-7]?[0-9]?[0-9]?[:][0-5][0-9][:]?[0-5]?[0-9]?[.]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?$")
            if ( patternDate.search(value) ):
                return ["DATE", '20']
            if ( patternDatetime.search(value) ):
                return ["DATETIME", '21']
            if ( patternTime.search(value) ):
                return ["TIME", '22']
        #Check strings
        #TODO add null, and change 0 to NULL in save function main module
        #if (value == "NULL"):
        #    return ["NULL", '-1']
        else:
            return ["VARCHAR("+str(len(value))+")", str(100+len(value))]

    def identifyTypeColumn (self, column):
        '''
        Function: For indentify type of column
        Takes: column = list([item, ..]), without name of column
        Returns : finalType = str(type)
        '''
        finalType = ''
        finalIndex = -10
        
        for item in column:
            tempT = self.identifyType(item)
            if (tempT[1][0] == '2') and (int(finalIndex) < 20):
                finalType = "VARCHAR("+str(20)+")"
            if int(tempT[1]) > finalIndex:
                finalIndex = int(tempT[1])
                finalType = tempT[0]
        return finalType
                
    def tempIdAdd (self):
        '''
        Function create in opened table autoincrement column [1,2,3]
        '''
        tempID = "tempIDColumn"
        
        self.cursor.do("ALTER TABLE "+ str(self.dbMan.nameTable()) + 
                " add "+ tempID +" INT NOT NULL FIRST;")
        self.cursor.do("set @"+ tempID +":=0;")
        self.cursor.do("update "+ str(self.dbMan.nameTable()) + 
                " set "+ tempID + " = (@"+ tempID +" := @"+ tempID +" + 1);")
        return tempID
            
    def tempIdDel (self, tempID):
        '''
        Function delete in opened table autoincrement column
        Takes: name of tempID column
        '''
        self.cursor.do("ALTER TABLE "+ str(self.dbMan.nameTable()) + 
                " drop "+ tempID +" ;")
        
    def changeColumn (self, columnOldName, columnNew, tempID):
        '''
        Function changing column (add new column after old column,
        insert items in new column, delete old column)
        Takes: old column name (str) , new column (list, where [0] 
        element is name of new column, tempID name (str))
        Returns: nothing just change table in DB
        '''
        typeColumn = self.identifyTypeColumn (columnNew[1:])
        #Adding column after old column
        self.cursor.do("ALTER TABLE "+ str(self.dbMan.nameTable()) + 
                " ADD " + str(columnNew[0]) + 
                " " + str(typeColumn) +
                " AFTER " + str(columnOldName) + ";")
        #Insert items in new column
        for i in range(1,len(columnNew)):
            self.cursor.do("UPDATE "+ str(self.dbMan.nameTable()) + 
                    " SET "+ str(columnNew[0]) + 
                    " = '" + str(columnNew[i]) + "'" +
                    " WHERE " + tempID + " = " + str(i) + ";")
        #Drop old column
        self.cursor.do("ALTER TABLE "+ str(self.dbMan.nameTable()) + 
                " DROP " + str(columnOldName) + ";")
        #Saving changes
        self.cursor.commit()
    
    def addColumn (self, columnNew, tempID):
        '''
        Function create new column, after last column and insert items
        from columnNew 
        Takes: column new (list, where name is [0]), and tempID name
        of temporary column (using for indexes)
        Return: nothing, just commit changes in table in DB
        '''
        typeColumn = self.identifyTypeColumn (columnNew[1:])
        #Adding column after last column
        self.cursor.do("ALTER TABLE "+ str(self.dbMan.nameTable()) + 
                " ADD " + str(columnNew[0]) + 
                " " + str(typeColumn) + ";")
        #Insert items in new column
        for i in range(1,len(columnNew)):
            self.cursor.do("UPDATE "+ str(self.dbMan.nameTable()) + 
                    " SET "+ str(columnNew[0]) + 
                    " = '" + str(columnNew[i]) + "'" +
                    " WHERE " + tempID + " = " + str(i) + ";")
        #Saving changes
        self.cursor.commit()
        
    def deleteColumn (self, name):
        '''
        Function delete column by name 
        Takes: name
        Return: nothing, rewriting table
        '''
        #Drop column
        self.cursor.do("ALTER TABLE "+ str(self.dbMan.nameTable()) + 
                " DROP " + str(name) + ";")
        print (name)
        #Saving changes
        self.cursor.commit()

    def checkType (self,i,j):
        '''
        Function check type, is it compatible with type in the table.
        Takes: indexes for matrixNew (i,j)
        Return: True or Falsr (True if compatible)
        '''
        def parseType (typeStr):
            '''
            Fucntion split type on two parts, type and lenght of type
            '''
            typeStr = str(typeStr).lower()
            typePart1 = typeStr.split('(')[0]
            if typePart1 == 'varchar':
                typePart2 = typeStr.split('(')[1].replace(')','')
            else:
                typePart2 = '0'
            return list((typePart1, typePart2))
            
        #Ident current type
        print (self.matrixNew[i][j])
        currentType = str(self.identifyType(self.matrixNew[i][j])[0])
        #Ident previous type
        self.cursor.do("desc " + self.dbMan.nameTable() + ";")
        desc = [list(row) for row in self.cursor.done()]
        for index in range(len(desc)):
            if parseType(desc[index][1])[0] == parseType(currentType)[0]:
                if parseType(currentType)[0] == 'varchar':
                    if parseType(desc[index][1])[1] > parseType(currentType)[1]:
                        return True
                if parseType(currentType)[0] != 'varchar':
                    return True
        
        return False
        
    def changeValue (self, i, j, tempID):
        '''
        Function edit value in table using indexes
        Takes: indexes for matrixNew (i,j) and tempID for coordinates
        '''
        self.cursor.do("UPDATE "+ str(self.dbMan.nameTable()) + 
                    " SET "+ str(self.matrixNew[0][j]) + 
                    " = '" + str(self.matrixNew[i][j]) + "'" +
                    " WHERE " + tempID + " = " + str(i) + ";")
        self.cursor.commit()
        
    def checkColumns (self, tempID):
        '''
        Function for checking names of columns, and edit our type and
        values if necessary.
        Takes: tempID for coordinates
        '''
        #Check every column for deleting
        if len(self.matrixOld[0]) > len(list(filter(bool, self.matrixNew[0]))):
            print(len(self.matrixOld[0]), len(list(filter(bool, self.matrixNew[0]))))
            deleteColumnsNames = []
            for item in self.matrixOld[0]:
                if item not in self.matrixNew[0]:
                    deleteColumnsNames.append(item)
            for name in deleteColumnsNames:
                self.deleteColumn(name)
            return
        #Check every column for changing and adding
        for i in range(len(self.matrixNew[0])):
            if i+1 <= len(self.matrixOld[0]):
                if self.matrixNew[0][i] != self.matrixOld[0][i]:
                    self.changeColumn (
                        #Get columns from matrix for giving
                        self.matrixOld[0][i],
                        list([li[i] for li in self.matrixNew]),
                        #Give name of tempID
                        tempID)
            if i+1 > len(self.matrixOld[0]):
                self.addColumn(list([li[i] for li in self.matrixNew]),
                                tempID)
        
        #Check values in cells
        self.checkValues(tempID)
        
    def checkValues (self, tempID):
        #Update old table
        self.matrixOld = self.dbMan.getAmendedTable()
        #Check values in table
        for i in range(len(self.matrixNew)):
            for j in range(len(self.matrixNew[i])):
                if i+1 <= len(self.matrixOld):
                    if j+1 <= len(self.matrixOld[j]):
                        if str(self.matrixOld[i][j]) != str(self.matrixNew[i][j]):
                            if self.checkType(i,j):
                                self.changeValue(i,j, tempID)
        
    def checkMatrix (self):
        #Update old table
        self.matrixOld = self.dbMan.getAmendedTable()
        #Add temp id column
        try:
            tempID = self.tempIdAdd()
        except pymysql.err.InternalError:
            self.tempIdDel('tempIDColumn')
            tempID = self.tempIdAdd()
            
        #---Delete---
        print ("old/new \n")
        for l in self.matrixOld:
            print (l)
        for r in self.matrixNew:
            print (r)
        #------------
        
        self.checkColumns(tempID)
        
        #Delete column with temp id
        self.tempIdDel(tempID)
