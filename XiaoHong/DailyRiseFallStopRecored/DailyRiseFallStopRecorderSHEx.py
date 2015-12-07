'''
Created on 7 Dec 2015
This file is used to record the real time number of rise fall stop stocks by crawling data from http://stock.jrj.com.cn/tzzs/zdtwdj.shtml.
Result is written in a csv file

@author: daytona
'''

from urllib import urlopen
from bs4 import BeautifulSoup
import html5lib

import requests
import urllib2


if __name__ == '__main__':    
    # read in http://stock.jrj.com.cn/tzzs/zdtwdj.shtml
    #url = raw_input("http://stock.jrj.com.cn/tzzs/zdtwdj.shtml")

    url = "http://js.jrjimg.cn/stock/tzzs/zdtwdj/showChar.js?v=23456787894121"
    page= urllib2.urlopen(url).read()
    
    soup = BeautifulSoup(page, "html5lib")

    print soup

    # Separate time, number of rise stop, and number of fall stop from the html content
    
    # write to file
    
    
    pass