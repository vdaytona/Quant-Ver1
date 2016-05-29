'''
Created on 28 May 2016
To merge USD/JPY, JPY/EUR, EUR/GBP, GBP/CHF with time line
@author: purewin7
'''

import pandas as pd

def run():
    USDJPY = pd.read_csv("../Data/USDJPY240_cal.csv",header=None)[[0,1,5]]
    JPYEUR = pd.read_csv("../Data/JPYEUR240_cal.csv",header=None)[[0,1,5]]
    EURGBP = pd.read_csv("../Data/EURGBP240.csv",header=None)[[0,1,5]]
    GBPCHF = pd.read_csv("../Data/GBPCHF240.csv",header=None)[[0,1,5]]
    result = pd.merge(USDJPY, JPYEUR, how="inner", on = [0,1]).dropna().rename(columns = {'5_x' : 'USDJPY', '5_y' : 'JPYEUR'})
    
    
    result = pd.merge(result, EURGBP, how="inner", on = [0,1]).dropna().rename(columns = {5 : 'EURGBP'})
    result = pd.merge(result, GBPCHF, how="inner", on = [0,1]).dropna().rename(columns = {5 : 'GBPCHF'})
    #for pair in ["USDJPY","JPYEUR","EURGBP","GBPCHF"] :
    #    result[pair] = (result[pair] - result[pair].min()) / (result[pair].max() - result[pair].min())
    #print USDJPY
    #print JPYEUR
    print result
    result.to_csv("../Data/combination.csv")

if __name__ == '__main__':
    run()