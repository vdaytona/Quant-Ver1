'''
Created on 21 Jan 2016

@author: purewin7
'''
from distutils.core import setup
import py2exe

setup(console=['DailyLimitUpLimitDownMonitorSHEx_ver1.py'],
          options = {
           "py2exe":{"dll_excludes":["MSVCP90.dll"]}})