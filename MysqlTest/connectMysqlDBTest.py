'''
!/usr/bin/python27
Demonstration of using connectMysqlDB
Created on 2015/06/03

@author: Daytona
'''
import connectMysqlDB
import mysql.connector

def main():
    
    # set connection info
    host='149.171.37.73'
    userName='PengJiang'
    password='jiangpengjun'
    database='sydneyexchange'
    cnx = mysql.connector.connect();
    try:
        #get cnx used for connecting DB
        cnx = connectMysqlDB.cnxStock(host=host,userName=userName,password=password,database=database).connect()
        
        #write anything you want to do in the workingSpace
        workingSpace(cnx)
        
    finally:
        cnx.close()
    
    print ("finish")
    
#write your work here
def workingSpace(cnx):
    sql = ("select * from newyorkexchange.ibm_historicalquotes_newyork")
    df = connectMysqlDB.query(cnx).pandasQuery(sql)
    #print(df.head(100))
    #df['AdjClose'].hist()
    #p.show()
    return df
    
if __name__ == "__main__": main()
