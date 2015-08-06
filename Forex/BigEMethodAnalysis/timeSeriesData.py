'''
Created on 6 Aug 2015

@author: purewin7
'''

import pandas as pd

class Balance():
    '''
    Container for trading result
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.baclance_record = pd.DataFrame(columns='Date','Open_Time','Type','Size','Item',
                                            'Open_Price','Stop_Limit','Take_Profit','Close_Time',
                                            'Close_Price','Commission','Taxes','Swap','Pips','Profit')