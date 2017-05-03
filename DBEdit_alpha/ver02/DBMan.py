# Import module for MySQL
import pymysql
# Import module for graphs
from graphviz import Digraph
# Module for regular expression
import re
from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem,
                             QAbstractScrollArea)

class MySQL:
    """
    Class for working with MySQL
    """
    # Cursor for working with database
    __conn = pymysql.connect(host='localhost', user='root', passwd='',
                             db='mysql')
    __lastExecute = None

    def __init__(self):
        pass

    def do(self, command):
        """
        Function execute commands for databases
        """
        # Open cursor for working with database
        cur = self.__conn.cursor()
        # Execute command
        cur.execute(command)
        # Save last result from command
        self.__lastExecute = cur
        # Closing cursor
        cur.close()

    def commit(self):
        """
        Function for saving changes
        """
        self.__conn.commit()

    def done(self):
        """
        Function return result of last command
        """
        return self.__lastExecute


class Relationship:
    __listOfRelationships = []
    __tablesList = []

    def __init__(self, tablesList):
        # Create atribute class
        self.__tablesList = tablesList
        self.__listOfRelationships = [j for x in
                                      [self.findRelationship(i) for i in
                                       tablesList if
                                       self.findRelationship(i)] for j
                                      in x]

    def getListOfRelationships(self):
        return self.__listOfRelationships

    def drawGraph(self):
        """
        Function draws graph using graphviz module
        """
        print(self.__listOfRelationships)
        graphRelationships = Digraph('Relationships',
                                     filename='Relationships.gv')
        graphRelationships.body.append('nodesep="2.0"')
        graphRelationships.body.append('ranksep="2.0"')
        graphRelationships.body.append('lblstyle="above"')
        graphRelationships.attr('node', shape='box')
        for name in self.__tablesList:
            graphRelationships.node(name)
        for relationship in self.__listOfRelationships:
            graphRelationships.edge(relationship[0], relationship[2],
                                    label=relationship[1])

        graphRelationships.view()

    def formatWord(self, word):
        """
        Function delete from string bad symbols and new linew, tabs ...
        """
        badSymbols = "!@.,/#$%:;'?()-`"
        for char in badSymbols:
            word = word.replace(char, "")
        return word.strip()

    def findOutRelationshipBetweenColumns(self, column1, column2):
        """
        Function check relationships between two input columns and
        return list.
        with type of relationship.
        """

        def manyOrOne(checkList):
            for i in checkList:
                if i > 1:
                    return u"\u221E"
            else:
                return '1'

        checkListForColumn1 = [0 for i in column1]
        checkListForColumn2 = [0 for i in column2]
        for i in range(len(column1)):
            for j in range(len(column2)):
                if column1[i] == column2[j]:
                    checkListForColumn1[i] += 1
        for i in range(len(column2)):
            for j in range(len(column1)):
                if column2[i] == column1[j]:
                    checkListForColumn2[i] += 1
        resultList = [manyOrOne(checkListForColumn2),
                      manyOrOne(checkListForColumn1)]
        return resultList

    def findAllForeignKeyTables(self, tableName):
        """
        Function accepts name of the table, return foreign tables 
        and columns.
        tableName -> [[tableName,foreignCol], 
                      [tableName2, referencesCol] ...]
        """
        cursor = MySQL()
        resultList = []
        cursor.do("show create table " + tableName + ";")
        showCreateTableList = list([i for i in cursor.done()][0])[
            1].split(" ")
        for i in range(len(showCreateTableList)):
            if showCreateTableList[i] == 'FOREIGN':
                resultList.append([tableName, self.formatWord(
                    showCreateTableList[i + 2])])
            if showCreateTableList[i] == 'REFERENCES':
                resultList.append(
                    [self.formatWord(showCreateTableList[i + 1]),
                     self.formatWord(showCreateTableList[i + 2])])
        return resultList

    def findRelationship(self, tableName):
        """
        Function findAllForeignKeyTables get columns from tables and
        compare their using function findOutRelationshipBetweenColumns.
        return [table1, [relationships, ..], table2]
        """
        cursor = MySQL()
        names = self.findAllForeignKeyTables(tableName)
        finalList = []
        if len(names) > 1:
            for i in range(0, len(names), 2):
                List = []
                cursor.do("select " + names[i][1] + " from " + names[i][
                    0] + ";")
                column1 = [i for i in cursor.done()]
                cursor.do("select " + names[i + 1][1] + " from " +
                          names[i + 1][0] + ";")
                column2 = [i for i in cursor.done()]
                List.append(names[i][0])
                List.append(" -> ".join(
                    self.findOutRelationshipBetweenColumns(column1,
                                                           column2)))
                List.append(names[i + 1][0])
                finalList.append(List)

        return finalList


