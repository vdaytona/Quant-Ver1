#coding = utf-8
#encoding: utf-8
#This Python file uses the following encoding: utf-8

'''
Created on 8 May 2016
create a edge list for graph clustering

@author: Daytona
'''

import pandas as pd

if __name__ == '__main__':
    
    raw_data = pd.read_csv("./Data/allData.csv")
    #print raw_data
    
    dep_list = pd.Series(raw_data["Dep_Name"].values).unique()
    #print dep_list
    
    dep_list_id_dict = dict()
    number = 1
    # make name dict
    for dep_name in dep_list :
        dep_list_id_dict[dep_name] = number
        number += 1
    #print dep_list_dict
    
    # find unique combination of the list
    event_list = raw_data[["Date","List_Type","Code","Buy_Sell"]].drop_duplicates()
    #event_list = raw_data[["Date","List_Type","Code"]].drop_duplicates()
    
    edge_list = []
    selectionA = []
    selectionB = []
    print "start analyze"
    for item in event_list.index :
        keys = raw_data[["Date","List_Type","Code","Buy_Sell"]].loc[item]
        #keys = raw_data[["Date","List_Type","Code"]].loc[item]
        key_date = keys["Date"]
        key_list_type = keys["List_Type"]
        key_code = keys["Code"]
        key_buy_sell = keys["Buy_Sell"]
        dep_list = raw_data.loc[(raw_data["Date"] == key_date) & \
                                 (raw_data["List_Type"] == key_list_type) & \
                                 (raw_data["Code"] == key_code) & \
                                 (raw_data["Buy_Sell"] == key_buy_sell) ,"Dep_Name"]
        
        #=======================================================================
        # dep_list = raw_data.loc[(raw_data["Date"] == key_date) & \
        #                         (raw_data["List_Type"] == key_list_type) & \
        #                         (raw_data["Code"] == key_code) ,"Dep_Name"]
        #=======================================================================
        
        # get dep name for each day of distinct stock and distinct buy or sell 
        dep_id = []
        for i in dep_list.values :
            dep_id.append(dep_list_id_dict[i])
        
        # get unique
        dep_id = list(set(dep_id))
        # sort in ascending order
        dep_id = sorted(dep_id)
        
        for i in range(len(dep_id)-1) :
            for j in range(i+1,len(dep_id)) :
                selectionA.append(dep_id[i])
                selectionB.append(dep_id[j])
                
    print "finish analyze"
    edge_list = pd.DataFrame()
    edge_list["A"] = selectionA
    edge_list["B"] = selectionB
    
    edge_list["Duplicated"] = edge_list.duplicated(take_last = True) | edge_list.duplicated()
    
    count = []
    for i in edge_list.index :
        if edge_list["Duplicated"][i] == False :
            count.append(1)
        else :
            size = len(edge_list.loc[(edge_list["A"] == edge_list["A"][i]) & \
                                (edge_list["B"] == edge_list["B"][i])])
            count.append(size)
    edge_list["Weight"] = count
    edge_list = edge_list.drop_duplicates()
    edge_list[["A","B","Weight"]].to_csv("./Result/edge_list_v1.csv",index=False)
    