import datetime

from pandas.io import data

from pyalgotrade import strategy
from pyalgotrade import barfeed
from pyalgotrade import bar


# Example BarFeed for dataframes with data for a single instrument.
class DataFrameBarFeed(barfeed.BaseBarFeed):
    def __init__(self, dataframe, instrument, frequency):
        super(DataFrameBarFeed, self).__init__(frequency)
        self.registerInstrument(instrument)
        self.__df = dataframe
        self.__instrument = instrument
        self.__next = 0

    def reset(self):
        super(DataFrameBarFeed, self).reset()
        self.__next = 0

    def peekDateTime(self):
        return self.getCurrentDateTime()

    def getCurrentDateTime(self):
        ret = None
        if not self.eof():
            date = self.__df["Date"].values[self.__df.index[self.__next]]
            #print type(datetime.datetime(date.year, date.month, date.day))
            ret = datetime.datetime(date.year, date.month, date.day)
        return ret

    def barsHaveAdjClose(self):
        return True
    
    def getNextBars(self):
        ret = None
        if not self.eof():
            # Convert the dataframe row into a bar.BasicBar
            rowkey = self.__df.index[self.__next]
            row = self.__df.ix[rowkey]
            date = row["Date"]
            dateandtime = datetime.datetime(date.year, date.month, date.day)
            bar_dict = {
                self.__instrument: bar.BasicBar(
                    dateandtime,
                    row["Open"],
                    row["High"],
                    row["Low"],
                    row["Close"],
                    row["Volume"],
                    row["AdjClose"],
                    self.getFrequency()
                )
            }
            ret = bar.Bars(bar_dict)
            self.__next += 1
        return ret


    def eof(self):
        return self.__next >= len(self.__df.index)

    def start(self):
        pass

    def stop(self):
        pass

    def join(self):
        pass

class MyStrategy(strategy.BacktestingStrategy):
    def onBars(self, bars):
        for instrument in bars.getInstruments():
            bar = bars[instrument]
            self.info("%s: %s %s %s %s %s %s" % (
                instrument,
                bar.getOpen(),
                bar.getHigh(),
                bar.getLow(),
                bar.getClose(),
                bar.getAdjClose(),
                bar.getVolume(),
            ))


def main():
    instrument = 'orcl'
    df = data.DataReader(instrument, 'yahoo', datetime.datetime(2011,1,1), datetime.datetime(2012,1,1))
    print df
    feed = DataFrameBarFeed(df, instrument, barfeed.Frequency.DAY)
    myStrategy = MyStrategy(feed)
    myStrategy.run()


if __name__ == "__main__":
    main()