'''
Created on 2015/07/18

@author: Daytona
'''

from sklearn.svm import SVC
import time
import numpy as np

class svc():
    def __init__(self):
        pass

    # TODO @MJD
    def svc(self, x_train, y_train, x_test, y_real, kernel):
        # change y_real to numpy.array type
        y_real = y_real.values
        
        # set parameter range
        parameter_start = -10
        parameter_stop = 10
        count = 20
        c_set = self.numberGenerate(parameter_start, parameter_stop, count)
        gamma_set = self.numberGenerate(parameter_start, parameter_stop, count)
        
        # preset the parameters container for the best result
        c_max_profit_day = 0
        gamma_max_profit_day = 0
        c_max_profit_percent = 0
        gamma_max_profit_percent = 0
        
        # container for the best result
        max_profit_percent = 0
        max_profit_percent_all_day = 0
        max_profit_day = 0
        max_profit_day_all_day = 0
        
        # loop control number
        loop_number = (count+1)**2
        loop_count = 0
        percent_count = 0.05
        t0 = time.time()
        
        for C in c_set:
            for gamma in gamma_set:
                # loop plus one
                loop_count += 1
                
                # to confirm whether parameters has no zero value
                if (C * gamma != 0):
                    # predit and fit
                    y_pred = SVC(kernel=kernel , gamma= gamma, C=C).fit(x_train, y_train).predict(x_test)
                    
                    # if prediction has trading record evaluate the result
                    if np.count_nonzero(y_pred) > 0 :
                        
                        # count the profit day and loss day
                        profit_day = 0
                        loss_day = 0
                        for i in range(len(y_real)) :
                            if y_real[i] == 0 and y_pred[i] == 1:
                                loss_day += 1
                            elif y_real[i] == 1 and y_pred[i] == 1:
                                profit_day += 1
                        profit_percent = float(profit_day) / float(profit_day + loss_day) * 100
                        
                        # save the parameter for the best result
                        if profit_day > max_profit_day :
                            max_profit_day = profit_day
                            max_profit_day_all_day = profit_day + loss_day
                            c_max_profit_day = C
                            gamma_max_profit_day = gamma
                        if profit_percent > max_profit_percent :
                            max_profit_percent = profit_percent
                            max_profit_percent_all_day = profit_day + loss_day
                            c_max_profit_percent = C
                            gamma_max_profit_percent = gamma
                        
                # loop count and show left time
                finished_percent = float(loop_count) / float(loop_number)
                t1 = time.time()
                if finished_percent > percent_count :
                    minutes_lfet = ((t1-t0) * (1.0 - finished_percent) / finished_percent) /60
                    print("%d%% %f minutes left" %(percent_count * 100, minutes_lfet ))
                    percent_count += 0.05
        # print result
        print('hmmtest day: %d' %len(y_real))
        print('Max profit day:')
        print ('Profit day is %d for %f%% by SVM' % (max_profit_day, float(max_profit_day) / float(max_profit_day_all_day) * 100))
        print('Parameters : Gamma = %f , C = %f4d' %(gamma_max_profit_day, c_max_profit_day))
        print('Max profit percent day:')
        print ('Profit day is %d for %f%% by SVM' % (max_profit_percent_all_day, max_profit_percent))
        print('Parameters : Gamma = %f , C = %f' %(gamma_max_profit_percent, c_max_profit_percent))
        
        return y_pred
    
    def numberGenerate(self,start, stop, count):
        result = []
        interval = (stop - start) / count
        for i in range (0,count+1):
            result.append(10**(start + i * interval) /2)
        return result