'''
Two methods which train the rf and return the forest(the trained model) and the relative
importances of input features, and test the model and return the probability distribution

Created on 27 Sep 2015

@author: peng
'''
import RFclass as rf

def trainRF(train_x, train_y, n_estimator):
    forest = rf.training().trainforest('rf', train_x, train_y, n_estimator)
    importances = rf.training().importance(forest, n_estimator)
    
    return forest, importances

def testRF(test_x, test_y, forest):
    output_RF = rf.test().testforest(test_x, test_y, forest)

