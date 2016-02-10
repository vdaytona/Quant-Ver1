'''
Created on 2016/02/02

@author: Daytona
'''

import mysql.connector
import MyLibrary.connectMysqlDB as Mysql
from pandas import DataFrame as pd
from MyLibrary import johansen
from statsmodels.tsa.stattools import adfuller
from pyalgotrade.plotter import InstrumentMarker
from MyLibrary.mysqlQuery import historicalPriceQuery
import matplotlib.pyplot as plt
import datetime
import os
import csv

class input():
    
    def __init__(self):
        self.__writer = None

    def getInstrumentList(self,cnx):
        sql = "select Local_Code from newyorkexchange.listedcompanies_newyork"
        df = Mysql.query(cnx).pandasQuery(sql)
        return df
    
    def getAllHistoricalQuotes(self,cnx, instruments):
        tableNames = dict()
        for instrument  in instruments :
            tableName = str("newyorkexchange.`%s_historicalquotes_newyork`" %instrument)
            tableNames[instrument] = tableName
         
        query = historicalPriceQuery(instruments, tableNames)
        quotes = query.pandasQueryMulitple(cnx)
        return quotes
    
    def alignTime(self,instruments):
        i = 0
        mergedSeries = None
        for instrument in instruments :
            if i == 0:
                # first instrument do not merge
                i += 1
                # change col name in order not to overlap
                mergedSeries = instruments[instrument][["Date","AdjClose"]]
                newColName = str("%s_Adjclose" %instrument)
                mergedSeries = mergedSeries.rename(columns={'AdjClose': newColName})
            else :
                newSeries = instruments[instrument][["Date","AdjClose"]]
                newColName = str("%s_Adjclose" %instrument)
                newSeries = newSeries.rename(columns={'AdjClose': newColName})
                
                mergedSeries = pd.merge(mergedSeries,newSeries, on="Date", how = "inner")
        mergedSeries.dropna()
        # put result into Dict, and recover Name
        alignedSeries = dict()
        for instrument in instruments :
            colName = str("%s_Adjclose" %instrument)
            alignedSeries[instrument] = mergedSeries[["Date",colName]].rename(columns={colName : 'AdjClose'})
        mergedSeries = mergedSeries.set_index(mergedSeries["Date"].values)
        #mergedSeries.plot()
        #plt.show()
        return alignedSeries
    
    def JohansenTest(self, instruments, quotes):
        data = pd()
        for instrument in instruments :
            data[instrument] = quotes[instrument]["AdjClose"]
        jres = johansen.coint_johansen(data, 0, 1)
        #johansen.print_johan_stats(jres)
        return jres
    
    def Output(self,instrumens, jres, fileName):
        row, fieldsName = self.parseRowField(instrumens, jres)
        #print row
        if self.checkIfHasTodayFile(fileName) is True :
            self.addNewRow(row, fieldsName, fileName)
        else :
            self.createNewCsv(row, fieldsName, fileName)
    
    def parseRow(self,instruments, jres):
        return self.parseRowField(instruments, jres)[0]
    
    def parseRowField(self,instruments, jres):
        number = len(instruments)
        fieldNames = []
        row = dict()
        for i in range(number) :
            colName = "Instrument_%s" %str(i)
            fieldNames.append(colName)
            row[colName] = instruments[i]
        for i in range(number) :
            colName = "Trace_Statistic_%s" %str(i)
            fieldNames.append(colName)
            row[colName] = str(jres.lr1[i])
            colName = "Crit_%s" %str(i)
            fieldNames.append(colName)
            row[colName] = str(jres.cvt[i])
        return row, fieldNames
        
    
    def checkIfHasTodayFile(self,fileName):
        for s in os.listdir("./Result") :
            if fileName.split("/")[-1] in s :            
                return True
        return False
    
    def addNewRow(self, row, fieldName, fileName):
        with open(fileName, 'a') as csvfile :
            self.__writer = csv.DictWriter(csvfile,fieldnames=fieldName)
            self.__writer.writerow(row)
    
    def createNewCsv(self,row, fieldName, fileName):
        # create New Csv to save data
        with open(fileName, 'w') as csvfile :
            #print fieldName
            self.__writer = csv.DictWriter(csvfile, fieldnames=fieldName)
            self.__writer.writeheader()
            self.__writer.writerow(row)
    
    def run(self):
        # 1. output csv file name
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        fileName = ("./Result/Pair-Cointegration-Record-%s.csv" % currentTime)
        
        # 1. connect database
        cnx = Mysql.cnxStock()
        try:
            connection = cnx.connect()
            # 2. import instruments name from database
            #instrumentList = self.getInstrumentList(connection)["Local_Code"].values
            instrumentList = ("A","ibm","aapl")
            
            print ("Instruments Name import finished")
            
            loopNumber = len(instrumentList) * (len(instrumentList)-1)
            count = 0
            for i in range(len(instrumentList)) :
                for k in range(i+1 , len(instrumentList)) :
                    instrumentA = instrumentList[i]
                    instrumentB = instrumentList[k]
                    print "start %s and %s pair, this %s to process (%s in all)" %(instrumentA, instrumentB, str(count) , str(loopNumber))
                    if instrumentA is not instrumentB :
                        instruments = [instrumentA, instrumentB]
                        # 3. import data from database, as Dict{instrument_Name : dataseries}
                        try :
                            quotes = self.getAllHistoricalQuotes(connection, instruments)
                            # 4 Align time
                            alignedSeries = self.alignTime(quotes)
                            # 5 JohansenTest
                            jres = self.JohansenTest(instruments,alignedSeries)
                            #if jres.lr1[0] > 19.9349 and jres.lr1[1] > 6.6349
                            johansen.print_johan_stats(jres)
                            if jres.lr1[0] > 19.1 and jres.lr1[1] > 4.1 :
                                # 6 output result
                                self.Output(instruments, jres, fileName)
                        except :
                            print "%s and %s has problem" %(instrumentA, instrumentB)
                        
                    count += 1
                        
            
        finally:
            cnx.close_connection()
        print "Finish"
            

if __name__ == '__main__':
    input().run()