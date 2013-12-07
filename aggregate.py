
#define needed date conversion functions
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
import brewer2mpl

def globe_date_convert(date):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    temp = date.split(' ')
    
    #convert month name to number
    month_num = 0
    
    month_count = 0
    for month in months:
        month_count = month_count + 1
        if temp[0] == month:
            month_num = month_count
            
    #get the day
    day_num = temp[1].replace(',','')
    date_result = datetime.date(int(temp[2]), int(month_num), int(day_num)) 
    return date_result

def guardian_date_convert(date):
    temp = date.split('T')
    date_result = datetime.datetime.strptime(temp[0], "%Y-%m-%d").date()
    return date_result

def nydn_date_convert(date):
    temp = date.split(' ')
    date_result = datetime.datetime.strptime(temp[0], "%Y-%m-%d").date()
    return date_result


#clean Chicago Tribune
chicago_frame = pd.read_csv("./Chicago_Tribune_Data/ChicagoTribune_romney_or_obama_newer.csv", encoding = "UTF-8")
chicago_frame['date'] = chicago_frame.date.apply(globe_date_convert)

#clean globe data
globe_frame = pd.read_csv("./Globe_Data/Globe_romney_or_obama.csv", encoding = "UTF-8")
globe_frame['date'] = globe_frame.date.apply(globe_date_convert)

#clean guardian data
guardian_frame = pd.read_csv("./Guardian_Data/Guardian_2012_election_full.csv", encoding = "UTF-8")
guardian_frame = guardian_frame.drop(['id','trailText','url'],1)

guardian_frame['date'] = guardian_frame.pub_date.apply(guardian_date_convert)
guardian_frame = guardian_frame.drop('pub_date',1)
guardian_frame.rename(columns={'standfirst': 'abstract', 'sectionName':'section'}, inplace=True)
guardian_frame['source'] = 'Guardian'

#clean LATimes data
latimes_frame = pd.read_csv("./LATimes_Data/LATimes_romney_or_obama_total.csv", encoding = "UTF-8")
latimes_frame['date'] = latimes_frame.date.apply(globe_date_convert)

#cleaning Newsday
newsday_frame = pd.read_csv("./Newsday_Data/newsday_romney_or_obama_newer.csv", encoding = "UTF-8")
newsday_frame['date'] = newsday_frame.date.apply(globe_date_convert)

#clean nydn data
nydn_frame = pd.read_csv("./NYDN_Data/NYDN_politics_2008_present.csv", encoding = "UTF-8")
nydn_frame = nydn_frame.drop(['body', 'byline','url'],1)
nydn_frame.rename(columns={'summary':'abstract','pub_date':'date'},inplace=True)

nydn_frame['date'] = nydn_frame.date.apply(nydn_date_convert)
nydn_frame = nydn_frame[nydn_frame['source'] == 'New York Daily News']

nydn_frame = nydn_frame[nydn_frame['date'] > datetime.date(2012,1,1)]
nydn_frame = nydn_frame[nydn_frame['date'] < datetime.date(2012,11,6)]

#clean NYT data
nyt_frame = pd.read_csv("./NYT_Data/election_2012_NYT.csv", encoding = "UTF-8")
nyt_frame['date'] = nyt_frame.pub_date.apply(guardian_date_convert)

#combine abstract and snippets
temp_list = []
for row in nyt_frame.iterrows():
    if pd.isnull(row[1][1]):
       temp_list = temp_list + [row[1][11]]
    else:
        temp_list = temp_list + [row[1][1] + ' ' + row[1][11]]
nyt_frame['abstract'] = temp_list

nyt_frame = nyt_frame.drop(['blog','pub_date','id', 'url','lead_paragraph','seo_headline','snippet'],1)
nyt_frame.rename(columns={'news_desk':'section'},inplace=True)

#cleaning PANewspapers
pa_frame = pd.read_csv("./PA_newspapers_Data/PA_romney_or_obama_newer.csv", encoding = "UTF-8")
pa_frame['date'] = pa_frame.date.apply(globe_date_convert)

#clean Washington Post data
wp_frame = pd.read_csv("./WashingtonPost_Data/WP_election_2012.csv", encoding = "UTF-8")
wp_frame['date'] = wp_frame.date.apply(globe_date_convert)

#clean USAToday
usa_t_frame = pd.read_csv("./USA_Today_data/USAToday_romney_or_obama.csv", encoding = "UTF-8")
usa_t_frame['date'] = usa_t_frame.date.apply(globe_date_convert)

#clean wsj data
wsj_frame = pd.read_csv("./WSJ_data/WSJ_obama_romney_newest.csv",encoding = "UTF-8")
wsj_frame['date'] = wsj_frame.date.apply(globe_date_convert)
wsj_frame.rename(columns={'snippet':'abstract'},inplace=True)
wsj_frame = wsj_frame[wsj_frame['date'] > datetime.date(2012,1,1)]
wsj_frame = wsj_frame[wsj_frame['date'] < datetime.date(2012,11,6)]

#combine dataframes
total_frame = globe_frame.append(guardian_frame,ignore_index=True)
total_frame = total_frame.append(chicago_frame,ignore_index=True)
total_frame = total_frame.append(usa_t_frame,ignore_index=True)
total_frame = total_frame.append(latimes_frame,ignore_index=True)
total_frame = total_frame.append(nydn_frame,ignore_index=True)
total_frame = total_frame.append(nyt_frame,ignore_index=True)
total_frame = total_frame.append(wp_frame,ignore_index=True)
total_frame = total_frame.append(newsday_frame,ignore_index=True)
total_frame = total_frame.append(pa_frame,ignore_index=True)
total_frame = total_frame.append(wsj_frame,ignore_index=True)
total_frame = total_frame.drop(['Unnamed: 0','keywords','subjects'],1)
total_frame['id'] = list(xrange(len(total_frame.index)))
total_frame['abstract'] = total_frame['abstract'].fillna('-')
total_frame.to_csv("./all_data.csv", encoding = "UTF-8")

