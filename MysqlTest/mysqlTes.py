'''
for testing and showing the connecti
Created on 2015/06/03

@author: Daytona
'''


# import mysql.connector
import connectMysqlDB
# from mysql.connector import cursor
# import pandas as pd
# import pandas.io.sql as psql
import pylab as p

host='149.171.37.73'
userName='PengJiang'
password='jiangpengjun'
database='sydneyexchange'

cnx = connectMysqlDB.cnxStock(host=host,userName=userName,password=password,database=database).connect()
sql = ("SELECT * from aac_historicalquotes_sydney")
df = connectMysqlDB.query(cnx).pandasQuery(sql)
print(df.head(100))
df['Open'].hist()
p.show()

train_data = df.head(100)
test_data = df.head();

cnx.close()

#cnx = mysql.connector.connect(user='PengJiang', password='jiangpengjun', host='149.171.37.73', database='sydneyexchange')


# cursor = cnx.cursor()
# query = ("SELECT * from aac_historicalquotes_sydney")
# df = psql.read_sql(query, cnx)
# cursor.execute(query)
# 
# 
# for (Country, Local_Code, Name_English, Date, Open, High) in cursor:
#     print("{}, {}, {}, {}, {}, {}".format(Country, Local_Code, Name_English, Date, Open, High))
# 
# cursor.close()

print ("finish")
