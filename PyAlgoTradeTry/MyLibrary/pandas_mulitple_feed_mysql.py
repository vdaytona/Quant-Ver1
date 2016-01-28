import datetime

from pyalgotrade import bar
from pyalgotrade.barfeed import membf
from pyalgotrade import dataseries
from pyalgotrade.barfeed import csvfeed

# Example BarFeed for dataframes with data for a single instrument.
class DataFrameMulitpleBarFeed(membf.BarFeed):
    # @dataframes : Dict [key = instrument, value = df]
    # @instruments : key of Dict
    def __init__(self, dataframes, frequency,  timezone=None, maxLen=dataseries.DEFAULT_MAX_LEN):
        if isinstance(timezone, int):
            raise Exception("timezone as an int parameter is not supported anymore. Please use a pytz timezone instead.")

        if frequency not in [bar.Frequency.DAY, bar.Frequency.WEEK]:
            raise Exception("Invalid frequency.")
        
        membf.BarFeed.__init__(self, frequency, maxLen)
        #csvfeed.BarFeed.__init__(self, frequency, maxLen)
        self.__dfs = dataframes
        self.__instruments = dataframes.keys()
        self.__timezone = timezone
        self.__sanitizeBars = False
        self.__barFilter = None
    
    
    def getBarFilter(self):
        return self.__barFilter

    def setBarFilter(self, barFilter):
        self.__barFilter = barFilter
        
    def sanitizeBars(self, sanitize):
        self.__sanitizeBars = sanitize
    
    def barsHaveAdjClose(self):
        return True
    
    def addMultipleBars(self, timezone=None):
        if isinstance(timezone, int):
            raise Exception("timezone as an int parameter is not supported anymore. Please use a pytz timezone instead.")

        if timezone is None:
            timezone = self.__timezone
            
        for instrument in self.__instruments:
            # add one bars series into BarFeed
            self.addBarsFromSequence(instrument, self.newBasicBar(self.__dfs[instrument]))
    
    # put df data quotes into bar.BasicBars sequence
    # bars : sequence of bar.BasicBars        
    def newBasicBar(self, df):
        bars = []
        for index in df.index :
            date = df["Date"][index]
            dateandtime = datetime.datetime(date.year, date.month, date.day)
            bars.append(bar.BasicBar(dateandtime,
                    df["Open"][index],
                    df["High"][index],
                    df["Low"][index],
                    df["Close"][index],
                    df["Volume"][index],
                    df["AdjClose"][index],
                    self.getFrequency()))
        return bars