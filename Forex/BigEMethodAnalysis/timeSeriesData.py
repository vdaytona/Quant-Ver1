'''
Created on 6 Aug 2015

@author: purewin7
'''

import pandas as pd
from twisted.trial._synctest import Todo

class timeSeriesData():
    '''
    Container for historical trading data
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        self.baclance_record = pd.DataFrame(columns='Date','Open_Time','Type','Size','Item',
                                            'Open_Price','Stop_Limit','Take_Profit','Close_Time',
                                            'Close_Price','Commission','Taxes','Swap','Pips','Profit')
        
    @Todo
    def set_data(self, pair, time_frame):
        '''
        import historical trading data
        '''
        pass
    
    @Todo
    def get_data(self, pair, time_frame, date_after = None, date_before = None):
        '''
        export historical trading data
        '''
        pass
    
    @Todo
    def get_merged_data(self, pair):
        '''
        export historical trading data with multiple time_frame
        '''
        pass
    