'''
Created on 2015/08/07

@author: Daytona
'''

def TDI(close_price,RSI_period=13, RSI_price='mode_close', Volatility_Band=34, RSI_price_line=2, RSI_price_type='Mode_sma', Trade_signal_line=7, Trade_signal_type='mode_sma', Use_alerts=False):
    '''
    Traders Dynamic Index (http://www.earnforex.com/metatrader-indicators/Traders-Dynamic-Index):
    a comprehensive but helpful indicator that uses RSI and moving averages along with some on-the-fly volatility calculations to 
    offer the trader a full picture of the current Forex market situation. This indicator can use sound alerts
    RSI_Period (default = 13) — period in bars for calculation of RSI.
    RSI_Price (default = MODE_CLOSE) — price type to use in RSI calculation.
    Volatility_Band (default = 34) — parameter for volatility band calculation. Can be between 20 and 40. The lower this value is the curvier becomes the band.
    RSI_Price_Line (default = 2) — period of the first moving average (fast).
    RSI_Price_Type (default = MODE_SMA) — type of the first moving average.
    Trade_Signal_Line (default = 7) — period of the second moving average (slow).
    Trade_Signal_Type (default = MODE_SMA) — type of the second moving average.
    UseAlerts (default = false) — if true then sound alert will be played each time red and yellow lines cross.
    '''
    
    pass

def RSI(close_price = None,RSI_period=13, RSI_price='mode_close',RSI_price_line=2, RSI_price_type='mode_sma'):
    '''
    RELATIVE STRENGTH INDEX - RSI (http://www.investopedia.com/terms/r/rsi.asp):
    A technical momentum indicator that compares the magnitude of recent gains to recent losses in an attempt to determine 
    overbought and oversold conditions of an asset.
    It is calculated using the following formula:
    RSI = 100 - 100/(1 + RS*)
    Where RS = Average of x days gain / Average of x days loss
    '''
    if close_price == None :
        print 'No close price data'
        return None
    elif len(close_price) != RSI_period:
        print'Not enough data for calculation period'
        return None
    
    average_gain = 0.0
    average_loss = 0.0
    for i in range(1,RSI_period) :
        if (close_price[i] > close_price[i-1]) :
            average_gain += abs(close_price[i] - close_price[i-1])
        elif(close_price[i] < close_price[i-1]) :
            average_loss += abs(close_price[i] - close_price[i-1])
    average_gain = average_gain / float(RSI_period)
    if(average_loss == 0) :
        average_loss = 0.01
    else :
        average_loss = average_loss / float(RSI_period)
    
    return 100.0 - 100.0 / (1.0 + average_gain / average_loss)

def sma(close_price, sma_period):
    pass
