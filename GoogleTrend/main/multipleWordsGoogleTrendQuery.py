'''
Created on 2015/09/12

@author: Daytona
'''
import pandas as pd
import main as ma
import hmmPeriodDivison as hmm
import numpy as np

def main():
    #r = py.pyGTrends(username = "daytonaviola@gmail.com", password="Ding198573jie")
    #===========================================================================
    # for word in getSearchWords():
    #     r.download_report((word))
    #     #r.writer( "search_query_name.csv" )
    #     data = r.csv( section='Main',as_list= True)
    #     result = df.DataFrame(data)
    #     fileName = ('../Data/%s_google_trend.csv'%word)
    #     print ('%s finished' %word)
    #     result.to_csv(fileName, header = 1, columns= [0,1],index = False)
    #===========================================================================
    result_csv = pd.DataFrame(columns = ['Key_Word','Mean_Nasdaq_Change','Mean_Return','Variance_Nasdaq_Change','Variance_Return'])
    i = 0
    for word in getSearchWords():
        if i < 5 :
            hmmAnalyze(word, result_csv)
    print result_csv
    result_csv.to_csv('../Result/multipleWordsGoogleTrendsQuery.csv')

def getSearchWords():
    words = ['debt','color','stocks','restaurant','portfolio','inflation','housing','dow jones','revenue','economics',\
            'credit','markets','return','unemployment','money','religion','cancer','growth','investment','hedge','marriage',\
            'bonds','derivatives','headlines','profit','society','leverage','loss','cash','office','fine','stock market','banking',\
            'crisis','happy','car','nasdaq','finance','sell','invest','fed','house','metals','travel','returns','gain',\
             'default','present','holiday','water','rich','risk','gold','success','oil','war','economy','chance',\
             'short sell','lifestyle','greed','food','financial markets','movie','nyse','ore','buy and hold','opportunity','health',\
             'short selling','earnings','arts','culture','bubble','buy','trader','rare earths','tourism','politics','energy',\
             'consume','consumption','freedom','dividend','world','conflict','kitchen','forex','home','crash','transaction',\
             'garden','fond','train','labor','fun','environment','ring']
             

             
    return words

def hmmAnalyze(key_word, result_csv):
    # Acquiring data
    fileName = ('../Data/%s_google_trend.csv'%key_word)
    key_word_data = pd.read_csv(fileName,header = 1)
    nasdaq = pd.read_csv('../Data/nasdaq_historical_quotes.csv',header = 0)[['Date','Open','Close']]
    
    # Processing data
    preprocess_raw_data = ma.preprocessData(key_word_data,key_word, nasdaq)
    
    # add indicator into data for trading strategy
    trade_data = ma.excuteStrategy(preprocess_raw_data, key_word)
    
    # preprocess data
    trade_data = hmm.processTradingData(trade_data)
    
    # hmm model analyze
    print ('%s is under test' %key_word)
    result_model = hmm.hmmtest(trade_data, trade_data[['Nasdaq_Close_RDP_5','Strategy_Gross_Return_RDP_5']])
    columnName = []
    period = [1,2,5,15,30]
    column = ['Nasdaq_Close','Strategy_Gross_Return','Strategy_Cumulative_Return_R']
    for col in column:
        for i in period:
            col_name = str('%s_RDP_%s' % (col, str(i))) 
            columnName.append(col_name)
    
    outputResult(key_word,result_model, result_csv,trade_data)
    
    print('-------------------------')
    
    # Strategy backtest
    
    # Result Output
    #ma.writeToCSV(trade_data, random_data)
    pass

def outputResult(key_word, model, result_csv, trade_data):
    for i in range(model.n_components):
        result_csv.loc[len(result_csv)] = [key_word, model.means_[i][0],model.means_[i][1],\
                                           np.diag(model.covars_[i])[0],np.diag(model.covars_[i])[1]]
        #result_csv['Key_Word','Mean','Variance'] = key_word, model.means_[i], np.diag(model.covars_[i])
        #=======================================================================
        # print("%dth hidden state" % i)
        # print("mean = ", model.means_[i])
        # print("var = ", np.diag(model.covars_[i]))
        #=======================================================================

if __name__ == '__main__':
    main()