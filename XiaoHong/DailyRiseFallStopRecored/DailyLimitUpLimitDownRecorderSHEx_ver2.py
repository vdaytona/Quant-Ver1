'''
Created on 7 Dec 2015
This file is used to record the real time number of rise fall stop stocks by crawling data from http://stock.jrj.com.cn/tzzs/zdtwdj.shtml.
Result is written in a csv file
version - 1.1 plus dialog function
@author: daytona
'''

from urllib import urlopen

import datetime
import matplotlib.pyplot as plt
import Tkinter
import tkMessageBox
import csv
import json
import time
import os
from matplotlib.dates import DateFormatter

record_url = "http://home.flashdata2.jrj.com.cn/limitStatistic/min.js"

def getCurrentTime():
    pass

def ifTradingTime():
    pass

def getTodayRecord():
    # get data from web into JSON type
    print "Start connecting to database..."
    jsonurl = urlopen(record_url)
    content = jsonurl.read()
    startNumber = content.__str__().find("=")
    text = json.loads(content[startNumber + 1:-3])
    date = extractDateDay(text["time"])
    data = splitData(text["Data"])
    print "Latest data has been caught!"
    return date, data

def splitData(listInput):
    # split data into Dict type : time , limitUp, limitDown
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
    # extract Date and Day from origin turn into datetime type
    date = datetime.datetime.strptime(inputlist[0:-3], "%Y-%m-%d %H:%M")
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
    fileName = ("%s-limitup-limitdown-record.csv" % (date.strftime("%Y-%m-%d")))
    
    print "Data of %s has been updated in ./%s ." % (day, fileName)
    

def createNewCsv(date, data):
    # create New Csv to save data
    day = date.strftime("%Y-%m-%d")
    fileName = ("%s-limitup-limitdown-record.csv" % (date.strftime("%Y-%m-%d")))
    with open(fileName, 'w') as csvfile:
        fieldnames = ['Date', 'Time', 'limitUp', 'limitDown']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(0 , len(data["time"])) :
            timestr = str(data["time"][i])
            time = timestr[:-2] + ":" + timestr[-2:]
            writer.writerow({'Date' : day, 'Time' : time, 'limitUp' : data["limitUp"][i], 'limitDown' : data["limitDown"][i]})
    print "Data of %s has been saved in ./%s ." % (day, fileName)
    
def plotRecrod(date , data):
    x = []
    y1 = []
    y2 = []
    for i in range(0 , len(data["time"])) :
            timestr = str(data["time"][i])
            time = timestr[:-2] + ":" + timestr[-2:] + " " + date.strftime("%Y-%m-%d")
            x.append(datetime.datetime.strptime(time, "%H:%M %Y-%m-%d"))
            y1.append(data["limitUp"][i])
            y2.append(data["limitDown"][i])
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    
    ax1.plot_date(x, y1, fmt="r-")
    ax2.plot_date(x, y2, fmt="b-")
    
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Number of LimitUp", color='r')
    ax2.set_ylabel("Number of LimitDown", color='b')
    ax1.set_xlim(x[0] - datetime.timedelta(minutes=5), x[-1] + datetime.timedelta(minutes=5))
    ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    
    ax1.set_ylim(0, max(max(y1), max(y2)) * 1.1)
    ax2.set_ylim(0, max(max(y1), max(y2)) * 1.1)
   
    ax1.grid(True)
    fig.autofmt_xdate()
    
    timestr = str(data["time"][-1])
    time = date.strftime("%Y-%m-%d") + " " + timestr[:-2] + ":" + timestr[-2:]
    title = time + "\nNumber of LimitUp : " + str(data["limitUp"][-1]) + "\nNumber of LimitDwon : " + str(data["limitDown"][-1])
    plt.title(title)
    
    plt.show()
    pass

def updataTodayRecordToCsv():
    pass

def printStartDownload():
    pass

def printUpdataTodayRecordNow():
    pass

def run():
    date , data = getTodayRecord()
    outpuCsv(date, data)
    plotRecrod(date, data)
    tkMessageBox.showinfo("Info", "Data download finished")

if __name__ == '__main__':
    #===========================================================================
    # # start logging
    # logging.basicConfig(filename='example.log',level=logging.DEBUG)
    # logging.info("start")
    #===========================================================================
    
    # read in data and split into datetime (corresponding data) and data
    
    
    # output into csv name as "yyyy-mm-dd-limitup-limitdown-record.csv"
    
    top = Tkinter.Tk()
    B = Tkinter.Button(top, text="Download data!", command=run)
    B.pack()
    top.mainloop()
    
    # run()
    
    print "finished"
