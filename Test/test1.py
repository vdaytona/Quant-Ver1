'''
Created on 2015/08/12

@author: Daytona
'''

import numpy as np
from scipy import stats
#np.random.seed(12345678)

from sknn.mlp import Classifier, Layer

nn = Classifier(
    layers=[
        Layer("Rectifier", units=100),
        Layer("Linear")],
    learning_rate=0.02,
    n_iter=10)
nn.fit(X_train, y_train)

y_valid = nn.predict(X_valid)

score = nn.score(X_test, y_test)