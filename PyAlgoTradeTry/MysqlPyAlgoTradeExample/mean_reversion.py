'''
Mean reversion strategy
ref to statarb_erniechan
https://github.com/jp1989326/pyalgotrade/blob/master/samples/statarb_erniechan.py
Created on 1 Feb 2016

@author: purewin7
'''

from pyalgotrade import strategy
from pyalgotrade import dataseries
from pyalgotrade.dataseries import aligned
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.stratanalyzer import sharpe
from statsmodels.tsa.stattools import adfuller
from MyLibrary import johansen

import numpy as np
import statsmodels.api as sm
import pandas as pd



#===============================================================================
# def get_beta(values1, values2):
#     # get beta value (shares of instrument in unit Portfolio) through Johansen Test
#     
#     
#     rarray=np.random.random(size=50)
#     model = sm.OLS(values1, values2, rarray)
#     results = model.fit()
#     return results.params[0]
#===============================================================================




class StatArbHelper:
    def __init__(self, inputDs, windowSize):
        # 1. aligning time
        self.__ds = self.multipleDatetimeAligned(inputDs)
        
        # 2. initial parameters
        self.__instrumentList = input.key()
        self.__windowSize = windowSize
        self.__hedgeRatio = None
        self.__spread = None
        self.__spreadMean = None
        self.__spreadStd = None
        self.__zScore = None
        
    def multipleDatetimeAligned(self, input):
        # in case of multiple dataseries, add multiple datatime aligned function
        # input : Dictionary(instrumentName : dataseries)
        alignedSeries = dict()
        instrumentList = input.key()
        k = 0;
        while k < 2:
            k += 1
            for i in range(1,len(instrumentList)) :
                alignedSeries[instrumentList[0]],alignedSeries[instrumentList[i]] = aligned.datetime_aligned(input[instrumentList[0]], input[instrumentList[i]])
        return alignedSeries
    
    def get_beta(self,inputDs):
        # doing johanson test and return 
        data = dict()
        for i in range(len(self.__instrumentList)) :
            data[self.__instrumentList[i]] = inputDs[self.__instrumentList[i]]["AdjClose"]
        jres = johansen.coint_johansen(data, 0, 1)
        result = dict()
        for i in range(len(self.__instrumentList)) :
            result[self.__instrumentList[i]] = jres.evec[i,0]
        return result
    
    
    
    
    
    def getSpread(self):
        return self.__spread

    def getSpreadMean(self):
        return self.__spreadMean

    def getSpreadStd(self):
        return self.__spreadStd

    def getZScore(self):
        return self.__zScore

    def getHedgeRatio(self):
        return self.__hedgeRatio

    #===========================================================================
    # def __updateHedgeRatio(self, values1, values2):
    #     self.__hedgeRatio = get_beta(values1, values2)
    #     
    #===========================================================================


    def __updateHedgeRatio(self,currentValues):
        self.__hedgeRatio = self.get_beta(currentValues)
        pass

    def __updateSpreadMeanAndStd(self, values1, values2):
        if self.__hedgeRatio is not None:
            spread = values1 - values2 * self.__hedgeRatio
            self.__spreadMean = spread.mean()
            self.__spreadStd = spread.std(ddof=1)

    #===========================================================================
    # def __updateSpread(self):
    #     if self.__hedgeRatio is not None:
    #         self.__spread = self.__ds1[-1] - self.__hedgeRatio * self.__ds2[-1]
    #===========================================================================
    def __updateSpread(self):
       if self.__hedgeRatio is not None:
           self.__spread = self.__
        pass

    def __updateZScore(self):
        if self.__spread is not None and self.__spreadMean is not None and self.__spreadStd is not None:
            self.__zScore = (self.__spread - self.__spreadMean) / float(self.__spreadStd)

    def update(self):
        # check if the bar has gone the length of windowSize, otherwise parameters can not be calculated
        if len(self.__ds[self.__instrumentList[0]]) >= self.windowSize :
            currentValues = dict()
            for i in range(len(self.__instrumentList)) :
                currentValues[self.__instrumentList[i]] = np.asarray(self.__ds[self.__instrumentList[i]][-1*self.__windowSize:])
            self.__updateHedgeRatio(currentValues)
            
            self.__updateSpread()
            pass
        
        # need to update hedgeratio (Johansen test), unit portofolio, position
        
        if len(self.__ds1) >= self.__windowSize:
            values1 = np.asarray(self.__ds1[-1*self.__windowSize:])
            values2 = np.asarray(self.__ds2[-1*self.__windowSize:])
            self.__updateHedgeRatio(values1, values2)
            self.__updateSpread()
            self.__updateSpreadMeanAndStd(values1, values2)
            self.__updateZScore()


class StatArb(strategy.BacktestingStrategy):
    def __init__(self, feed, instruments, windowSize, initialCash ):
        strategy.BacktestingStrategy.__init__(self, feed, initialCash)
        self.setUseAdjustedValues(True)
        self.__statArbHelper = StatArbHelper(feed, instruments, windowSize)
        self.__shareToBuy = {}
        # These are used only for plotting purposes.
        self.__spread = dataseries.SequenceDataSeries()
        self.__hedgeRatio = dataseries.SequenceDataSeries()
        self.__instruments = instruments
    
    
