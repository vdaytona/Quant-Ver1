'''
===================================================================
Application of support vector machines in financial time series forecasting
===================================================================

This program is to predict time series data (stock price here) using SVM based on paper
"Application of support vector machines in financial time series forecasting" 

Created on 2015/07/13

@author: Daytona
'''
import connectMysqlDB
import mysql.connector
import pandas
import time
from svm import evaluation
from ljCao.indexCal import index_cal
from svm.svmCal import svr

# main program
def main():
    t0 = time.time()
    # 1. collect data from DB
    raw_data = collectData()
    
    # 2. Feature engineering
    (x_train, y_train, x_test ,y_real) = feature_engineering(raw_data)
    
    # 3. SVM
    svr().svr_timeseries(x_train, y_train, x_test, y_real, 'rbf')
    
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
        sql = ('select * from newyorkexchange.ibm_historicalquotes_newyork where Date > \'2015-1-1\'')
        df = connectMysqlDB.query(cnx).pandasQuery(sql)
    finally:
        cnx.close()
    return df

# TODO @MJD
def feature_engineering(raw_data):
    input_data = raw_data[['Date','AdjClose','Volume']].dropna()
    train_ratio = 0.9
    
    
    #print(input_data['AdjClose'].pct_change(periods = 5))
    
    #Vol_5 = index_cal().VOL_n(input_data, 5)
    #Vol_10 = index_cal().VOL_n(input_data, 10)
    #Vol_15 = index_cal().VOL_n(input_data, 15)
    #Vol_20 = index_cal().VOL_n(input_data, 20)
    #RDV_5 = index_cal().RDV_n(input_data, 5)
    #RDV_10 = index_cal().RDV_n(input_data, 10)
    #RDV_15 = index_cal().RDV_n(input_data, 15)
    #RDV_20 = index_cal().RDV_n(input_data, 20)
    RDP_5 = index_cal().RDP_n(input_data, 5)
    RDP_10 = index_cal().RDP_n(input_data, 10)
    RDP_15 = index_cal().RDP_n(input_data, 15)
    RDP_20 = index_cal().RDP_n(input_data, 20)
    RDP_plus_5 = index_cal().RDP_plus_n(input_data, 5)
    #RDP_plus_5['RDP+90'].hist(bins=50)
    #p.ion()
    #p.show()
    features = mergeColumnByDate(RDP_5,RDP_10,RDP_15,RDP_20,RDP_plus_5)
    (train_data, test_data) = divideTrainTest(features, train_ratio)
    
    x_train = train_data[['RDP-5','RDP-10','RDP-15','RDP-20']]
    y_train = train_data['RDP+5']
    x_test = test_data[['RDP-5','RDP-10','RDP-15','RDP-20']]
    y_real = test_data['RDP+5']
    
    
    return (x_train,y_train,x_test,y_real)
    #EMA_15 = index_cal.EMA_n(input_data, 15)
    pass

    # split train and test data
def divideTrainTest(raw_data,train_ratio):
    raw_data_size = len(raw_data.index)
    train_size = int(raw_data_size * train_ratio)
    train_data = raw_data[0:train_size-1]
    test_data = raw_data[train_size:raw_data_size]
    return (train_data,test_data)

def mergeColumnByDate(*args):
    result = args[0]
    if(len(args) > 1):
        for i in range(1,len(args)):
            result = pandas.merge(result, args[i], left_on = 'Date', right_on = 'Date', how = 'outer')
    return result.dropna()
    pass
    

def eval_results(self,svr_result):
    eval = evaluation(svr_result)
    return (eval.evaluation.NMSE(),eval.evaluation.MAE(),eval.evaluation.DS(),eval.evaluation.WDS())

# TODO @MJD
def output_result(svr_result,NMSE,MAE,DS,WDS):
    pass

if __name__ == '__main__': main()