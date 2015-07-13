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
from svm import svmCal
from svm import evaluation
from ljCao.indexCal import index_cal

# main program
def main():
    
    # 1. collect data from DB
    raw_data = collectData()
    
    # 2. Feature engineering
    (x_train, y_train, x_test ,y_real) = feature_engineering(raw_data)
    
    # 3. SVM
    svr_result = svmCal.svr_timeseries(x_train, y_train, x_test, y_real, 'rbf')
    
    # 4.Evaluation
    (NMSE,MAE,DS,WDS) = eval_results(svr_result)
    
    # 5. output result
    output_result(svr_result, NMSE, MAE, DS, WDS)

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
        sql = ('select * from newyorkexchange.ibm_historicalquotes_newyork')
        df = connectMysqlDB.query(cnx).pandasQuery(sql)
    finally:
        cnx.close()
    return df

# TODO @MJD
def feature_engineering(self,raw_data):
    input_data = raw_data['Date']['AdjClose']
    RDP_5 = index_cal.RDP_n(self, input_data, 5)
    RDP_10 = index_cal.RDP_n(self, input_data, 10)
    RDP_15 = index_cal.RDP_n(self, input_data, 15)
    RDP_20 = index_cal.RDP_n(self, input_data, 20)
    EMA_15 = index_cal.EMA_n(self, input_data, 5)
    pass

def eval_results(self,svr_result):
    eval = evaluation(svr_result)
    return (eval.evaluation.NMSE(),eval.evaluation.MAE(),eval.evaluation.DS(),eval.evaluation.WDS())

# TODO @MJD
def output_result(svr_result,NMSE,MAE,DS,WDS):
    pass

if __name__ == '__main__': main()