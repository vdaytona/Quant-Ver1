from pandas.core.frame import DataFrame
import numpy as np
import pandas as pd
from sklearn import preprocessing
import matplotlib.pyplot as plt
from sklearn.metrics.classification import accuracy_score, confusion_matrix, classification_report
import csv
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, BaggingClassifier, ExtraTreesClassifier, GradientBoostingClassifier
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.ensemble.partial_dependence import partial_dependence
from mpl_toolkits.mplot3d import Axes3D


class training(object):
    def __init__(self):
        print "This is for training set**************************************"
        
    def trainforest(self, seed, train, trainlabel, number_trees):
        seed_of_tree = {'rf': RandomForestClassifier(n_estimators= number_trees, max_features=8), 
                      'adb': AdaBoostClassifier(n_estimators= number_trees),
                      'bag': BaggingClassifier(n_estimators= number_trees, max_features=8),
                      'ext': ExtraTreesClassifier(n_estimators= number_trees, max_features=8),
                      'gbt': GradientBoostingClassifier(n_estimators= number_trees, max_features=8)}
        rawforest=seed_of_tree[seed]
        forest=rawforest.fit(train,trainlabel)
        outputtrain= forest.predict(train)
        accuracytrain = accuracy_score(trainlabel, outputtrain)        
        print "The size of the training set is %r , %r" %(np.shape(train)[0],np.shape(train)[1])
        #---------------------------------------- print "The method is %r" %seed
        # print "The accuracy for the training set is %r" %accuracytrain, "and the confusion matrix is"
        #------------------------ print confusion_matrix(outputtrain,trainlabel)
        return (forest)
    
    def importance(self, forest, n):
        print "************************this is the output of relative importance**************"
        print(forest.feature_importances_)
        importances=forest.feature_importances_
        return importances
#        std=np.std([tree.feature_importances_ for tree in forest.estimators_],axis=0)
        #--------------------------------- indices=np.argsort(importances)[::-1]
        #--------------------------------------------------------- print indices
        #--------------------------------------------- print("Feature ranking:")
        #--------------------------------------------------- for f in range(12):
             # print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))
        #---------------------------------------------------------- plt.figure()
        #------------------------------ plt.bar(range(12), importances[indices],
            #---------------------------------------- color="c", align="center")
        # #------------------------------ plt.bar(range(12), importances[indices],
            # #--------------------- color="c", yerr=std[indices], align="center")
        #--------------------------------------- plt.xticks(range(n), indices+1)
        #----------------------------------------------------- plt.xlim([-1, n])
        #-------------------------- plt.xlabel('The input feature', fontsize=16)
        #------------------------ plt.ylabel('Relative importance', fontsize=16)
        #------------------------------------------------------------ plt.show()
    
    
    def dependence(self, forest, train, feature_set):
        print "******************this is the output of dependences of features"
        fig, axs = plot_partial_dependence(forest, train, features=feature_set
                                           )
        plt.show()
        
        
    def dependence3d(self, forest, train, feature_set):
        print "******************this is the output of dependences of features"
        fig = plt.figure()
        pdp, (x_axis, y_axis) = partial_dependence(forest, feature_set,
                                           X=train)
        XX, YY = np.meshgrid(x_axis, y_axis)
        Z = pdp.T.reshape(XX.shape)
        ax = Axes3D(fig)
        surf = ax.plot_surface(XX, YY, Z, rstride=1, cstride=1, cmap=plt.cm.BuPu)
        #------------------------------- ax.set_xlabel(names[target_feature[0]])
        #------------------------------- ax.set_ylabel(names[target_feature[1]])
        ax.set_zlabel('Partial dependence')
        #  pretty init view
        ax.view_init(elev=22, azim=122)
        plt.colorbar(surf)
        plt.suptitle('Partial dependence of house value on median age and '
                    'average occupancy')
        plt.subplots_adjust(top=0.9)
        
        plt.show()
        

class test():    
    def __init__(self):
        print "*******************************************"
        
    def testforest(self, test, testlabel,forest):
        outputtest= forest.predict(test) 
        accuracytrain = accuracy_score(testlabel, outputtest)
        #----------------------------------- print "The size of the test set is"
        #------------------------------------------------- print  np.shape(test)
        # print "The accuracy for the test set is %r" %accuracytrain, "and the confusion matrix is"
        #-------------------------- print confusion_matrix(outputtest,testlabel)
        #-------------------- print classification_report(testlabel, outputtest)
        # generate probability
        #-------------------------------- outputproba=forest.predict_proba(test)
        # outperfor={'prob0':outputproba[:,0],'prob1':outputproba[:,1],'output':outputtest,'target':testlabel}
        #----------------------------------------- outframe=DataFrame(outperfor)
        #print outframe
        #outframe.to_csv(r'D:\allprob.csv', header=0)
        return accuracytrain
        #return (outframe)
        
         


