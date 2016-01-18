'''
Created on 7 Dec 2015
This file is used to record the real time number of rise fall stop stocks by crawling data from http://stock.jrj.com.cn/tzzs/zdtwdj.shtml.
Result is written in a csv file
version - 1.0 can catch data from web, and saved into csv, but cannot update existed file
@author: daytona
'''

from urllib import urlopen
from datetime import date
from datetime import datetime

import csv
import json
import time
import os

record_url = "http://home.flashdata2.jrj.com.cn/limitStatistic/min.js"

def getCurrentTime():
    pass

def ifTradingTime():
    pass

def getTodayRecord():
    # get data from web into JSON type
    print "Start connecting to database..."
    jsonurl = urlopen(record_url)
    content  = jsonurl.read()
    startNumber = content.__str__().find("=")
    text = json.loads(content[startNumber+1:-3])
    date = extractDateDay(text["time"])
    data = splitData(text["Data"])
    print "Latest data has been caught!"
    return date, data

def splitData(listInput):
    #split data into Dict type : time , limitUp, limitDown
    timeList = []
    limitUpList = []
    limitDown = []
    for i in range(0 , len(listInput)):
        timeList.append(listInput[i][0])
        limitUpList.append(listInput[i][1])
        limitDown.append(listInput[i][2])
    data = {"time" : timeList, "limitUp" : limitUpList , "limitDown" : limitDown}
    return data

def extractDateDay(inputlist):
    #extract Date and Day from origin turn into datetime type
    date = datetime.strptime(inputlist[0:-3], "%Y-%m-%d %H:%M")
    return date

def outpuCsv(date, data):
    # check if has already have file
    if checkIfHasTodayFile(date) is True :
        # add new data
        createNewCsv(date, data)
    else:
        # create new csv file for today
        createNewCsv(date, data)

def checkIfHasTodayFile(date):
    today = date.strftime("%Y-%m-%d")
    for s in os.listdir("./") :
        if today in s :
            return True
    return False

def addNewDataIntoCsv(date, data):
    day = date.strftime("%Y-%m-%d")
    fileName = ("%s-limitup-limitdown-record.csv" %(date.strftime("%Y-%m-%d")))
    
    print "Data of %s has been updated in ./%s ." % (day, fileName)
    
    # TODO

def createNewCsv(date, data):
    # create New Csv to save data
    day = date.strftime("%Y-%m-%d")
    fileName = ("%s-limitup-limitdown-record.csv" %(date.strftime("%Y-%m-%d")))
    with open(fileName, 'w') as csvfile:
        fieldnames = ['Date', 'Time', 'limitUp', 'limitDown']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i in range(0 , len(data["time"])) :
            timestr = str(data["time"][i])
            time = timestr[:-2] + ":" + timestr[-2:]
            writer.writerow({'Date' : day, 'Time' : time, 'limitUp' : data["limitUp"][i], 'limitDown' : data["limitDown"][i]})
    print "Data of %s has been saved in ./%s ." % (day, fileName)
    
def plotTodayRecrod():
    pass

def updataTodayRecordToCsv():
    pass

def printStartDownload():
    pass

def printUpdataTodayRecordNow():
    pass

if __name__ == '__main__':
    #===========================================================================
    # # start logging
    # logging.basicConfig(filename='example.log',level=logging.DEBUG)
    # logging.info("start")
    #===========================================================================
    
    # read in data and split into datetime (corresponding data) and data
    date , data = getTodayRecord()
    
    # output into csv name as "yyyy-mm-dd-limitup-limitdown-record.csv"
    outpuCsv(date, data)
    print "finished"