'''

---------------------------------------------------------------
Buy or Sell the open price, and close the trade at the close price
---------------------------------------------------------------

Created on 2015/07/17

@author: Daytona
'''

import connectMysqlDB
import mysql.connector
import numpy as np
import time
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from SVC.svcCal import svc
from SVC.randomforestCal import randomForestCal


# main program

def main():
    
    # 1. collect data from DB
    raw_year_data = collectData()
    t0 = time.time()
    threshold = 0.001
    
    # 2. Feature engineering
    (x_train, y_train, x_test ,y_real) = featureEnginnering(raw_year_data,threshold)
    
    # 3. Prediction
    # SVC
    y_pred_svc = svc().svc(x_train, y_train, x_test, y_real, 'rbf')
    
    # RandomForest
    # y_pred_randomforest = randomForestCal().randomforestClassifier(x_train, y_train, x_test, y_real)
    
    # 4. Evaluation
    #(NMSE,MAE,DS,WDS) = eval_results(svr_result)
    
    # 5. output result
    #output_result(svr_result, NMSE, MAE, DS, WDS)
    t1 = time.time()
    print ('Processing %f times took' % (t1 - t0), 'seconds')
    print('finished')

def collectData():
    host='149.171.37.73'
    userName='PengJiang'
    password='jiangpengjun'
    database='sydneyexchange'
    cnx = mysql.connector.connect();
    try:
        #get cnx used for connecting DB
        cnx = connectMysqlDB.cnxStock(host=host,userName=userName,password=password,database=database).connect()
        
        # collecting IBM historical data
        sql = ('select Date, (Open * AdjClose / Close) AdjOpen, AdjClose from newyorkexchange.ibm_historicalquotes_newyork where Date > \'2014-1-1\'')
        df = connectMysqlDB.query(cnx).pandasQuery(sql)
    finally:
        cnx.close()
    return df

