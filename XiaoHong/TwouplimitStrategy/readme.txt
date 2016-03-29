sell_stop_limit_backtest_v6.py
different sell method :
	if D+1 open / D close > 1.04
		sell at open price D+1
	if D+1 open / D close < 1.04
		sell at close price D+1
	if D+1 open / D close >= 1.099
		uplimit condition:
		sell when uplimit is broken or keep onto D+2 and repeat