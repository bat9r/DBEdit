#Module for using MySQL
import pymysql
#Module for regular expression
import re

class Database:
    #Connecting to MySQL host
    __conn = pymysql.connect(host='localhost', user='root', passwd='', db='mysql')

    def __init__ (self, nameDatabase):
        #Opening cursor for working with database
        cursor = self.__conn.cursor()
        #Choose database
        cursor.execute('use ' + nameDatabase + ';')
        #Closing cursor
        cursor.close()

    def getTable (self, nameTable):
        '''
        Function: get from MySQL and convert database table
        Takes: argument name of needed table,
        Returns: table in matrix view
        '''
        #Opening cursor for working with database
        cursor = self.__conn.cursor()
        #MySQL command Get table
        cursor.execute('select * from ' + nameTable + ';')
        #Get table like matrix
        matrix = [list(row) for row in cursor]
        #Closing cursor
        cursor.close()
        #Returning table-matrix
        return matrix

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
            print (type(value))
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


    def save(self):
        self._conn.commit()

if __name__ == "__main__":
    db = Database('testRelationships')
    for i in range(10):
        print (db.identifyType(input(">> ")))
    
