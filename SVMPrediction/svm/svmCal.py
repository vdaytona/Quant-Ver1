'''
This module is for svm calculation

Created on 2015/07/13

@author: Daytona
'''

from sklearn.svm import SVR
import matplotlib.pyplot as plt
import numpy as np
import evaluation

class svr():
    def __init__(self):
        pass

    # TODO @MJD
    def svr_timeseries(self, x_train, y_train, x_test, y_real, kernel):
        #'''
        c_set = [0.0001,0.001,0.01,0.1,1,10,100,1000]
        gamma_set = [0.0001,0.001,0.01,0.1,10,100,1000]
        epsilon_set = [0.0001,0.001,0.01,0.1,10,100,1000]
        c_min = 0
        gamma_min = 0
        epsilon_min = 0
        #nmse_min = 100
        #nmse_result = []
        ds_max = 0
        ds_result = []
        profit_result = []
        for C in c_set:
            for gamma in gamma_set:
                for epsilon in epsilon_set:
                    svr_rbf = SVR(kernel=kernel, C=C, gamma=gamma, epsilon = epsilon)
                    #svr_rbf.fit(x_train, y_train)
                    y_pred = svr_rbf.fit(x_train, y_train).predict(x_test)
                    #nmse = evaluation.evaluation(y_real.values,y_pred).NMSE()
                    ds = evaluation.evaluation(y_real.values,y_pred).DS()
                    #corr = np.corrcoef(y_real.values, y_pred, bias = 0, ddof = None)[0,1]
                    print("C = %f, gamma = %f, epsilon = %f, DS = %f" %(C,gamma,epsilon,ds))
                    #nmse_result.append(nmse)
                    ds_result.append(ds)
                    if (ds > ds_max):
                        c_min = C
                        gamma_min = gamma
                        epsilon_min = epsilon
                        ds_max = ds
        svr_rbf = SVR(kernel=kernel, C=c_min, gamma=gamma_min, epsilon = epsilon_min)
        y_pred = svr_rbf.fit(x_train, y_train).predict(x_test)
        nmse = evaluation.evaluation(y_real.values,y_pred).NMSE()
        ds = evaluation.evaluation(y_real.values,y_pred).DS()
        profit = evaluation.evaluation(y_real.values,y_pred).Profit()
        profit_time = evaluation.evaluation(y_real.values,y_pred).ProfitTimeSeries()
        print('MAX DS = %f' %ds)
        print('Hit rate = %f' %(float(ds) / float(len(y_pred))))
        print('NMSE = %f' %nmse)
        print('Profit = %f' %profit)
        x = range(len(y_real.index))
        plt.scatter(x, y_real, c='k', label='data')
        plt.hold('on')
        plt.plot(x, y_pred, c='g', label='RBF model')
        plt.xlabel('data')
        plt.ylabel('target')
        plt.title('Support Vector Regression')
        plt.legend()
        plt.show()
        x = range(len(profit_time))
        plt.plot(x, profit_time, c='g', label='profit')
        plt.xlabel('day')
        plt.ylabel('profit')
        plt.show()
        
        pass
        #return svr_result
        
    def numberGenerate(self,start, stop, times):
        
        pass