'''
Created on 8 Jan 2016

@author: purewin7
'''
import datetime
import pandas_feed_mysql
import connectMysqlDB
import mysql.connector

from pandas.io import data
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade import barfeed
from connectMysqlDBTest import workingSpace




class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed, 2000)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1] and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy(smaPeriod):
    
    host='149.171.37.73'
    userName='PengJiang'
    password='jiangpengjun'
    database='sydneyexchange'
    cnx = mysql.connector.connect();
    pandasResult = None
    try:
        #get cnx used for connecting DB
        cnx = connectMysqlDB.cnxStock(host=host,userName=userName,password=password,database=database).connect()
        
        #write anything you want to do in the workingSpace
        pandasResult = workingSpace(cnx)
        
    finally:
        cnx.close()
    #print pandasResult
    
    # Load the yahoo feed from the CSV file
    #feed = yahoofeed.Feed()
    #feed.addBarsFromCSV("orcl", "orcl-2000.csv")
    instrument = 'orcl'
    #df = data.DataReader(instrument, 'yahoo', datetime.datetime(2011,1,1), datetime.datetime(2012,1,1))
    
    feed = pandas_feed_mysql.DataFrameBarFeed(pandasResult, instrument, barfeed.Frequency.DAY)
    #print feed
    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "orcl", smaPeriod)
    myStrategy.run()
    print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()

run_strategy(15)