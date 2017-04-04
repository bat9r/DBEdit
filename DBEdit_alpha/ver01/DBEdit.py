#Import modules for UI
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QGridLayout, QApplication,
    QDesktopWidget, QListWidget, QPushButton, QFileDialog, QAbstractItemView)
#Module for regular expression
import re
#Our module
from DBMan import DBM

class TRVisualGUI(QWidget):
    
    def __init__(self):
        #Initialize father (QWidget) constructor (__init__)
        super().__init__()
        #Function for creating UI
        self.dbMan = DBM()
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
    dbMan = DBM()
    dbMan.database('testRelationships')
    dbMan.table('Addresses')
    matrix = (dbMan.getAmendedTable())
    #app = QApplication(sys.argv)
    #trv = TRVisualGUI()
    #sys.exit(app.exec_())
    
    
   

if __name__ == "__main__":
    main()
        
        
