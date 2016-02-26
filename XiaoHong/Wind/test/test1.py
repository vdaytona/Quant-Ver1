'''
Test for connecting wind server
Created on 23 Feb 2016

@author: purewin7
'''

from WindPy import *

if __name__ == '__main__':
    try :
        w.start()
        data=w.wsd("600000.SH","close,amt", datetime.today()-timedelta(100))
        
        print data
        print data["Times"]
        print data["CLOSE"]    
    finally:
        w.stop()
    
    