#coding = utf-8
#encoding: utf-8
#This Python file uses the following encoding: utf-8
'''
Created on 2016/03/19

@author: Daytona
'''

import csv
import code
import copy
import pandas as pd

count = 0

class recordContainer():
    def __init__(self):
        self.__time = None # 交易日
        self.__code = None # 证券代码
        self.__name = None # 证券简称
        self.__deviate = 0.0 # 偏离值
        self.__amount = 0.0 # 成交量
        self.__volume = 0.0 # 股票成交金额
        self.__depVolume = 0.0 # 营业部交易额
        self.__depName = None # 营业部名称
        self.__buysell = None # 买入 or 卖出
        self.__marketDep = None # A or B 股
        self.__type = None

def readOut(fileName):
    csvfile = file(fileName, 'rb')
    fileContent = csv.reader(csvfile)
    result = []
    for line in fileContent :
        result.extend(parserUpDeviationSeven(line))
    return result

def findLineIndex(key_word, string_list):
    for i in range(len(string_list)) :
        line = string_list[i][1:-1]
        if key_word in line : 
            return i + 1

def dateConvert(dateString):
    # change 2006年12月28日 to 2006-12-28
    year = dateString[0:4]
    month= dateString[7:9]
    day = dateString[-5:-3]
    result = year + "-" + month + "-" + day
    return  result

def parserUpDeviationSeven(input):
    final_result_container = []
    #print input
    string_list = ''.join(input).split(",")
    # see if has record
    start_index = findLineIndex("1、", string_list)
    end_index = findLineIndex("2、", string_list)
    # extract the date has no record
    if end_index - start_index  < 3:
        return final_result_container
    # find date
    trade_date = ""
    for i in range(len(string_list)) :
        line = string_list[i][1:-1]
        #print line
        if "交易日期:" in line :
            start_index = line.index(":")+1
            line = line[start_index:]
            end_index = line.index("日") + 3
            trade_date = line[:end_index]
            print trade_date
            break
    # find number of security of A stock
    start_index = 0
    end_index = 0
    for i in range(len(string_list)) :
        line = string_list[i][1:-1]
        if "证券代码" in line : 
            start_index = i + 1
            break
    for i in range(start_index, start_index + 5) :
        line = string_list[i][1:-1]
        if "证券代码" in line : 
            end_index = i-1
            break
    #print security_num
    security_container = dict()
    for i in range(start_index, end_index) :
        line = string_list[i][1:-1].strip()
        print line
        # find code
        code = codeParser(line)
        # find code_name
        name_end_index = 0
        for i in range (16,len(line)) :
            if line[i].isdigit() :
                name_end_index = i
                break
        name_split = line[14:name_end_index].split("   ")
        if len(name_split[0]) <= 2 and len(name_split[1]) <= 2:
            name = name_split[2].replace(' ', '')
        elif len(name_split[0]) <= 2 :
            name = name_split[1].replace(' ', '')
        else :
            name = name_split[0].replace(' ', '')
        # find deviate
        deviate_start_index = 30
        deviate_end_index = line.index("%")+1
        deviate = line[deviate_start_index:deviate_end_index].strip()
        
        # find amount
        amount_start_index = deviate_end_index + 1
        amount_end_index = -15
        amount = line[amount_start_index:amount_end_index].strip()
        # find volume
        volume = line[amount_end_index : ].strip()
        oneRecord = recordContainer()
        oneRecovolume1ime = datevolume1t(trade_date)
        oneRecord.__code = code
        oneRecord.__name = name
        oneRecord.__deviate = deviate
        oneRecord.__amount = float(amount) # 成交量
        oneRecord.__volume = float(volume) * 10000.0 # 成交金额
        oneRecord.__type = "UpDeviationSevenPercent" # 有价格涨跌幅限制的日收盘价格涨幅偏离值达到7%的前三只证券
        volume1(code) > 2 :
            security_container[code] = oneRecord
        #print security_container
    
    # get department info
    for code in security_container.keys() :
        start_index = 0
        end_index = 0
        for i in range(len(string_list)) :
            line = string_list[i][1:-1].strip()
            if code in line and "%" not in line :
                start_index = i
            if start_index != 0 and "卖出" in line :
                end_index = i + 6
                break
        buy_start_index = 0
        buy_end_index = 0
        sell_start_index = 0
        for i in range(start_index, end_index) :
            line = string_list[i][1:-1].strip()
            if "买入" in line :
                buy_start_index = i + 2
            if "卖出" in line :
                buy_end_index = i-1
                sell_start_index = i + 1
        # find buy
        for i in range(buy_start_index,buy_end_index) :
            line = string_list[i][1:-1].strip().split(" ")
            #print line[0]
            if len(line) < 2:
                break
            else :
                record = copy.deepcopy(security_container[code])
                depName = line[1]
                depVolume = line[-1]
                record.__depName = depName
                record.__depVolume = float(depVolume)
                record.__buysell = "buy"
                record.__marketDep = "A"
                final_result_container.append(record)
        # find sell
        for i in range(sell_start_index, end_index) :
            line = string_list[i][1:-1].strip().split(" ")
            #print line[0]
            if len(line) < 2 :
                break
            else :
                record = copy.deepcopy(security_container[code])
                depName = line[1]
                depVolume = line[-1]
                record.__depName = depName
                record.__depVolume = float(depVolume)
                record.__buysell = "sell"
                record.__marketDep = "A"
                final_result_container.append(record)
    return final_result_container

def codeParser(input):
    start_index = 0
    end_index = 0
    for i in range(3,len(input)) :
        if start_index == 0 and input[i].isdigit() :
            start_index = i
        elif start_index != 0 and not input[i].isdigit() :
            end_index = i
            break
    code = input[start_index:end_index]
    return code

def getResultRecord():
    result = []
    for i in range(24):
        fileName = "./Data/allData-" + str(i) + ".txt"
        #print fileName
        result.extend(readOut(fileName))
    return result

def writeToCsv(result):
    column = ["Date","List_Type","Code","Code_Name","Deviate","Amount","Volume","Dep_Volume","Dep_Name","Buy_Sell","Market_Dep"]
    resultDataFrame = pd.DataFrame(columns=column)
    for i in range(len(result)) :
        if i % 1000 == 0:
            print str(i) + " of " + str(len(result)) 
        oneResult = result[i]
        column_data = []
        column_data.append(oneResult.__time)
        column_data.append(oneResult.__type)
        column_data.append(oneResult.__code)
        column_data.append(oneResult.__name)
        column_data.append(oneResult.__deviate)
        column_data.append(oneResult.__amount)
        column_data.append(oneResult.__volume)
        column_data.append(oneResult.__depVolume)
        column_data.append(oneResult.__depName)
        column_data.append(oneResult.__buysell)
        column_data.append(oneResult.__marketDep)
        resultDataFrame.loc[i] = column_data
    print("Writing to CSV!")
    resultDataFrame.to_csv("./Data/allData.csv", index=False)
    
if __name__ == "__main__":
    # parser result form raw downloaded data
    result = getResultRecord()
    # write to csv "allData.csv"
    writeToCsv(result)
    print("finished")
    
