'''
Created on 4 Mar 2016

@author: purewin7
'''

import pandas as pd
import matplotlib.pyplot as plt

raw_year_data = pd.read_csv("./Data/2005-2016_v2.csv").dropna().reset_index(drop = True)
print len(raw_year_data)

# get highest and lowest, close price distribution in 2nd day

high = []
low = []
close = []
open = []
for i in range(len(raw_year_data)) :
    high.append(raw_year_data.loc[i][-239:].max())
    low.append(raw_year_data.loc[i][-239:].min())
    close.append(raw_year_data.loc[i][-1])
    open.append(raw_year_data.loc[i][-239])
    
plt.hist(high, range = (-0.2,0.26), bins=100, cumulative = False, normed=True, stacked=True,  histtype='step' )
plt.hist(close, range = (-0.2,0.26), bins=100, cumulative = False, normed=True, stacked=True,  histtype='step' )
plt.title("Highest return appearing in 2nd trading day.")
plt.show()
plt.hist(low, range = (-0.2,0.26), bins=100, cumulative = False, normed=True, stacked=True,  histtype='step' )
plt.hist(close, range = (-0.2,0.26), bins=100, cumulative = False, normed=True, stacked=True,  histtype='step' )
plt.title("Lowest return appearing in 2nd trading day.")
plt.show()
plt.hist(open, bins=50, cumulative = True, normed=True, stacked=True )
plt.title("open return appearing in 2nd trading day.")
plt.show()
plt.hist(close, bins=50, cumulative = True, normed=True, stacked=True )
plt.title("close return appearing in 2nd trading day.")
plt.show()
plt.scatter(high, low)
plt.xlabel("Highest return appearing in 2nd trading day.")
plt.ylabel("Lowest return appearing in 2nd trading day.")
plt.title("Highest vs lowest return appearing in 2nd trading day.")
plt.show()
plt.scatter(high, close)
plt.xlabel("Highest return appearing in 2nd trading day.")
plt.ylabel("Close return appearing in 2nd trading day.")
plt.title("Highest vs close return appearing in 2nd trading day.")
plt.show()
plt.scatter(high, open)
plt.xlabel("Highest return appearing in 2nd trading day.")
plt.ylabel("Open return appearing in 2nd trading day.")
plt.title("Highest vs close return appearing in 2nd trading day.")
plt.show()
plt.scatter(close, open)
plt.xlabel("Close return appearing in 2nd trading day.")
plt.ylabel("Open return appearing in 2nd trading day.")
plt.title("Open vs close return appearing in 2nd trading day.")
plt.show()



if __name__ == '__main__':
    pass