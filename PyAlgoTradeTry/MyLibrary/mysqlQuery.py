'''
Created on 13 Jan 2016

@author: purewin7
'''

import pandas.io.sql as psql

# connect to Mysql Database to query data , return pandas dataframe type
class historicalPriceQuery:
    def __init__(self, instruments, tableNames):
        self.__instruments = instruments
        self.__tableNames = tableNames
    
    def pandasQuerySingle(self,  connection):
        sql = str("select * from %s" % self.__tableNames)
        return psql.read_sql(sql, connection)
        
    def pandasQueryMulitple(self, connection):
        barsDict = dict()
        for instrument in self.__tableNames :
            tableName = self.__tableNames[instrument]
            sql = str("select * from %s" % tableName)
            df = psql.read_sql(sql, connection)
            barsDict[instrument] = df
        return barsDict
            