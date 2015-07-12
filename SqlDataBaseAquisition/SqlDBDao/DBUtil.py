'''
Created on 2015/06/12

@author: Daytona
'''

import mysql.connector

class DBUtil():
    '''
    return info for connection DB
    '''

    def __init__(self, String):
        '''
        Constructor
        '''
    def _get_UNSW_Daytona_Sql_Connection (self, DBName):
        if(DBName == "UNSW_Daytona") :
            cnx = mysql.connector.connect(user='PengJiang', password='jiangpengjun', host='149.171.37.73', database='sydneyexchange');
            return cnx