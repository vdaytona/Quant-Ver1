#coding = utf-8
#encoding: utf-8
#This Python file uses the following encoding: utf-8
'''

Created on 2016/03/16
Unsed to download longhubang data from sse
@author: Daytona
'''

import urllib2 
import csv
import codecs
import json
import ast
import datetime

def download(date, resultList):
    url = "http://query.sse.com.cn/infodisplay/showTradePu\
blicFile.do?jsonCallBack=jsonpCallback4090&isPagination=false&dateTx=" + date + "&_=1458018159344"
    #print url
    
    headers={'host':'query.sse.com.cn','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36','Referer':'http\
://www.sse.com.cn/disclosure/diclosure/public/','Accept-Encoding':'gzip, \
deflate, sdch'}
    
    #print headers
    
    req = urllib2.Request(url = url,headers = headers)
    result = urllib2.urlopen(req).read()
    start_indexOfTradeDate = result.index("isTradeDate") + 13
    end_indexOfTradeDate = result[start_indexOfTradeDate :].index(",")
    isTradeDate = result[start_indexOfTradeDate : start_indexOfTradeDate + end_indexOfTradeDate]
    if "false" in isTradeDate :
        print False
    else :
        print date
        #print result
        result = result.split("fileContents")[1][4:].split("]")[0]
        resultList.append(result)
    #print isTradeDate
    #result = result[result.index("(", )+1 : result.index(")", )]
    #print result
    #result = json.loads(result)
    #print result["isTradeDate"]
    #print type(result)
    #result = feeddata.split("fileContents")[1][4:].split("]")[0]
    #return result

start_date = datetime.date(2006,8,07)
end_date = datetime.date(2016,3,18)
dateList = []
for i in range((end_date-start_date).days + 1) :
    day = start_date + datetime.timedelta(days=i)
    dateList.append(day.strftime("%Y-%m-%d"))
#print dateList
resultList = []
for i in range(len(dateList)) :
    download(dateList[i],resultList)
    
print resultList

csvfile = file('./Data/allData.txt', 'wb')
writer = csv.writer(csvfile)
for line in resultList :
    writer.writerow(line)
csvfile.close()


# readout
#===============================================================================
# csvfile = file('./Data/allData.txt', 'rb')
# readout = csv.reader(csvfile)
# for line in readout :
#     readout = ''.join(line)
#     readlinst = readout.split(",")
#     flag = False
#     start_line = 0
#     end_line = 0
#     for i in range(len(readlinst)) :
#         line = readlinst[i][1:-1]
#         #print line
#         if "有价格涨跌幅限制的日收盘价格涨幅偏离值达到7%的前三只证券" in line :
#             start_line = i
#         if "B股" in line :
#             end_line = i
#             break
#     for i in range(start_line,end_line) :
#         print readlinst[i][1:-1]
#===============================================================================
    