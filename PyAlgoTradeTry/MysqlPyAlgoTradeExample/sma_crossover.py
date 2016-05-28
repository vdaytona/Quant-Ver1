'''
Created on 13 Jan 2016
http://gbeced.github.io/pyalgotrade/docs/v0.17/html/sample_sma_crossover.html
@author: purewin7
'''
from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross


class SMACrossOver(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.__share = None
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__sma = ma.SMA(self.__prices, smaPeriod)
        for i in  self.__sma.getDataSeries():
            print i 

    def getSMA(self):
        return self.__sma

    def onEnterCanceled(self, position):
        self.__share = None

    def onExitOk(self, position):
        self.__share = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__share.exitMarket()

    def onBars(self, bars):
        if len(self.getActivePositions()) > 0 :
            print self.getActivePositions()
        print self.getLastPrice(self.__instrument)
        print self.getFeed()
        print self.getBarsProcessedEvent()
        
        # If a position was not opened, check if we should enter a long position.
        if self.__share is None:
            if cross.cross_above(self.__prices, self.__sma) > 0:
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                # Enter a buy market order. The order is good till canceled.
                self.__share = self.enterLong(self.__instrument, shares, True)
        # Check if we have to exit the position.
        elif not self.__share.exitActive() and cross.cross_below(self.__prices, self.__sma) > 0:
            self.__share.exitMarket()