#Import modules for UI
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QApplication,
    QDesktopWidget, QListWidget, QPushButton, QFileDialog, QAbstractItemView,
    QAction, QMenuBar, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QAbstractScrollArea)

#Our module
from DBMan import DBM, TableProcessor

class DBEditGUI (QMainWindow):
    
    def __init__ (self, dbmObj):
        #Initialize father (QWidget) constructor (__init__)
        super().__init__()
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
        
        createGraphAction = QAction("Create",self)
        createGraphAction.setShortcut("Ctrl+G")
        graphMenu.addAction(createGraphAction)

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
        #tableMenu.triggered[QAction].connect(self.openActionFunc)
        openAction.triggered.connect(self.openActionFunc)
        createGraphAction.triggered.connect(self.createGraphActionFunc)
        saveAction.triggered.connect(self.saveActionFunc)
        #Connect the ScrollBar for signal when table ends
        self.tableWidget.verticalScrollBar().valueChanged.connect(self.scrolledEvent)
        self.tableWidget.horizontalScrollBar().valueChanged.connect(self.scrolledEvent)
        
        #Show window
        self.show()
        
    def createRows (self):
        '''
        Function add Row in tableWidget
        '''
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        
    def createColumns (self):
        '''
        Function add Column in tableWidget
        '''
        self.tableWidget.insertColumn(self.tableWidget.columnCount())
        
    def scrolledEvent(self, value):
        '''
        Function reacts for end of scrolling and calls to functions for
        adding rows or columns
        '''
        if value == self.tableWidget.verticalScrollBar().maximum():
             self.createRows()
        elif value == self.tableWidget.horizontalScrollBar().maximum():
             self.createColumns()
    
    def openActionFunc (self):
        '''
        Function creates window for choosing table for editing
        '''
        self.changerGUI = ChangerGUI(self.dbMan, self)
        self.changerGUI.show()
        
    def createGraphActionFunc (self):
        '''
        Function create window for making graphs
        '''
        self.graphGUI = TRVisualGUI()
        self.graphGUI.show()
    
    def getMatrixFromTable (self):
        '''
        Function get values from tableWidget in matrix view end 
        returns it. Empty values change in 0
        '''
        #Get matrix without none elements
        w = self.tableWidget.columnCount()
        h = self.tableWidget.rowCount()
        matrixWithoutNone = list(
                            filter(bool, 
                            [[self.tableWidget.item(j,i).text() 
                                for i in range(w) 
                                    if self.tableWidget.item(j,i) is not None ] 
                            for j in range(h)]
                            ))
        #Get real width and height matrix
        width = 0
        height = len(matrixWithoutNone)
        for r in matrixWithoutNone:
            if len(r) > width:
                width = len(r)
        #Create matrix none -> 0 , like a square
        matrixWithEmptyItems = ([[0 for i in range(width)] 
                                    for j in range(height)])
        for i in range(len(matrixWithoutNone)):
            for j in range(len(matrixWithoutNone[i])):
                matrixWithEmptyItems[i][j] = matrixWithoutNone[i][j]
                
        return matrixWithEmptyItems
    
    def saveActionFunc (self):
        tabProc = TableProcessor (self.dbMan, self.getMatrixFromTable())
        self.printTable()
        
        
    def printTable (self):
        '''
        Function print table from DBM in DBEditGUI tableWidget
        '''
        self.tableNameLabel.setText(self.dbMan.nameDatabase() +', '+ self.dbMan.nameTable())
        table = self.dbMan.getAmendedTable()
        columnCount = len(table[0])
        rowCount = len(table)
        self.tableWidget.setColumnCount(columnCount)
        self.tableWidget.setRowCount(rowCount)
        for rowI in range(rowCount):
            for colI in range(columnCount):
                self.tableWidget.setItem(rowI, colI, QTableWidgetItem(str(table[rowI][colI])))
        #Changes cells size for fitting to content
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        #Do table bigger (for scrolling)
        for i in range(10):
            if i < self.tableWidget.columnCount():
                self.tableWidget.insertColumn(self.tableWidget.columnCount())
        for j in range(20):
            if j < self.tableWidget.rowCount():
                self.tableWidget.insertRow(self.tableWidget.rowCount())
         
    
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
    
    def __init__ (self, dbManObj, DBEditGUISelf):
        #Initialize father (QWidget) constructor (__init__)
        QWidget.__init__(self)
        #Create obj foe correct working
        self.dbMan = dbManObj
        self.DBEditGUISelf = DBEditGUISelf
        #Function for creating UI 
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
        self.dbMan.table(self.tablesList.currentItem().text())
        DBEditGUI.printTable(self.DBEditGUISelf)
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
        #self.show()

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
    #Database manager
    mainDBM = DBM()
    app = QApplication(sys.argv)
    edit = DBEditGUI(mainDBM)
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
        
