#coding = utf-8
#encoding: utf-8
#This Python file uses the following encoding: utf-8

'''
Created on 2016/03/20
used to search the database in allData.csv
185       新时代证券有限责任公司包头广场西道证券营业部,新时代证券有限责任公司包头少先路证券营业部      0.428571
206        方正证券股份有限公司株洲新华西路证券营业部,光大证券股份有限公司长沙人民中路证券营业部      0.400000
252          信达证券股份有限公司朝阳五一街证券营业部,南京证券股份有限公司上海番禺路证券营业部      0.400000
207              方正证券股份有限公司株洲新华西路证券营业部,中原证券股份有限公司商丘分公司      0.400000
254              光大证券股份有限公司长沙人民中路证券营业部,中原证券股份有限公司商丘分公司      0.333333

@author: Daytona
'''

import pandas as pd

if __name__ == '__main__':
    data = pd.read_csv("./Data/allData.csv")
    # key word
    dep_Name1 = "方正证券股份有限公司株洲新华西路证券营业部"
    dep_Name2 = "光大证券股份有限公司长沙人民中路证券营业部"
    
    filter1_dictionary = dict()
    result_dictionary = dict()
    filter1 = data[data["Dep_Name"] == dep_Name1]
    for i in filter1.index :
        filter1_dictionary[filter1.loc[i]["Date"]] = filter1.loc[i]["Code_Name"]
    
    filter2 = data[data["Dep_Name"] == dep_Name2]
    print filter1
    print filter2
    for i in filter2.index :
        if filter2.loc[i]["Date"] in filter1_dictionary.keys() :
            result_dictionary[filter2.loc[i]["Date"]] = filter2.loc[i]["Code_Name"]
    date_list = result_dictionary.keys()
    
    for i in sorted(date_list) :
        print i + " : " + result_dictionary[i]