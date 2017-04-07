#Import modules for UI
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QApplication,
    QDesktopWidget, QListWidget, QPushButton, QFileDialog, QAbstractItemView,
    QAction, QMenuBar, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout)
#Module for regular expression
import re
#Our module
from DBMan import DBM

class DBEditGUI (QMainWindow):
    
    def __init__ (self, dbmObj):
        #Initialize father (QWidget) constructor (__init__)
        super().__init__()
        #DELETE THIS
        global pself
        pself = self
        #Function for creating UI
        self.dbMan = dbmObj
        self.initUI()
    
    def initUI (self):
        '''
        Function initialize user interface
        '''
        #Set window title, size and put in center
        self.setWindowTitle('DBEdit')
        self.resize(900, 600)
        self.moveToCenter()
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)
        
        #Initialize Menu Bar
        menuBar = QMenuBar()
        self.setMenuBar(menuBar)
        tableMenu = menuBar.addMenu("Table")
        editMenu = menuBar.addMenu("Edit")
        graphMenu = menuBar.addMenu("Graph")
        #Actions for menu
        newAction = QAction("New",self)
        newAction.setShortcut("Ctrl+N")
        tableMenu.addAction(newAction)
        
        openAction = QAction("Open",self)
        openAction.setShortcut("Ctrl+O")
        tableMenu.addAction(openAction)
        
        saveAction = QAction("Save",self)
        saveAction.setShortcut("Ctrl+S")
        tableMenu.addAction(saveAction)
        
        findAction = QAction("Find",self)
        findAction.setShortcut("Ctrl+F")
        editMenu.addAction(findAction)
        
        createAction = QAction("Create",self)
        createAction.setShortcut("Ctrl+G")
        graphMenu.addAction(createAction)

        #Name opened table
        self.tableNameLabel = QLabel('')
        #Center label in grid cell
        self.tableNameLabel.setAlignment(Qt.AlignCenter)
        #Create table
        self.tableWidget = QTableWidget()
        
        #Create grid and set spacing for cells
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.tableNameLabel, 0, 0)
        grid.addWidget(self.tableWidget, 1, 0)
        mainWidget.setLayout(grid) 
        self.tableWidget.move(0,0)
        #Binding actions
        tableMenu.triggered[QAction].connect(self.openActionFunc)
        #Show window
        self.show()
    
    def openActionFunc (self):
        self.changerGUI = ChangerGUI(self.dbMan)
        self.changerGUI.show()
    
    #TODO Write func
    def printTable (self):
        #----DELETE THIS----
        test1 = self.dbMan.getAmendedTable()
        test2 = self.dbMan.getTable()
        for i in test1:
            print (i)
        for j in test2:
            print (j)
        #-------------------
        self.tableNameLabel.setText(self.dbMan.nameTable())
        table = self.dbMan.getAmendedTable()
        columnCount = len(table[0])
        rowCount = len(table)
        self.tableWidget.setColumnCount(columnCount)
        self.tableWidget.setRowCount(rowCount)
        for rowI in range(rowCount):
            for colI in range(columnCount):
                self.tableWidget.setItem(rowI, colI, QTableWidgetItem(str(table[rowI][colI])))
         
        
    def moveToCenter (self):
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
   
class ChangerGUI (QWidget):
    
    def __init__ (self, dbManObj):
        #Initialize father (QWidget) constructor (__init__)
        QWidget.__init__(self)
        #Function for creating UI
        self.dbMan = dbManObj
        self.initUI()
        
    def initUI (self):
        '''
        Function initialize user interface
        '''
        #Set window title, size and put in center
        self.setWindowTitle('Choose table')
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
        self.tablesList.setSelectionMode(QAbstractItemView.SingleSelection)
        #Adding items in databasesList and tablesList
        self.showDatabases()
        #Bind list
        self.databasesList.itemClicked.connect(self.showTables)
        #Create buttom
        makeGraphButton = QPushButton('Change')
        #Bind Button
        makeGraphButton.clicked.connect(self.changeTable)
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

    def changeTable(self):
        global pself
        self.dbMan.table(self.tablesList.currentItem().text())
        DBEditGUI.printTable(pself)
        self.hide()

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
        self.databasesList.addItems(self.dbMan.getListNamesDatabases())

    def showTables(self):
        '''
        This function shows all tables, after user click on name of database
        and put their in tablesList. Also this function change database
        (use [db];).
        '''
        self.tablesList.clear()
        self.dbMan.database(self.databasesList.currentItem().text())
        self.tablesList.addItems(self.dbMan.getListNamesTables())

class TRVisualGUI (QWidget):
    
    def __init__ (self):
        #Initialize father (QWidget) constructor (__init__)
        super().__init__()
        #Function for creating UI
        self.dbMan = DBM()
        self.initUI()
    
    def initUI (self):
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
        outputGraph = self.dbMan.relationshipsGraph(selectedTablesList)

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
        self.databasesList.addItems(self.dbMan.getListNamesDatabases())

    def showTables(self):
        '''
        This function shows all tables, after user click on name of database
        and put their in tablesList. Also this function change database
        (use [db];).
        '''
        self.tablesList.clear()
        self.dbMan.database(self.databasesList.currentItem().text())
        self.tablesList.addItems(self.dbMan.getListNamesTables())
      
def main():
    #dbMan = DBM()
    #dbMan.database('testRelationships')
    #dbMan.table('Addresses')
    mainDBM = DBM()
    app = QApplication(sys.argv)
    edit = DBEditGUI(mainDBM)
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()
        
        
