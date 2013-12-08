    
from collections import defaultdict
import json
import requests
import warnings
from pattern import web
from pattern.web import plaintext

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pprint
import datetime as datetime
from datetime import date, timedelta as td
import string
import re

from matplotlib import rcParams
import matplotlib.cm as cm
import matplotlib as mpl

import random
import math
from scipy import stats

def nydn_date_convert(date):
    temp = date.split(' ')
    date_result = datetime.datetime.strptime(temp[0], "%Y-%m-%d").date()
    return date_result

def polling_date_convert(date):
    date_result = datetime.datetime.strptime(date, "%d/%m/%Y").date()
    return date_result

def get_poll(id): 
    url = "http://charts.realclearpolitics.com/charts/%i.xml" % int(id)
    xml = requests.get(url).text
    dom = web.Element(xml)
    result = {}
    
    dates = dom.by_tag('series')[0]



    temp = []
    temp_dates = []
    for n in dates.by_tag('value'):
        temp = temp + [str(n.content)]
    for t in temp:
        split = t.split('/')
        d = datetime.date(int(split[2]), int(split[0]), int(split[1]))
        temp_dates = temp_dates + [unicode(d)]
    dates = temp_dates

    for graph in dom.by_tag('graph'):
        name = graph.attributes['title']
        poll_data = []
        for n in graph.by_tag('value'):
            if n.content:
                poll_data = poll_data + [float(n.content)]
            else: 
                poll_data = poll_data + [np.nan]
        result[name] = poll_data


    frame = pd.DataFrame(result, index=dates)
    frame.index.name = 'date'
    return frame


def pos_analysis(csv, candidate):
    sent_frame = pd.read_csv(csv, encoding='UTF-8')
    sent_frame['net_pos'] = sent_frame['pos'] -.5
    

    def aggregate(frame):
        dg = frame.groupby('date')
        pos_sums = dg.pos.sum()
        pos_means = dg.pos.mean()
        net_pos_sums = dg.net_pos.sum()
        result = pd.DataFrame(pos_sums)
        result.columns = ['pos_sum']
        result['pos_mean'] = pos_means
        result['net_pos_sums'] = net_pos_sums
        return result


    result = aggregate(sent_frame[sent_frame['candidate'] == candidate])
    polls = get_poll(1171)

    temp = polls[candidate]
    result['polls']=temp[temp.notnull()]
    result = result[result.polls.notnull()]

    return result


romney_frame = pos_analysis('./Data/all_data_sentiment.csv', 'Romney')
obama_frame = pos_analysis('./Data/all_data_sentiment.csv', 'Obama')

romney_frame.to_csv("./Data/romney_analysis_v1.csv", encoding = "UTF-8")
obama_frame.to_csv("./Data/obama_analysis_v1.csv", encoding = "UTF-8")