#===============================================================================
#     def __init__(self, feed, instrument1, instrument2, windowSize):
#         strategy.BacktestingStrategy.__init__(self, feed)
#         self.setUseAdjustedValues(True)
#         self.__statArbHelper = StatArbHelper(feed[instrument1].getAdjCloseDataSeries(), feed[instrument2].getAdjCloseDataSeries(), windowSize)
#         self.__i1 = instrument1
#         self.__i2 = instrument2
# 
#         # These are used only for plotting purposes.
#         self.__spread = dataseries.SequenceDataSeries()
#         self.__hedgeRatio = dataseries.SequenceDataSeries()
#===============================================================================

    def getSpreadDS(self):
        return self.__spread

    def getHedgeRatioDS(self):
        return self.__hedgeRatio
    
    def rebalancePortofolio(self, currentPortfolio, unitSize):
        # currentPortofolio "Dict" type : {[instrumentName : position], }
        for instrument in self.__instruments:
            newShare = currentPortfolio[instrument] * unitSize
            currentShare = self.getBroker().getShares(instrument)
            changeShare = newShare - currentShare
            self.__shareToBuy[instrument] = changeShare
    
    def placeOrders(self):
        # place orders to change position
        # have not considered remaining cash yet
        for instrument in self.__instruments : 
            if self.__shareToBuy[instrument] != 0:
                self.marketOrder(instrument, self.__shareToBuy[instrument])
            
    
    
    
        
    
    #===========================================================================
    #do not need change order size 
    #def __getOrderSize(self, bars, hedgeRatio):
    #     cash = self.getBroker().getCash(False)
    #     prices = []
    #     sizes = []
    #     for instrument in self.__instruments:
    #         price = bars[instrument].getAdjClose()            
    #         prices.append(price)
    #         sizes.append(int(cash / (price + hedgeRatio[instrument] * price2)))
    #===========================================================================
        

    def __getOrderSize(self, bars, hedgeRatio):
        cash = self.getBroker().getCash(False)
        price1 = bars[self.__i1].getAdjClose()
        price2 = bars[self.__i2].getAdjClose()
        size1 = int(cash / (price1 + hedgeRatio * price2))
        size2 = int(size1 * hedgeRatio)
        return (size1, size2)

    def buySpread(self, bars, hedgeRatio):
        amount1, amount2 = self.__getOrderSize(bars, hedgeRatio)
        self.marketOrder(self.__i1, amount1)
        self.marketOrder(self.__i2, amount2 * -1)

    def sellSpread(self, bars, hedgeRatio):
        amount1, amount2 = self.__getOrderSize(bars, hedgeRatio)
        self.marketOrder(self.__i1, amount1 * -1)
        self.marketOrder(self.__i2, amount2)

    def reducePosition(self, instrument):
        currentPos = self.getBroker().getShares(instrument)
        if currentPos > 0:
            self.marketOrder(instrument, currentPos * -1)
        elif currentPos < 0:
            self.marketOrder(instrument, currentPos * -1)

    def onBars(self, bars):
        # update hedgeratio, z-score
        self.__statArbHelper.update()

        # These is used only for plotting purposes.
        self.__spread.appendWithDateTime(bars.getDateTime(), self.__statArbHelper.getSpread())
        self.__hedgeRatio.appendWithDateTime(bars.getDateTime(), self.__statArbHelper.getHedgeRatio())
        
        # implement trading
        if bars.getBar(self.__i1) and bars.getBar(self.__i2):
            hedgeRatio = self.__statArbHelper.getHedgeRatio()
            zScore = self.__statArbHelper.getZScore()
            if zScore is not None:
                currentPos = abs(self.getBroker().getShares(self.__i1)) + abs(self.getBroker().getShares(self.__i2))
                if abs(zScore) <= 1 and currentPos != 0:
                    self.reducePosition(self.__i1)
                    self.reducePosition(self.__i2)
                elif zScore <= -2 and currentPos == 0:  # Buy spread when its value drops below 2 standard deviations.
                    self.buySpread(bars, hedgeRatio)
                elif zScore >= 2 and currentPos == 0:  # Short spread when its value rises above 2 standard deviations.
                    self.sellSpread(bars, hedgeRatio)


def main(plot):
    # 1. import data
    
    # 2. clean data, time aligned
    
    # 3. feed data
    
    # 4. strategy
    instruments = ["gld", "gdx"]
    windowSize = 50

    # Download the bars.
    feed = yahoofinance.build_feed(instruments, 2006, 2012, ".")

    strat = StatArb(feed, instruments[0], instruments[1], windowSize)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, False, False, True)
        plt.getOrCreateSubplot("hedge").addDataSeries("Hedge Ratio", strat.getHedgeRatioDS())
        plt.getOrCreateSubplot("spread").addDataSeries("Spread", strat.getSpreadDS())

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()


if __name__ == "__main__":
    main(True)