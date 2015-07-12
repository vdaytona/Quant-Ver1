'''
!/usr/bin/python27
This module is used for connecting MysqlDB
Created on 2015/07/12

@author: Daytona

'''

__version__ = '1.0.1'

import mysql.connector
import pandas.io.sql as psql

# to get cnx by using host, userName, password, database (optional)
# if host is wrong, ask Daytona to get latest host IP
class cnxStock:
    def __init__(self, host = None, userName = None, password = None, database = None):
        self.host = host
        self.userName = userName
        self.password = password
        self.database = database
    
    def connect(self):
        try:
            if self.host is None:
                raise connectionInfoMissingException('host')
            elif self.userName is None:
                raise connectionInfoMissingException('userName')
            elif self.password is None:
                raise connectionInfoMissingException('password')
            cnx = mysql.connector.connect(user = self.userName,password = self.password,host = self.host, database = self.database)
            print('Successfully connected to %s @ %s' %(self.userName,self.host))
            return cnx
        except connectionInfoMissingException, e:
            print('%s is missing' %e.missingInfo)
    
    def set_database(self,database):
        self.host = database
    
    def get_database(self):
        return self.database
            
# query MysqlDB using sql grammar
class query:
    def __init__(self,cnx):
        self.cnx = cnx
        
    #return the query result in term of pandas
    def pandasQuery(self,sql):
        return psql.read_sql(sql, self.cnx)
        

# Exception for login MysqlDB server
class connectionInfoMissingException(Exception):
    def __init__(self,missingInfo):
        Exception.__init__(self)
        self.missingInfo = missingInfo