class DBM(Relationship, MySQL):
    __nameDatabase = ""
    __nameTable = ""

    def __init__(self):
        # Opening cursor for working with database
        MySQL.__init__(self)

    def getNameTable(self):
        """
        Function for get name database
        """
        return self.__nameTable

    def getNameDatabase(self):
        """
        Function for get name database
        """
        return self.__nameDatabase

    def putNameDatabase(self, nameDatabase):
        """
        Function for choosing database
        """
        self.__nameDatabase = nameDatabase
        self.do('use ' + self.__nameDatabase + ';')

    def putNameTable(self, nameTable):
        """
        Function for edit name database
        """
        self.__nameTable = nameTable

    def relationshipsList(self):
        """
        Function returns list with relationships of table
        """
        Relationship.__init__(self, [self.__nameTable])
        return self.findAllForeignKeyTables(self.__nameTable)

    def relationshipsGraph(self, tablesList):
        """
        Function build Graph which reflects the relationships
        between tablesList
        """
        Relationship.__init__(self, tablesList)
        self.drawGraph()

    def getListNamesTables(self):
        """
        Function returns list of names all tables
        """
        self.do("show tables;")
        return list([name[0] for name in self.done()])

    def getListNamesDatabases(self):
        """
        Function returns list of names all databases
        """
        self.do("show databases;")
        return list([name[0] for name in self.done()])

    def getColumnsNames(self):
        """
        Function returns list of columns names
        """
        self.do('show columns from ' + self.__nameTable + ';')
        return list([name[0] for name in self.done()])

    def getTable(self):
        """
        Function: get from MySQL and convert database table
        Takes: from DBMan argument name of needed table
        Returns: table in matrix view
        """
        # MySQL command Get table
        self.do('select * from ' + self.__nameTable + ';')
        # Get table like matrix
        matrix = [list(row) for row in self.done()]
        # Returning table-matrix
        return matrix

    def colNameAmendedForeign(self, name):
        """
        Function check relationships for name of column  
        :return: amended name of column
        """
        relationshipList = self.relationshipsList()
        for j in range(len(relationshipList)):
            if (name == relationshipList[j][1]):
                name = "$ " + name + " << " + str(
                    relationshipList[j + 1][1]) + ", " + str(
                    relationshipList[j + 1][0])
                return name
        return False

    def colNameAmendedAutoIncrement(self, name):
        self.do("show create table " + self.__nameTable + ";")
        createInfo = list([i for i in self.done()][0])[1].split(" ")
        for i in range(len(createInfo)):
            try:
                if ((re.sub(r"\W", "", createInfo[i]) == name) and
                    (re.sub(r",\n", "", createInfo[i+4]) == "AUTO_INCREMENT")):
                    return "$ " + name + " << AUTO"
            except IndexError:
                return False
        return False

    def getColumnsAmendedNames(self):
        """
        Function return columns names with amended names (like 
        relationships or autoincrement)
        (in text format, added in names)
        """
        columnsNamesList = self.getColumnsNames()
        for i in range(len(self.getColumnsNames())):
            if (self.colNameAmendedForeign(columnsNamesList[i])):
                columnsNamesList[i] = self.colNameAmendedForeign(
                    columnsNamesList[i])
            if (self.colNameAmendedAutoIncrement(columnsNamesList[i])):
                columnsNamesList[i] = self.colNameAmendedAutoIncrement(
                    columnsNamesList[i])

        return list(columnsNamesList)

    def getColumnByName(self, columnName):
        """
        Get column from current table by name
        :param columnName: str(name of column) 
        :return: list (values from column)
        """
        indexColumn = self.getColumnsNames().index(columnName)
        return [row(indexColumn) in self.getTable()]


