#coding = utf-8
#encoding: utf-8
#This Python file uses the following encoding: utf-8
'''
Created on 2016/03/20
v1
1. make the vector of each department 0 : not on the list, 1: on the list
2. calculate the similarity of each pair of vectors, and rank the result with the similarity (correlation)
3. only for pairs compare 
@author: Daytona
'''

import pandas as pd
import numpy as np
import scipy.stats as stats

def parser(dep, data):
    # make dictionary
    result_dictionary = dict()
    for dep_name in dep :
        vector = []
        result_dictionary[dep_name] = vector
    # find unique date
    date = pd.Series(data["Date"].values).unique()
    
    for i in range(len(date)) :
        oneData = data[data["Date"] == date[i]]
        trade_code = pd.Series(oneData["Code"].values).unique()
        for code in trade_code:
            # add 0 to each vector
            for keys in result_dictionary.keys() :
                result_dictionary[keys].append(0)
            # find listed code for iteration
            data_one_code = oneData[oneData["Code"] == code]
            for j in data_one_code.index:
                record = data_one_code.loc[j]
                # if it appears on list , change the last value to 1 or -1 for buy or sell condition
                #print record["Buy_Sell"]
                state = 1 if record["Buy_Sell"] == "buy" else -1
                result_dictionary[record["Dep_Name"]][-1] = state
    #for key in result_dictionary:
        #print result_dictionary[key]
    return result_dictionary

def calculateCorrealtion(vectors):
    result = []
    keys = vectors.keys()
    print len(keys)
    for i in range(0,len(keys)-1):
        print i 
        for j in range(i+1, len(keys)) :
            if findNonZeroNumber(vectors[keys[i]]) >= 3 and findNonZeroNumber(vectors[keys[j]]) >= 3 :
                cor, val = stats.pearsonr(vectors[keys[i]], vectors[keys[j]])
                result.append(cor)
    print max(result)

def findNonZeroNumber(input):
    result = 0
    for num in input:
        result += abs(num)
    return result

if __name__ == '__main__':
    # read the file from allData.csv
    data =  pd.read_csv("./Data/allData.csv")
    
    # find the department
    dep = pd.Series(data["Dep_Name"].values).unique()
    
    # make vectors
    vectors = parser(dep, data)
    
    # calculate the similarity
    calculateCorrealtion(vectors)
    
    # rank
    
    pass