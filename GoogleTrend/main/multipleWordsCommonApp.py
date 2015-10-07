'''
Created on 2015/10/07

@author: Daytona
'''

import os
import pandas

def importAllGoogleTrendsResults():
    # get fileName
    file_name_list = getGoogleTrendsResultFileName()
    
    # collecting all google  trends data
    google_trends_result_list = getGoogleTrendsDataFromCsv(file_name_list)
    
    return google_trends_result_list


def getGoogleTrendsResultFileName():
    # get xxx_google_trends.csv file names in ./Data folder
    file_name_list = []
    folder_path = "../Data"
    file_names = os.listdir(folder_path)
    for file_name in file_names:
        if("google_trend" in file_name):
            file_name_list.append(os.path.join(folder_path,file_name))
    return file_name_list

def getGoogleTrendsDataFromCsv(file_name_list):
    # import google trends data in pandas from .csv
    google_trends_result_list = []
    for file_name in file_name_list:
        google_trends_result_list.append(pandas.read_csv(file_name,header = 1))
    return google_trends_result_list


def mergeMultipleGoogleTrendsData(origin_data_list):
    
    pass