class TableParser:
    def __init__(self, DBManCurrent):
        self.DBManNew = None
        self.DBManOld = DBManCurrent

    def save(self, tableWidget):
        self.matrix = self.getMatrixValuesFromTable(
            self.getMatrixItemsFromTable(tableWidget)
        )
        self.createTempTable()
        self.matrix = self.getMatrixValuesFromTable(
            self.getMatrixItemsFromTable(tableWidget)
        )
        self.addRows()
        self.supersedeTable()

        # ---Delete---
        for i in self.matrix:
            print(i)
        # ------------

    def writeTable(self, tableWidget, tableNameLabel):
        """
        Function print table from DBM in DBEditGUI tableWidget
        """
        tableNameLabel.setText(
            self.DBManOld.getNameDatabase() + ', ' +
            self.DBManOld.getNameTable())
        table = self.DBManOld.getTable()
        table.insert(0, self.DBManOld.getColumnsAmendedNames())
        columnCount = len(table[0])
        rowCount = len(table)
        tableWidget.setColumnCount(columnCount)
        tableWidget.setRowCount(rowCount)
        for rowI in range(rowCount):
            for colI in range(columnCount):
                tableWidget.setItem(rowI, colI, QTableWidgetItem(
                    str(table[rowI][colI])))
        # Changes cells size for fitting to content
        tableWidget.setSizeAdjustPolicy(
            QAbstractScrollArea.AdjustToContents)
        tableWidget.resizeColumnsToContents()
        # Do table bigger (for scrolling)
        for i in range(10):
            if i < tableWidget.columnCount():
                tableWidget.insertColumn(
                    tableWidget.columnCount())
        for j in range(20):
            if j < tableWidget.rowCount():
                tableWidget.insertRow(tableWidget.rowCount())

    def getMatrixItemsFromTable(self, tableWidget):
        """
        Function get values from tableWidget in matrix view end 
        returns it.
        :return: Matrix QTableWidgetItem without empty rows and columns.
        """

        def allIsNone(l):
            """
            Check is all values in l is None
            :param l: lis(list of values)
            :return: True if all values is None
            """
            r = True
            for i in l:
                if i is not None:
                    r = False
            return r

        def column(i, m):
            """
            Get column from matrix
            :param i: index of column
            :param m: matrix
            :return: list(column)
            """
            return [row[i] for row in m]

        # Get matrix items objects
        w = tableWidget.columnCount()
        h = tableWidget.rowCount()
        matrix = [[tableWidget.item(j, i)
                   for i in range(w)]
                  for j in range(h)]
        # Create matrix without None rows
        m = [row for row in matrix if not allIsNone(row)]
        # Create matrix without None columns
        mm = zip(*[column(i, m)
                   for i in range(w)
                   if not allIsNone(column(i, m))])
        return mm

    def getMatrixValuesFromTable(self, matrixItems):
        matrixValues = []
        for rowItems in matrixItems:
            rowValues = []
            for item in rowItems:
                if item is not None:
                    if item.text() == "":
                        rowValues.append(0)
                    else:
                        rowValues.append(item.text())
                else:
                    rowValues.append(0)
            matrixValues.append(rowValues)
        #Delete row where all items == 0
        resultMatrix = []
        for row in matrixValues:
            if all(i==0 for i in row):
                continue
            if all(i == "None" for i in row):
                continue
            else:
                resultMatrix.append(row)
        #Delete columns where name int(0)
        for nameCol in resultMatrix[0]:
            if nameCol == 0:
                for i in range(len(resultMatrix)):
                    del resultMatrix[i][-1]

        return resultMatrix

    def getColumn(self, columnName):
        indexColumn = self.matrix[0].index(columnName)
        return [row[indexColumn] for row in self.matrix][1:]

    def uniqueNameTable(self):
        """
        Create unique name for table
        :return: str(another name as in list names tables)
        """
        nameTable = self.uniqueName(self.DBManOld.getListNamesTables())
        return str(nameTable)

    def uniqueName(self, namesList):
        """
        Create unique name
        :param namesList: list(names)
        :return: str(another name as in list)
        """

        def findUniqueName(uniName, namesList):
            count = 0
            while True:
                if uniName in namesList:
                    uniName += str(count)
                    count += 1
                else:
                    break
            return uniName

        uniName = "tempName"
        tempName = findUniqueName(uniName, namesList)
        return str(tempName)

    def identifyType(self, value):
        """
        Function: ident type of value for MySQL
        :param value: 
        :return: list[type of this argument (like in MySQL), len of type, 
        index(means how much big type is it]
        TODO: (may be mistake in date 2017-19-39)
        """

        value = str(value)
        # Check numbers
        if (value.replace(',', '.', 1).replace('.', '', 1).isdigit()):
            # Check integer of float
            if (value.isdigit()):
                value = int(value)
                # Choosing type of integer
                if (-127 < value and value < 127):
                    return ["TINYINT", '0']
                if (value == '0' or value == '1'):
                    return ["BOOL", '1']
                if (-32768 < value and value < 32767):
                    return ["SMALLINT", '2']
                if (-8388608 < value and value < 8388607):
                    return ["MEDIUMINT", '3']
                if (-2147483648 < value and value < 2147483647):
                    return ["INT", '4']
                if ((-9223372036854775808 < value) and
                        (value < 9223372036854775807)):
                    return ["BIGINT", '5']

            else:
                value = float(value.replace(',', '.', 1))
                if (((-3.402823466E+38 < value) and
                         (value < -1.175494351E-38))
                    or
                        ((1.175494351E-38 < value) and
                             (value < 3.402823466E+38))):
                    return ["FLOAT", '10']
                if (((-1.7976931348623157E+308 < value) and
                         (value < -2.2250738585072014E-308))
                    or
                        ((2.2250738585072014E-308 < value) and
                             (value < 1.7976931348623157E+308))):
                    return ["DOUBLE", '11']
        # Check dates
        if (value.isalpha() == False):
            patternDate = re.compile(
                r"^[1-9][0-9][0-9][0-9][-][0-1][0-9][-][0-3][0-9]$")
            patternDatetime = re.compile(
                r"^[1-9][0-9][0-9][0-9][-][0-1][0-9][-][0-3][0-9]"
                r" [0-2][0-3][:][0-5][0-9][:]?[0-5]?[0-9]?[.]?"
                r"[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?$")
            patternTime = re.compile(
                r"^[-]?[0-7]?[0-9]?[0-9]?[:][0-5][0-9][:]?[0-5]?[0-9]"
                r"?[.]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?[0-9]?$")
            if (patternDate.search(value)):
                return ["DATE", '20']
            if (patternDatetime.search(value)):
                return ["DATETIME", '21']
            if (patternTime.search(value)):
                return ["TIME", '22']
        # Check strings
        else:
            return ["VARCHAR(" + str(len(value)+1) + ")",
                    str(100 + len(value))]

    def identifyListValues(self, values):
        """
        Identify types of values in list
        :param values: list(values)
        :return: str(type with largest index)
        """
        index = -1
        resultType = None
        for value in values:
            tempType = self.identifyType(value)
            if int(tempType[1]) > index:
                index = int(tempType[1])
                resultType = tempType[0]
        return resultType

    def identifyTypeColumnValues(self, nameTable, nameColumn):
        """
        Identify type (from MySQL) of column by name
        :param nameTable: name of table
        :param nameColumn: name of column
        :return: str(type)
        """
        DBManForeign = DBM()
        DBManForeign.putNameDatabase(self.DBManOld.getNameDatabase())
        DBManForeign.putNameTable(nameTable)
        DBManForeign.do("desc " + DBManForeign.getNameTable() + ";")
        description = [list(row) for row in DBManForeign.done()]
        for descObj in description:
            if nameColumn == descObj[0]:
                return descObj[1]

    def identAutoIncrColumn(self, nameColumn):
        """
        Function create part of sql request
        :param nameColumn: str(name of column)
        :return: part of sql request
        """
        pattern = re.compile(r"^[$]\s\w+\s[<][<]\s[A][U][T][O]$")
        if (pattern.search(nameColumn)):
            return (nameColumn.split(" ")[1] + " " +
                    self.identifyListValues(
                        self.getColumn(nameColumn)) +
                    " AUTO_INCREMENT PRIMARY KEY, ")
        else:
            return False

    def identInheritColumn(self, nameColumn):
        """
        Function ident foreign key format
        :param nameColumn: str(name of column)
        :return: part of sql request str([name of column][type], 
        FOREIGN KEY [name of column] REFERENCES 
        [name external table]([name external column]))
        """
        pattern = re.compile(r"^[$]\s\w+\s[<][<]\s\w+[,]\s\w+$")
        if (pattern.search(nameColumn)):
            parNameCol = str(nameColumn.split(" ")[1])
            parNameColRef = str(re.sub(",", "",
                                       nameColumn.split(" ")[3]))
            parNameTableRef = str(nameColumn.split(" ")[4])
            parTypeColRef = str(self.identifyTypeColumnValues(
                parNameTableRef, parNameColRef))
            resList = str(parNameCol + " " + parTypeColRef + ", ")
            resList+=str("FOREIGN KEY (" + parNameCol +
                           ") REFERENCES " + parNameTableRef +
                           "(" + parNameColRef + "), ")
            return resList
        else:
            return False

    def identNormalColumn(self, nameColumn):
        """
        Ident normal format for column
        :param nameColumn: str(name of column)
        :return: str([name of column][type])
        """
        pattern = re.compile(r"^\w+$")
        if (pattern.search(nameColumn)):
            return (nameColumn + " " +
                    self.identifyListValues(self.getColumn(nameColumn))+
                    ", ")
        else:
            return False

    def typeColumn(self, nameColumn):
        """
        Calls all function for ident format.
        :param nameColumn: str(name column from matrix)
        :return: srt(part of sql request) ([[name column][type]])
        and (foreign and increment)
        """
        checks = [self.identAutoIncrColumn(nameColumn),
                  self.identInheritColumn(nameColumn),
                  self.identNormalColumn(nameColumn)]
        for r in checks:
            if r:
                return r

    def addColumns(self):
        """
        Function join result from function typeColumn
        :return: str(part of sql request) ([[name column][type]], )
        and (foreign and increment)
        """
        resRequest = ["("]
        for nameCol in self.matrix[0]:
            if (nameCol is None) or (nameCol == "") or (nameCol == 0):
                continue
            else:
                resRequest.append(self.typeColumn(nameCol))
        resRequest[-1] = re.sub(", ", " ", resRequest[-1])
        resRequest.append(");")
        return "".join(resRequest)

    def createTempTable(self):
        """
        Create temporary table for working with it
        :return: 
        """
        self.DBManNew = DBM()
        self.DBManNew.putNameDatabase(self.DBManOld.getNameDatabase())
        self.DBManNew.putNameTable(self.uniqueNameTable())
        self.DBManNew.do("CREATE TABLE " +
                         self.DBManNew.getNameTable()+ " " +
                         self.addColumns())

    def addRows(self):
        """
        Add rows in table from self.matrix(qtablewidget)
        :return: 
        """
        for row in self.matrix[1:]:
            tempListCols = []
            tempListVals = []
            for i in range(len(row)):
                if ((row[i] != 0) and
                    (i < len(self.DBManNew.getColumnsNames()))):
                    tempListCols.append(
                        self.DBManNew.getColumnsNames()[i])
                    tempListVals.append(str(row[i]))
            self.DBManNew.do(self.addRow(tempListCols, tempListVals))
        self.DBManNew.commit()

    def addRow(self, listCols, listValues):
        """
        Create part of request for adding row 
        :param listCols: list(cols which need add values)
        :param listValues: list(values which need to add)
        :return: part of request str(INSERT INTO [name table]
        ([columnName1], [columnName2]) VALUES ([value1], [value2]);)
        """
        colNames = ", ".join(listCols)
        colNames = "(" + colNames + ")"
        values = re.sub("\[", "", str(listValues))
        values = re.sub("\]", "", values)
        values = "(" + values + ")"
        request = str("INSERT INTO " + self.DBManNew.getNameTable() +
                      " " + colNames + " VALUES " + values + ";")
        return request

    def supersedeTable(self):
        """
        Delete old table and rename temporary to old 
        :return: None
        """
        self.DBManNew.do("drop table " +
                         self.DBManOld.getNameTable() + ";")
        self.DBManNew.do("RENAME TABLE " +
                         self.DBManNew.getNameTable() + " TO " +
                         self.DBManOld.getNameTable() + " ;")

