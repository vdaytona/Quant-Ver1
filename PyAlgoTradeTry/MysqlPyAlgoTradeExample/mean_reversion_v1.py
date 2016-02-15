'''
Mean reversion strategy_1
ref to statarb_erniechan
change the statarb_erniechan into mulitple instruments
https://github.com/jp1989326/pyalgotrade/blob/master/samples/statarb_erniechan.py
Created on 1 Feb 2016

@author: purewin7
'''

from pyalgotrade import strategy
from pyalgotrade import dataseries
from pyalgotrade.dataseries import aligned
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import sharpe
from MyLibrary import johansen
from pandas import DataFrame as df
from MyLibrary.connectMysqlDB import cnxStock
from MyLibrary.mysqlQuery import historicalPriceQuery
from MyLibrary.pandas_mulitple_feed_mysql import DataFrameMulitpleBarFeed
from pyalgotrade import barfeed

import numpy as np


class StatArbHelper:
    def __init__(self, feed, instrumentList,windowSize):
        # 1. initial parameters
        self.__instrumentList = instrumentList
        self.__windowSize = windowSize
        self.__hedgeRatio = dict()
        self.__spread = None
        self.__spreadMean = None
        self.__spreadStd = None
        self.__zScore = None
        self.__unitPortfolioCost = None
        
        # 2. aligning time
        self.__ds = self.multipleDatetimeAligned(feed)
        
    def multipleDatetimeAligned(self, feed):
        # in case of multiple dataseries, add multiple datatime aligned function
        ds = dict()
        ds[self.__instrumentList[0]] = feed[self.__instrumentList[0]].getAdjCloseDataSeries()
        for i in range(1,len(self.__instrumentList)) :
            ds[self.__instrumentList[0]], ds[self.__instrumentList[i]] = \
                aligned.datetime_aligned(ds[self.__instrumentList[0]], feed[self.__instrumentList[i]].getAdjCloseDataSeries())
        for i in range(1,len(self.__instrumentList)) :
            ds[self.__instrumentList[0]], ds[self.__instrumentList[i]] = \
                aligned.datetime_aligned(ds[self.__instrumentList[0]], ds[self.__instrumentList[i]])
        return ds
    
    def get_beta(self):
        # doing johanson test and return 
        data = df()
        for i in range(len(self.__instrumentList)) :
            data[self.__instrumentList[i]] = np.asarray(self.__ds[self.__instrumentList[i]][-1*self.__windowSize:])
        jres = johansen.coint_johansen(data[self.__instrumentList], 0, 1)
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
    
    def getUnitPortfolioCost(self):
        return self.__unitPortfolioCost

    def __updateHedgeRatio(self,currentValues):
        # normalized the beta, make the minimum beta to 1
        beta = self.get_beta()
        minBeta = min(map(abs, beta.values()))
        for instrument in self.__instrumentList :
            self.__hedgeRatio[instrument] = beta[instrument] / minBeta

    def __updateSpreadMeanAndStd(self, currentValues):
        if self.__hedgeRatio is not None :
            spread = 0.0
            for instrument in self.__instrumentList:
                spread += currentValues[instrument] * self.__hedgeRatio[instrument]
            self.__spreadMean = spread.mean()
            self.__spreadStd = spread.std(ddof=1)

    def __updateSpread(self):
        if self.__hedgeRatio is not None:
            self.__spread =  0.0
            for instrument in self.__instrumentList:
                self.__spread += self.__ds[instrument][-1] * self.__hedgeRatio[instrument]

    def __updateZScore(self):
        if self.__spread is not None and self.__spreadMean is not None and self.__spreadStd is not None:
            self.__zScore = (self.__spread - self.__spreadMean) / float(self.__spreadStd)
    
    def __updateUnitPortfolioCost(self):
        if self.__hedgeRatio is not None:
            self.__unitPortfolioCost = 0.0
            for instrument in self.__instrumentList :
                self.__unitPortfolioCost += self.__ds[instrument][-1] * abs(self.__hedgeRatio[instrument])

    def update(self):
        # check if the bar has gone the length of windowSize, otherwise parameters can not be calculated
        if len(self.__ds[self.__instrumentList[0]]) >= self.__windowSize :
            currentValues = dict()
            for instrument in self.__instrumentList :
                currentValues[instrument] = np.asarray(self.__ds[instrument][-1*self.__windowSize:])
            self.__updateHedgeRatio(currentValues)
            self.__updateSpread()
            self.__updateSpreadMeanAndStd(currentValues)
            self.__updateZScore()
            self.__updateUnitPortfolioCost()

