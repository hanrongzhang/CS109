    
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

#gets rcp polling average, returns df indexed by date
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


#runs analysis on a sentiment dataframe for a specified candidate
def pos_analysis(csv, candidate):
    sent_frame = pd.read_csv(csv, encoding='UTF-8')
    sent_frame['net_pos'] = sent_frame['pos'] -.5
    

    #creates stats based on the sentiment dataframe
    def aggregate(frame):

        #groups input frame by date
        dg = frame.groupby('date')

        #create stats
        pos_sums = dg.pos.sum()
        pos_means = dg.pos.mean()
        net_pos_sums = dg.net_pos.sum()


        #add stats to a new result df
        result = pd.DataFrame(pos_sums)
        result.columns = ['pos_sum']
        result['pos_mean'] = pos_means
        result['net_pos_sums'] = net_pos_sums
        return result


    #run aggregate on target candidate part of sentiment dataframe
    result = aggregate(sent_frame[sent_frame['candidate'] == candidate])

    #gets polls
    polls = get_poll(1171)

    #merges polls and sentiment-stats
    temp = polls[candidate]
    result['polls']=temp[temp.notnull()]
    result = result[result.polls.notnull()]

    # create running average
    running_average = []

    for index,(k, item) in enumerate(result.iterrows()):
        prev_sum = 0
        prev_count = 0

        for i in range(5):
            if (index-i) >= 0:
                prev_sum += result.iloc[index - i]['net_pos_sums']
                prev_count += 1
        run_avg = prev_sum / prev_count
        running_average.append(run_avg)

    result['running_pos_avg'] = running_average

    # create geometric weighted average
    geom_avg = []
    for index,(k, item) in enumerate(result.iterrows()):
        avg = 0

        for i in range(index+1):
            avg += (1 / ((float(index) - float(i) + 1) ** 2))* result.iloc[i]['net_pos_sums']

        geom_avg.append(avg)

    result['geom_avg'] = geom_avg

    return result


#run for obama and romney
obama_frame = pos_analysis('all_data_sentiment.csv', 'Obama')
romney_frame = pos_analysis('all_data_sentiment.csv', 'Romney')

#write to csv
romney_frame.to_csv("romney_analysis_v1.csv", encoding = "UTF-8")
obama_frame.to_csv("obama_analysis_v1.csv", encoding = "UTF-8")