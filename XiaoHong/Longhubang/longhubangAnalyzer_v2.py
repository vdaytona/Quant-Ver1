#coding = utf-8
#encoding: utf-8
#This Python file uses the following encoding: utf-8
'''
Created on 2016/03/23
v2
Different method to find group investors :
Since each stock may be bought for several continous days , 
so group investors need to be clustered by each complete investment event involving several days
1. cluster each investment event including information : code, start_date, end_date
(investment event is defined that one stock is contineously listed for more than one day)
2. Compare these list to find  the department which move similar
@author: Daytona
'''

import pandas as pd
import numpy as np
import datetime
import scipy.stats as stats
from numpy import corrcoef

def parser(data):
    # find code list
    code_list = pd.Series(data["Code"].values).unique()
    
    # find investment event list : "code,date1,date2,date3"
    investment_event_list = []
    for code in code_list :
        event_name = str(code)
        code_data = data[data["Code"] == code]
        date_list = pd.Series(np.sort(code_data["Date"].values)).unique()
        previous_date = None
        for i in range(len(date_list)) :
            date_datetime = datetime.datetime.strptime(date_list[i], "%Y-%m-%d")
            print date_datetime
            if previous_date == None :
                event_name += ("," + date_list[i])
                previous_date = date_datetime
                # if date is the last element in list, add to investment list
                if i == len(date_list) -1 :
                    investment_event_list.append(event_name)
            elif (date_datetime - previous_date).days <= 5 :
                event_name += ("," + date_list[i])
                previous_date = date_datetime
                if i == len(date_list) -1 :
                    investment_event_list.append(event_name)
                
            else :
                investment_event_list.append(event_name)
                previous_date = date_datetime
                event_name = str(code) +"," + date_list[i]
    event_dictionary = dict()
    for event in investment_event_list :
        print investment_event_list.index(event)
        department_list = []
        information = event.split(",")
        code = information[0]
        for i in range(1,len(information)) :
            filter1 = data[data["Code"] == float(code)]
            filter2 = filter1[filter1["Date"] == information[i]]
            department_list.extend(filter2["Dep_Name"].values)
        event_dictionary[event] = department_list
    for key in event_dictionary.keys() :
        print key
        for dep in event_dictionary[key] :
            print dep
    # TODO
    # write to csv
            
        
    
    
    #===========================================================================
    # # make dictionary
    # filter1_dictionary = dict()
    # for dep_name in dep :
    #     vector = []
    #     filter1_dictionary[dep_name] = vector
    # # find unique date
    # date = pd.Series(data["Date"].values).unique()
    # 
    # for i in range(len(date)) :
    #     oneData = data[data["Date"] == date[i]]
    #     trade_code = pd.Series(oneData["Code"].values).unique()
    #     for code in trade_code:
    #         # add 0 to each vector
    #         for keys in filter1_dictionary.keys() :
    #             filter1_dictionary[keys].append(0)
    #         # find listed code for iteration
    #         data_one_code = oneData[oneData["Code"] == code]
    #         for j in data_one_code.index:
    #             record = data_one_code.loc[j]
    #             # if it appears on list , change the last value to 1 or -1 for buy or sell condition
    #             #print record["Buy_Sell"]
    #             state = 1 if record["Buy_Sell"] == "buy" else -1
    #             filter1_dictionary[record["Dep_Name"]][-1] = state
    # #for key in filter1_dictionary:
    #     #print filter1_dictionary[key]
    # return filter1_dictionary
    #===========================================================================

def calculateCorrealtion(vectors):
    result = []
    keys = vectors.keys()
    column_data_List = []
    print len(keys)
    for i in range(0,len(keys)-1):
        print i 
        for j in range(i+1, len(keys)) :
            column_data = []
            if findNonZeroNumber(vectors[keys[i]]) >= 3 and findNonZeroNumber(vectors[keys[j]]) >= 3 :
                # delete the element that both are zero
                input1, input2 = deleteZero(vectors[keys[i]], vectors[keys[j]])
                cor= calculateSimilarity(input1, input2)
                if cor >= 0.2 :
                    dep_name = keys[i] + "," + keys[j]
                    column_data.append(dep_name)
                    column_data.append(cor)
                    column_data_List.append(column_data)
                    result.append(cor)
    print max(result)
    return column_data_List

def findNonZeroNumber(input):
    result = 0
    for num in input:
        result += abs(num)
    return result

def deleteZero(input1, input2):
    # delete the element both are zero, or it will increase the correlation
    new_input1 = []
    new_input2 = []
    for i in range(len(input1)) :
        if input1[i] != 0 or input2[i] != 0 :
            new_input1.append(input1[i])
            new_input2.append(input2[i])
    return new_input1, new_input2 

def writeToCsv(input):
    print("ready to write")
    column = {"Dep_Name", "Pearson_Corr"}
    resultDataFrame = pd.DataFrame(columns=column)
    print len(input)
    for i in range(len(input)) :
        resultDataFrame.loc[i] = input[i]
    print("is writing")
    resultDataFrame.to_csv("./Data/PersonCorr_Result.csv", index=False)

def calculateSimilarity(input1, input2):
    count = 0.0
    for i in range(len(input1)) :
        if input1[i] == input2[i] :
            count += 1
    return count / float(len(input1))

if __name__ == '__main__':
    #!!!!! sepearte buy or sell
    # read the file from allData.csv
    data =  pd.read_csv("./Data/allData.csv")
    data = data[data["Date"] >= "2005-01-01"]
    #print data
    
    # extract investment event and list for department: key: "code,date1,date2,date3...", value: department list
    investment_list = parser(data)
    
    
    #------------------------------------------------------
    
    # find the department
    #dep = pd.Series(data["Dep_Name"].values).unique()
    
    # make vectors
    #vectors = parser(dep,data)
    #corr_result = calculateCorrealtion(vectors)
    
    # write to csv
    #writeToCsv(corr_result)
    
    # read
    #print pd.read_csv("./Data/PersonCorr_Result.csv").sort(columns="Pearson_Corr", ascending=0).head(50)