def featureEnginnering(raw_year_data, threshold):
    '''
    input
    ['Date', 'AdjOpen', 'AdjClose']
    output
    ['Date','Change_Per','AdjClose_Previous','AdjOpen_Today', 'If_Trade']
    
    Change_Per:
    Change_Per = (Today AdjOpen - Previous AdjClose) / (Previous AdjClose)
    
    If_trade:
    When Change Per > 0 and today AdjOpen is higher than today AdjClose, then 1 (excute sell)
    elif:
    When Change Per < 0 and today AdjOpen is lower than today AdjClose, then 1 (excute buy)
    else:
    0
    '''
    n = len(raw_year_data.index)
    change_per = []
    change_per.append(None)
    adjclose_previous = []
    adjclose_previous.append(None)
    if_trade = []
    if_trade.append(None)
    profit = []
    loss = []
    trade_day = 0
    wrong_day = 0;
    wrong_day_set = []
    wrong_day_set.append(None)
    for i in range (1,n):
        change = (raw_year_data['AdjOpen'][i] - raw_year_data['AdjClose'][i-1])/raw_year_data['AdjClose'][i-1]
        change_per.append(change)
        close_open = raw_year_data['AdjClose'][i] - raw_year_data['AdjOpen'][i] 
        adjclose_previous.append(raw_year_data['AdjClose'][i-1])
        if (change > threshold and (close_open < 0 )) :
            trade_day += 1
            wrong_day_set.append(0)
            if_trade.append(1)
            profit.append(-close_open/raw_year_data['AdjOpen'][i])
        elif(change < -threshold and (close_open > 0 )): 
            if_trade.append(1)
            trade_day += 1
            wrong_day_set.append(0)
            profit.append(close_open/raw_year_data['AdjOpen'][i])
        elif (change > threshold and (close_open >= 0 )):
            wrong_day += 1
            trade_day += 1
            wrong_day_set.append(1)
            if_trade.append(0)
            loss.append(-close_open/raw_year_data['AdjOpen'][i])
        elif (change < -threshold and (close_open <= 0 )):
            wrong_day += 1
            trade_day += 1
            wrong_day_set.append(1)
            if_trade.append(0)
            loss.append(close_open/raw_year_data['AdjOpen'][i])
        else:
            if_trade.append(0)
            wrong_day_set.append(0)
    
    #===========================================================================
    # print('Potential conducting trade (open_close_change > threshold, or open_close_change < threshold) in %f%% days.' %(float(np.count_nonzero(if_trade)) / float(len(if_trade)) *100))
    # print('In potential trading days, %f%% cause loss (wrong day), which result in average %f%% loss.' %(float(wrong_day) / float(trade_day) *100, np.mean(loss) * 100 ))
    # print('At the same time, the average profit in other potential (win) days is %f%%.' %(np.mean(profit) * 100))
    #===========================================================================
   
    raw_year_data['Change_Per'] = change_per
    raw_year_data['AdjClose_Previous'] = adjclose_previous
    raw_year_data['AdjOpen_Today'] = raw_year_data['AdjOpen']
    raw_year_data['if_trade'] = if_trade
    raw_year_data['Wrong_Day'] = wrong_day_set
    raw_year_data = raw_year_data.dropna()
    features = raw_year_data[['Change_Per','AdjClose_Previous', 'AdjOpen_Today']]
    
    objective = raw_year_data['if_trade']
    train_ratio = 0.8
    (x_train, x_test) = divideTrainTest(features, train_ratio)
    (y_train,y_real) = divideTrainTest(objective, train_ratio)
    return (x_train, y_train, x_test, y_real)

    '''
    plt.figure(1)
    plt.subplot2grid((2,2),(0, 0))
    plt.scatter(raw_year_data[raw_year_data['if_trade'] == 0][['Change_Per']], raw_year_data[raw_year_data['if_trade'] == 0][['AdjClose_Previous']], c='k', label='data')
    plt.scatter(raw_year_data[raw_year_data['if_trade'] == 1][['Change_Per']], raw_year_data[raw_year_data['if_trade'] == 1][['AdjClose_Previous']], c='red', label='data')
    plt.xlabel('change_per')
    plt.ylabel('close_previous')
    plt.title('change_per vs. close_previous')
    
    plt.subplot2grid((2,2),(0, 1))
    plt.scatter(raw_year_data[raw_year_data['if_trade'] == 0][['Change_Per']], raw_year_data[raw_year_data['if_trade'] == 0][['AdjOpen_Today']], c='k', label='data')
    plt.scatter(raw_year_data[raw_year_data['if_trade'] == 1][['Change_Per']], raw_year_data[raw_year_data['if_trade'] == 1][['AdjOpen_Today']], c='red', label='data')
    plt.xlabel('change_per')
    plt.ylabel('open_today')
    plt.title('change_per vs. open_today')
    
    plt.subplot2grid((2,2),(1, 0))
    plt.scatter(raw_year_data[raw_year_data['Wrong_Day'] == 1][['Change_Per']], raw_year_data[raw_year_data['Wrong_Day'] == 1][['AdjClose_Previous']], c='k', label='data')
    plt.scatter(raw_year_data[raw_year_data['if_trade'] == 1][['Change_Per']], raw_year_data[raw_year_data['if_trade'] == 1][['AdjClose_Previous']], c='red', label='data')
    plt.xlabel('Change_Per')
    plt.ylabel('close_previous')
    plt.legend()
    plt.title('open_today vs. close_previous')
    
    plt.subplot2grid((2,2),(1, 1))
    if_trade_density = []
    density_range = 20
    for i in range(density_range-1,len(raw_year_data.index)):
        if_trade_density.append(np.mean(raw_year_data[['if_trade']][i-9 : i]))        
    x= range(len(if_trade_density))
    plt.scatter(x,if_trade_density, c='k', label='data')
    plt.xlabel('day')
    plt.ylabel('trading density in last %d days' %density_range)
    plt.title('Trading density')
    
    #plt.show()
    '''

def divideTrainTest(raw_year_data,train_ratio):
    raw_data_size = len(raw_year_data)
    train_size = int(raw_data_size * train_ratio)
    train_data = raw_year_data[0:train_size-1]
    test_data = raw_year_data[train_size:raw_data_size]
    return (train_data,test_data)

if __name__ == '__main__': main()