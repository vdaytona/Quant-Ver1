'''
Created on 13 Jan 2016
an example to show feeding the bar using data from mysql
@author: purewin7
'''

import sma_crossover
import MyLibrary.pandas_feed_mysql

from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import sharpe
from MyLibrary.connectMysqlDB import cnxStock
from MyLibrary.mysqlQuery import historicalPriceQuery
from pyalgotrade import barfeed

def main(plot):
    
    # instruments and talbename in sql
    instrument = "ibm"
    tableName = "newyorkexchange.ibm_historicalquotes_newyork"
    
    # create instance to connect Mysql
    cnx = cnxStock()
    # create instance to query Mysql data base
    query = historicalPriceQuery(instrument, tableName)    
    df = query.pandasQuerySingle(cnx.connect())
    #close connection
    cnx.close_connection()
    
    # feed data from PyAlgoTrade back testing
    feed = MyLibrary.pandas_feed_mysql.DataFrameBarFeed(df, instrument, barfeed.Frequency.DAY)
    
    smaPeriod = 163
    strat = sma_crossover.SMACrossOver(feed, instrument, smaPeriod)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, False, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("sma", strat.getSMA())

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()

if __name__ == "__main__":
    main(True)