class StatArb(strategy.BacktestingStrategy):
    def __init__(self, feed, inputDs, windowSize, initialCash ):
        strategy.BacktestingStrategy.__init__(self, feed, initialCash)
        self.setUseAdjustedValues(True)
        
        self.__instrumentList = inputDs.keys()
        self.__shareToBuy = dict()
        self.__statArbHelper = StatArbHelper(feed, self.__instrumentList, windowSize)
        
        # These are used only for plotting purposes.
        self.__spread = dataseries.SequenceDataSeries()
        self.__zScore = dataseries.SequenceDataSeries()

    def getSpreadDS(self):
        return self.__spread

    def getZScoreDS(self):
        return self.__zScore
    
    def rebalancePortofolio(self, currentPortfolio, unitSize):
        # currentPortofolio "Dict" type : {[instrumentName : position], }
        for instrument in self.__instruments:
            newShare = currentPortfolio[instrument] * unitSize
            currentShare = self.getBroker().getShares(instrument)
            changeShare = newShare - currentShare
            self.__shareToBuy[instrument] = changeShare

    def __getOrderSize(self, bars, hedgeRatio):
        cash = self.getBroker().getCash(False)
        oneOrderCost = self.__statArbHelper.getUnitPortfolioCost()
        orderSize = int(cash / oneOrderCost)
        for instrument in self.__instrumentList:
            self.__shareToBuy[instrument] = int(orderSize * self.__statArbHelper.getHedgeRatio()[instrument])
        return self.__shareToBuy
    
    def buySpread(self, bars, hedgeRatio):
        orderSize = self.__getOrderSize(bars, hedgeRatio)
        for instrument in self.__instrumentList :
            self.marketOrder(instrument, orderSize[instrument])
            
    def sellSpread(self, bars, hedgeRatio):
        orderSize = self.__getOrderSize(bars, hedgeRatio)
        for instrument in self.__instrumentList :
            self.marketOrder(instrument, orderSize[instrument] * -1)
    
    def closePosition(self):
        # if abs(ZScore) <= 1 , close Position
        for instrument in self.__instrumentList :
            currentPos = self.getBroker().getShares(instrument)
            # close Position (is there other way specific for closing position)
            self.marketOrder(instrument, currentPos * -1)
    
    def checkIfHaveNextBars(self, bars):
        # check if there are still bars left for all the instruments
        result = True
        for instrument in self.__instrumentList :
            if not bars.getBar(instrument) :
                result = None
        return result
    
    def getCurrentPos(self):
        # get Current Pos
        currentPos = 0.0
        for instrument in self.__instrumentList :
            currentPos += abs(self.getBroker().getShares(instrument))
        return currentPos

    def onBars(self, bars):
        # update hedgeratio, z-score
        self.__statArbHelper.update()

        # These is used only for plotting purposes.
        self.__spread.appendWithDateTime(bars.getDateTime(), self.__statArbHelper.getSpread())
        self.__zScore.appendWithDateTime(bars.getDateTime(), self.__statArbHelper.getZScore())
        
        # implement trading
        if self.checkIfHaveNextBars(bars) :
            hedgeRatio = self.__statArbHelper.getHedgeRatio()
            zScore = self.__statArbHelper.getZScore()
            if zScore is not None :
                currentPos = self.getCurrentPos()
                if abs(zScore) <= 1 and currentPos != 0:
                    self.closePosition()
                elif zScore <= -2 and currentPos == 0:  # Buy spread when its value drops below 2 standard deviations.
                    self.buySpread(bars, hedgeRatio)
                elif zScore >= 2 and currentPos == 0:  # Short spread when its value rises above 2 standard deviations.
                    self.sellSpread(bars, hedgeRatio)


def main(plot):
    
    # trail
    initialCash = 10000
    instruments = ["aapl", "ibm"]
    windowSize = 50
    tableNames = dict()
    for instrument  in instruments :
        tableName = str("newyorkexchange.%s_historicalquotes_newyork" %instrument)
        tableNames[instrument] = tableName
        
    try :
        # create instance to connect Mysql
        cnx = cnxStock()
        # create instance to query Mysql data base
        query = historicalPriceQuery(instruments, tableNames)
        dfs = query.pandasQueryMulitple(cnx.connect())
        #close connection
    finally:
        cnx.close_connection()
    
    feed = DataFrameMulitpleBarFeed(dfs,barfeed.Frequency.DAY)
    feed.addMultipleBars()
    strat = StatArb(feed,dfs, windowSize, initialCash)
    
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, False, False, True)
        plt.getOrCreateSubplot("zScore").addDataSeries("zScore", strat.getZScoreDS())
        plt.getOrCreateSubplot("spread").addDataSeries("Spread", strat.getSpreadDS())

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()


if __name__ == "__main__":
    main(True)