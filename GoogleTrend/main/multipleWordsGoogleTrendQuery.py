'''
Created on 2015/09/12

@author: Daytona
'''

import pandas as df
import Google.GoogleTrends as py

def main():
    r = py.pyGTrends(username = "daytonaviola@gmail.com", password="Ding198573jie")
    for word in getSearchWords():
        r.download_report((word))
        #r.writer( "search_query_name.csv" )
        data = r.csv( section='Main',as_list= True)
        result = df.DataFrame(data)
        fileName = ('../Data/%s_google_trend.csv'%word)
        print ('%s finished' %word)
        result.to_csv(fileName, header = 1, columns= [0,1],index = False)

def getSearchWords():
    words = ['finance','sell','invest','fed','house','metals','travel','returns','gain',\
             'default','present','holiday','water','rich','risk','gold','success','oil','war','economy','DOW JONES','chance',\
             'short sell','lifestyle','greed','food','financial markets','movie','nyse','ore','BUY AND HOLD','opportunity','health',\
             'short selling','earnings','arts','culture','bubble','buy','trader','rare earths','tourism','politics','energy',\
             'consume','consumption','freedom','dividend','world','conflict','kitchen','forex','home','crash','transaction',\
             'garden','fond','train','labor','fun','environment','ring']
             
             #==================================================================
             # 'debt','color','stocks','restaurant','portfolio','inflation','housing','dow jones','revenue','economics',\
             # 'credit','markets','return','unemployment','money','religion','cancer','growth','investment','hedge','marriage',\
             # 'bonds','derivatives','headlines','profit','society','leverage','loss','cash','office','fine','stock market','banking',\
             # 'crisis','happy','car','nasdaq','
             #==================================================================
             
    return words

if __name__ == '__main__':
    main()