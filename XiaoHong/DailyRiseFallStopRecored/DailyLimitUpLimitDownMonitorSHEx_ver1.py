'''
Created on 7 Dec 2015
This file is used to monitor the real time number of limitUp/limitDown stop stocks by crawling data from http://stock.jrj.com.cn/tzzs/zdtwdj.shtml.
And show the result in plot
version - 1.0
@author: daytona
'''

from urllib import urlopen
from matplotlib.dates import DateFormatter
import datetime
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import json
import time
import os
import csv

# set the figure
record_url = "http://home.flashdata2.jrj.com.cn/limitStatistic/min.js"
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

ax1.set_xlabel("Time")
ax1.set_ylabel("Number of LimitUp", color='r')
ax2.set_ylabel("Number of LimitDown", color='b')
ax1.xaxis.set_major_formatter(DateFormatter('%H:%M'))
ax1.grid(True)

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
    
def plotRecrod(num):
    #get Data
    date, data = getTodayRecord()
    
    # fill xaxis, yaxis
    x = []
    y1 = []
    y2 = []
    for i in range(0 , len(data["time"])) :
            timestr = str(data["time"][i])
            time = timestr[:-2] + ":" + timestr[-2:] + " " + date.strftime("%Y-%m-%d")
            x.append(datetime.datetime.strptime(time, "%H:%M %Y-%m-%d"))
            y1.append(data["limitUp"][i])
            y2.append(data["limitDown"][i])
    
    ax1.plot_date(x, y1, fmt="r-")
    ax2.plot_date(x, y2, fmt="b-")
    
    ax1.set_xlim(x[0] - datetime.timedelta(minutes=5), x[-1] + datetime.timedelta(minutes=5))
    ax1.set_ylim(0, max(max(y1), max(y2)) * 1.1)
    ax2.set_ylim(0, max(max(y1), max(y2)) * 1.1)
   
    fig.autofmt_xdate()
    
    # write title
    timestr = str(data["time"][-1])
    time = date.strftime("%Y-%m-%d") + " " + timestr[:-2] + ":" + timestr[-2:]
    title = "Current Time : " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\nData time: " + time + "\nNumber of LimitUp : " + str(data["limitUp"][-1]) + "\nNumber of LimitDwon : " + str(data["limitDown"][-1])
    plt.title(title)
    
    outpuCsv(date, data)
    
    return ax1, ax2

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

if __name__ == '__main__': 
    
    # animation so as to update figure in one minuter interval
    a = animation.FuncAnimation(fig, plotRecrod,  interval=60000 )
    
    plt.tight_layout()
    plt.show()
    print "finished"
