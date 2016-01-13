'''
Created on 13 Jan 2016

@author: purewin7
'''

import pandas.io.sql as psql

class historicalPriceQuery:
    def __init__(self, instruments, tableNames):
        self.__instruments = instruments
        print instruments
        self.__tableNames = tableNames
        print tableNames
    
    def pandasQuerySingle(self, connection):
        sql = str("select * from %s" % self.__tableNames)
        return psql.read_sql(sql, connection)
        