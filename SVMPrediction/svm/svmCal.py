'''
This module is for svm calculation

Created on 2015/07/13

@author: Daytona
'''

from sklearn.svm import SVR

def __init__(self):
    pass

# TODO @MJD
def svr_timeseries(self, x_train, y_train, x_test, y_real, kernel):
    svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1, epsilon = 0.1)
    y_pred = svr_rbf.fit(x_train, y_train).predict(x_test)
    svr_result = y_pred + y_real
    return svr_result
        