# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 14:31:18 2018

@author: Koch
"""

import pandas as pd


stops = pd.read_csv('C:\\Users\\Gabriel\\Documents\\GitHub\\Database\\TransUrb\\stops.txt')
stops = stops.drop(columns=['stop_id','stop_desc'])