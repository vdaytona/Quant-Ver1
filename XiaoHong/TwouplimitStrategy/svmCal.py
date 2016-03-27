'''
This module is for svm calculation

Created on 2015/07/13

@author: Daytona
'''

import pandas as pd
from sklearn.svm import SVR
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
import evaluation
import time

class svr():
    def __init__(self):
        pass

    # TODO @MJD
    def svr_timeseries(self, x_train, y_train, x_test, y_real, kernel):
        '''
        c_set = [0.0001,0.001,0.01,0.1,1,10,100,1000]
        gamma_set = [0.0001,0.001,0.01,0.1,10,100,1000]
        epsilon_set = [0.0001,0.001,0.01,0.1,10,100,1000]
        '''
        parameter_start = -4
        parameter_stop = 2.5
        count = 10.0
        c_set = self.numberGenerate(parameter_start, parameter_stop, count)
        gamma_set = self.numberGenerate(parameter_start, parameter_stop, count)
        epsilon_set = self.numberGenerate(parameter_start, parameter_stop, count)
        #c_set = self.numberGenerate(-2, 0, count)
        #gamma_set = self.numberGenerate(1, 2, count)
        #epsilon_set = self.numberGenerate(-2, 0, count)
        print c_set
        c_min = 0
        gamma_min = 0
        epsilon_min = 0
        nmse_min = 100
        nmse_result = []
        ds_max = 0
        ds_result = []
        mae_result = []
        profit_result = []
        profit_max = -100
        doc_max = -1000 # R square
        doc_result = []
        loop_number = (1+count)**3
        loop_count = 0
        percent_count = 0.05
        t0 = time.time()
        #=======================================================================
        # c_set = [0.012559]
        # gamma_set = [25.059362]
        # epsilon_set = [0.012559]
        #=======================================================================
        for C in c_set:
            for gamma in gamma_set:
                for epsilon in epsilon_set:
                    loop_count += 1
                    if (C * gamma * epsilon != 0):
                        svr_rbf = SVR(kernel=kernel, C=C, gamma=gamma, epsilon = epsilon)
                        #svr_rbf.fit(x_train, y_train)
                        y_pred = svr_rbf.fit(x_train, y_train).predict(x_test)
                        result = pd.DataFrame()
                        result["Y_real"] = y_real
                        result["y_pred"] = y_pred
                        #x_axis = range(len(y_real))
                        #plt.plot(x_axis, y_real[:100], color = "r", )
                        #plt.plot(x_axis, y_pred[:100])
                        #=======================================================
                        # plt.scatter(x_axis, y_real - y_pred)
                        # plt.xlabel("Trade Count")
                        # plt.ylabel("Real High - Pred High")
                        # plt.legend()
                        # plt.show()
                        # plt.scatter(x_axis, y_real, color = "r", )
                        # plt.plot(x_axis, y_pred)
                        # plt.show()
                        #=======================================================
                        
                        nmse = evaluation.evaluation(y_real,y_pred).NMSE()
                        ds = evaluation.evaluation(y_real,y_pred).DS()
                        mae = evaluation.evaluation(y_real, y_pred).MAE()
                        #profit = ljCao.profit.profitLjCao(y_real,y_pred).Profit()
                        doc = r2_score(y_real,y_pred)
                        #corr = np.corrcoef(y_real, y_pred, bias = 0, ddof = None)[0,1]
                        #print("C = %f, gamma = %f, epsilon = %f, NMSE = %f, DS = %f, Profit = %f, DOC = %f" %(C,gamma,epsilon,nmse,ds,profit,doc))
                        nmse_result.append(nmse)
                        ds_result.append(ds)
                        doc_result.append(doc)
                        mae_result.append(mae)
                        if (doc > doc_max):
                            c_min = C
                            gamma_min = gamma
                            epsilon_min = epsilon
                            doc_max = doc
                    finished_percent = float(loop_count) / float(loop_number)
                    t1 = time.time()
                    if finished_percent > percent_count :
                        minutes_left = ((t1-t0) * (1.0 - finished_percent) / finished_percent) /60
                        print("%d%% %f minutes left" %(percent_count * 100, minutes_left ))
                        percent_count += 0.05
        svr_rbf = SVR(kernel=kernel, C=c_min, gamma=gamma_min, epsilon = epsilon_min)
        y_pred = svr_rbf.fit(x_train, y_train).predict(x_test)
        nmse = evaluation.evaluation(y_real,y_pred).NMSE()
        ds = evaluation.evaluation(y_real,y_pred).DS()
        mae = evaluation.evaluation(y_real,y_pred).MAE()
        #profit = ljCao.profit.profitLjCao(y_real,y_pred).Profit()
        #profit_time = ljCao.profit.profitLjCao(y_real,y_pred).ProfitTimeSeries()
        doc = r2_score(y_real,y_pred)
        
        print('MAX DS = %f' %ds)
        print('Hit rate = %f' %(float(ds) / float(len(y_pred))))
        print('NMSE = %f' %nmse)
        #print('Profit = %f' %profit)
        print('DOC = %f' %doc)
        print("MAE = %f" %mae)
        print("C = %f, gamma = %f, epsilon = %f" %(c_min,gamma_min,epsilon_min))
        x = range(len(y_real))
        plt.figure()
        plt.subplot2grid((2,2),(0, 0))
        plt.scatter(x, y_real, c='k', label='data')
        plt.scatter(x, y_pred, c='r', label='RBF model')
        plt.xlabel('data')
        plt.ylabel('target')
        plt.title('Support Vector Regression')
        #plt.legend()
        #plt.figure(2)
        #plt.subplot2grid((2,2),(0, 1))
        #x = range(len(profit_time))
        #plt.plot(x, profit_time, c='g', label='profit')
        #plt.xlabel('day')
        #plt.ylabel('profit (times)')
        #plt.figure(3)
        plt.subplot2grid((2,2),(1, 0))
        x = range(len(nmse_result))
        plt.plot(x, nmse_result, c='g', label='NMSE')
        plt.xlabel('Times')
        plt.ylabel('NMSE')
        plt.subplot2grid((2,2),(1, 1))
        plt.show()
        pass
        #return svr_result
        
    def numberGenerate(self,start, stop, count):
        result = []
        interval = (stop - start) / count
        for i in range (int(count+1)):
            result.append(10**(start + i * interval) /2)
        return result