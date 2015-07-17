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
from theano.tests import diverse_tests
from sklearn.ensemble import RandomForestClassifier


# main program

def main():
    
    # 1. collect data from DB
    raw_data = collectData()
    t0 = time.time()
    
    # 2. Feature engineering
    (x_train, y_train, x_test ,y_real) = featureEnginnering(raw_data)
    
    y_pred = randomForest(x_train, y_train, x_test)
    print(y_real.values)
    wrong_count = float(np.count_nonzero((y_real.values -y_pred)))
    all_count = float(len(y_pred))
    hit_rate = (all_count - wrong_count) / all_count
    print hit_rate
    # 3. SVM
    #svr().svr_timeseries(x_train, y_train, x_test, y_real, 'rbf')
    
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
        sql = ('select Date, (Open * AdjClose / Close) AdjOpen, AdjClose from newyorkexchange.ibm_historicalquotes_newyork where Date > \'2015-1-1\'')
        df = connectMysqlDB.query(cnx).pandasQuery(sql)
    finally:
        cnx.close()
    return df

def featureEnginnering(raw_data):
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
    n = len(raw_data.index)
    change_per = []
    change_per.append(None)
    adjclose_previous = []
    adjclose_previous.append(None)
    if_trade = []
    if_trade.append(None)
    for i in range (1,n):
        change = (raw_data['AdjOpen'][i] - raw_data['AdjClose'][i-1])/raw_data['AdjClose'][i-1]
        change_per.append(change)
        adjclose_previous.append(raw_data['AdjClose'][i-1])
        if (change * (raw_data['AdjOpen'][i] - raw_data['AdjClose'][i]) > 0) : 
            if_trade.append(1)
        else: 
            if_trade.append(0)
        
    raw_data['Change_Per'] = change_per
    raw_data['AdjClose_Previous'] = adjclose_previous
    raw_data['AdjOpen_Today'] = raw_data['AdjOpen']
    raw_data['if_trade'] = if_trade
    raw_data = raw_data.dropna()
    features = raw_data[['Change_Per','AdjClose_Previous', 'AdjOpen_Today']]
    objective = raw_data['if_trade']
    train_ratio = 0.8
    (x_train, x_test) = divideTrainTest(features, train_ratio)
    (y_train,y_real) = divideTrainTest(objective, train_ratio)
    return (x_train, y_train, x_test, y_real)

def divideTrainTest(raw_data,train_ratio):
    raw_data_size = len(raw_data)
    train_size = int(raw_data_size * train_ratio)
    train_data = raw_data[0:train_size-1]
    test_data = raw_data[train_size:raw_data_size]
    return (train_data,test_data)
    
    pass

def randomForest(x_train, y_train, x_test):
    forest = RandomForestClassifier(n_estimators = 100)


    # Fit the training data to the Survived labels and create the decision trees
    forest = forest.fit(x_train,y_train)

    # Take the same decision trees and run it on the test data
    output = forest.predict(x_test)
    print(output)
    return output
if __name__ == '__main__': main()