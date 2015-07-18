'''
Created on 2015/07/18

@author: Daytona
'''
from sklearn.ensemble import RandomForestClassifier

class randomForestCal():
    def __init__(self):
        pass

    # TODO @MJD
    def randomforestClassifier(self, x_train, y_train, x_test, y_real):
        
        
        forest = RandomForestClassifier(10)
        # Fit the training data to the Survived labels and create the decision trees
        forest = forest.fit(x_train,y_train)
        # Take the same decision trees and run it on the test data
        y_pred = forest.predict(x_test)
        
        profit_day = 0
        loss_day = 0
        for i in range(len(y_real)) :
            if y_real[i] == 0 and y_pred[i] == 1:
                loss_day += 1
            elif y_real[i] == 1 and y_pred[i] == 1:
                profit_day += 1
        print ('loss day is %d, profit day is %d for %f%% by SVM' % (loss_day,profit_day, float(profit_day) / float(profit_day + loss_day) * 100))
        
        return y_pred
    
    
    