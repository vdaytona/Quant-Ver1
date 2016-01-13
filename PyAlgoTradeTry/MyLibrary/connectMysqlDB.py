'''
!/usr/bin/python27
This module is used for connecting MysqlDB
Created on 2016/01/13
for PyAlgoTrade
@author: Daytona

'''

__version__ = '1.0.2'

import mysql.connector
import pandas.io.sql as psql

# to get cnx by using host, userName, password, database (optional)
# if host is wrong, ask Daytona to get latest host IP

class cnxStock:
    def __init__(self, host = "149.171.37.73", userName = "PengJiang", password = "jiangpengjun", database = "sydneyexchange"):
        self.__host = host
        self.__userName = userName
        self.__password = password
        self.__database = database
        self.__cnx = mysql.connector.connect()
    
    def connect(self):
        try:
            if self.__host is None:
                raise connectionInfoMissingException('host')
            elif self.__userName is None:
                raise connectionInfoMissingException('userName')
            elif self.__password is None:
                raise connectionInfoMissingException('password')
            self.__cnx = mysql.connector.connect(user = self.__userName,password = self.__password,host = self.__host, database = self.__database)
            print('Successfully connected to %s @ %s' %(self.__userName,self.__host))
            return self.__cnx
        except connectionInfoMissingException, e:
            print('%s is missing' %e.missingInfo)
    
    def set_database(self,database):
        self.__database = database
    
    def get_database(self):
        return self.__database
    
    def close_connection(self):
        self.__cnx.close()
        print ('connection to %s @ %s has been closed' %(self.__userName,self.__host))
            
# query MysqlDB using sql grammar
class query:
    def __init__(self,cnx):
        self.__cnx = cnx
        
    #return the query result in term of pandas
    def pandasQuery(self,sql):
        return psql.read_sql(sql, self.__cnx)
        

# Exception for login MysqlDB server
class connectionInfoMissingException(Exception):
    def __init__(self,missingInfo):
        Exception.__init__(self)
        self.missingInfo = missingInfo