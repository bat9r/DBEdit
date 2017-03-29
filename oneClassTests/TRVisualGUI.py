#Import modules for UI
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QApplication,
    QDesktopWidget, QListWidget, QPushButton, QFileDialog, QAbstractItemView)
#Import module for MySQL
import pymysql
#Import module for graphs
from graphviz import Digraph

#Cursor for working with database
_conn = pymysql.connect(host='localhost', user='root', passwd='', db='mysql')

class Graph:
    def __init__(self, tablesList):
        #Create list of relationships between tables
        listOfRelationships = [j for x in [self.findRelationship(i) for i in tablesList if self.findRelationship(i)] for j in x]
        self.drawGraph(listOfRelationships, tablesList)
        print (tablesList)


    def drawGraph(self, listOfRelationships, tableList):
        '''
        Function draws graph using graphviz module
        '''
        graphRelationships = Digraph('Relationships', filename='Relationships.gv')
        graphRelationships.body.append('nodesep="2.0"')
        graphRelationships.body.append('ranksep="2.0"')
        graphRelationships.body.append('lblstyle="above"')
        graphRelationships.attr('node', shape = 'box')
        for name in tableList:
            graphRelationships.node(name)
        for relationship in listOfRelationships:
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
        cursor = _conn.cursor()
        resultList = []
        cursor.execute("show create table " + tableName + ";")
        showCreateTableList = list([i for i in cursor][0])[1].split(" ");
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
        cursor = _conn.cursor()
        names= self.findAllForeignKeyTables(tableName)
        finalList = []
        if len(names) > 1:
            for i in range(0,len(names),2):
                List = []
                cursor.execute("select " + names[i][1] + " from " + names[i][0] + ";")
                column1 = [i for i in cursor]
                cursor.execute("select " + names[i+1][1] + " from " + names[i+1][0] + ";")
                column2 = [i for i in cursor]
                List.append(names[i][0])
                List.append(" -> ".join(self.findOutRelationshipBetweenColumns(column1, column2)))
                List.append(names[i+1][0])
                finalList.append(List)

        return finalList

class TRVisualGUI(QWidget):
    def __init__(self):
        #Initialize father (QWidget) constructor (__init__)
        super().__init__()
        #Function for creating UI
        self.initUI()

    def initUI(self):
        '''
        Function initialize user interface
        '''
        #Set window title, size and put in center
        self.setWindowTitle('Visualize relationships')
        self.resize(400, 300)
        self.moveToCenter()
        #Create labels
        databasesLabel = QLabel('Databases')
        tablesLabel = QLabel('Tables')
        #Center labels in grid cell
        databasesLabel.setAlignment(Qt.AlignCenter)
        tablesLabel.setAlignment(Qt.AlignCenter)
        #Create lists
        self.databasesList = QListWidget()
        self.tablesList = QListWidget()
        #Set selection mode
        self.tablesList.setSelectionMode(QAbstractItemView.MultiSelection)
        #Adding items in databasesList and tablesList
        self.showDatabases()
        #Bind list
        self.databasesList.itemClicked.connect(self.showTables)
        #Create buttom
        makeGraphButton = QPushButton('Make graph')
        #Bind Button
        makeGraphButton.clicked.connect(self.makeGraph)
        #Create grid and set spacing for cells
        grid = QGridLayout()
        grid.setSpacing(10)
        #Add widgets to grid
        grid.addWidget(databasesLabel, 0, 0)
        grid.addWidget(tablesLabel, 0, 1)
        grid.addWidget(self.databasesList, 1, 0)
        grid.addWidget(self.tablesList, 1, 1)
        grid.addWidget(makeGraphButton, 2, 0, 1, 2)
        #Set layout of window
        self.setLayout(grid)
        #Show window
        self.show()

    def makeGraph(self):
        #Get from tablesList selected tables and put their in selectedTablesList
        selectedTablesList = [ i.data() for i in self.tablesList.selectedIndexes()]
        outputGraph = Graph(selectedTablesList)

    def moveToCenter(self):
        '''
        Function put window (self) in center of screen
        '''
        #Get rectangle, geometry of window
        qr = self.frameGeometry()
        #Get resolution monitor, get center dot
        cp = QDesktopWidget().availableGeometry().center()
        #Move rectangle centre in window center
        qr.moveCenter(cp)
        #Move topLeft dot of window in topLeft of rectangle
        self.move(qr.topLeft())

    def showDatabases(self):
        '''
        This function shows all databases and put their in databasesList
        '''
        cursor = _conn.cursor()
        cursor.execute("show databases;")
        for name in cursor:
            self.databasesList.addItem(name[0])
        cursor.close()

    def showTables(self):
        '''
        This function shows all tables, after user click on name of database
        and put their in tablesList. Also this function change database
        (use [db];).
        '''
        self.tablesList.clear()
        cursor = _conn.cursor()
        cursor.execute("use " + str(self.databasesList.currentItem().text()) + ";")
        cursor.execute("show tables;")
        for name in cursor:
            self.tablesList.addItem(name[0])
        cursor.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    trv = TRVisualGUI()
    sys.exit(app.exec_())
