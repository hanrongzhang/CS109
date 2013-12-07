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
import urlparse

# LA Times Scraper is basically the same as Boston Globe -- generalized to PQ archive
def PQarchive_url_list(start_date, end_date, page, newspaper_tag = 'latimes', query = 'romney OR obama', debug = False):
    '''
    Scrapes the PQ archive system to get a list of all URLs.
    
    Inputs: M(M)-D(D)-YYYY of start and end date, page number (1-indexed)
    Output: URL List
    '''

    # split dates into M, D, Y
    start_date = start_date.split('-')
    end_date = end_date.split('-')
    
    options = {}
    
    # run the query
    url = 'http://pqasb.pqarchiver.com/' + newspaper_tag + '/results.html'
    options['st'] = 'advanced'
    options['sortby'] = 'CHRON'
    options['datetype'] = 6
    options['frommonth'] = start_date[0]
    options['fromday'] = start_date[1]
    options['fromyear'] = start_date[2]
    options['tomonth'] = end_date[0]
    options['today'] = end_date[1]
    options['toyear'] = end_date[2]
    options['type'] = 'current'
    options['start'] = (page-1)*10
    options['QryTxt'] = query
    
    # try to get url with specified parameters
    try:
        r = requests.get(url, params=options)
        html = r.text
        if debug: print r.url
    except:
        print 'Unable to parse URL list for ' + str(url)
        return None
    
    # declare dom object to begin parsing the data
    dom = web.Element(html)
    
    url_list = []
    
    # find each url
    for a in dom('.result_title a'):
        url_list.append(str(a.attrs['href']))

    return url_list

def PQarchive_scrape_archives(start_date, end_date, newspaper_tag = 'latimes', source = 'LA Times', 
                              query = 'romney OR obama', debug = False):

    '''
    Scrape all articles, headlines, and descriptions from the PQarchive system
    
    Inputs: begin_date, end_date in YYYY-M(M)-D(D) format (use datetime.datetime(year, month, day))
    Output: DataFrame with all inputs appended
    '''
    
    url_list = []
    
    # start page counter at 1
    i = 1
    
    # scrape first page of results
    new_url_list = PQarchive_url_list(start_date, end_date, i, newspaper_tag,  query, debug)
    
    # keep scraping until we run out of pages
    while new_url_list:
    
        # add 10 new urls to url_list
        url_list += new_url_list
        
        # Move to next page and scrape it
        i += 1
        new_url_list = PQarchive_url_list(start_date, end_date, i, newspaper_tag, query, debug)
    
    # create DataFrame
    PQarchive_full = pd.DataFrame(columns=['author','date','section','word_count','abstract','headline','source', 'subjects'])
    
    url_count = 0
    
    print "This query will run for "  + str(len(list(set(url_list))))
    
    if debug: print list(set(url_list))
    
    # loop through complete url list
    for url in list(set(url_list)):

        url_count += 1
        if url_count % 100 == 0:
            print url_count
        
        # get html from each url
        try:
            html = requests.get('http://pqasb.pqarchiver.com' + url).text
        except:
            print "Could not retrieve html for page " + str(url)
            continue
    
        # declare dom object to begin parsing the data
        dom = web.Element(html)

        prev_content = ''
        article = {}
        
        # don't scrape if no abstract
        if dom('p'):
            
            article['abstract'] = ''
            # add the abstract text to the article dict
            for p in dom('p'):
                if (p.content != '<a href="http://www.latimes.com/terms">Terms of Service</a> | <a href="http://www.latimes.com/privacypolicy">Privacy Policy</a> | Los Angeles Times, 202 West 1st Street, Los Angeles, California, 90012 | Copyright 2011'):
                    article['abstract'] += ' ' + plaintext(p.content)
        
            # go to each table row
            for td in dom('td'):
           
                # since we're going in order of td's, 'Author:' will come right before the author's name, and so on
                if prev_content == 'Author:':
                    article['author'] = td.content
                elif prev_content == 'Date:':
                    article['date'] = td.content
                elif prev_content == 'Section:':
                    article['section'] = td.content
                elif prev_content == 'Text Word Count:':
                    article['word_count'] = td.content
                elif prev_content == 'Subjects:':
                    article['subjects'] = plaintext(td.content)
                
                # update prev_content for the next loop
                prev_content = td.content
            
            # append each article dict as a row to the full df, adding headline and source
            for headline in dom('.docTitle'):
                article['headline'] = headline.content
            if debug: print urlparse.parse_qs(urlparse.urlparse(url).query)
            article['source'] = urlparse.parse_qs(urlparse.urlparse(url).query)['pub'][0]
            PQarchive_full = PQarchive_full.append(article, ignore_index = True)
        
    return PQarchive_full

# Scraping USA Today
full_LAtimes_df = PQarchive_scrape_archives('1-1-2011','11-30-2011', 'latimes', 'LA Times', 
                                             query = 'romney OR obama', debug = False)
full_LAtimes_df.to_csv("./LATimes_romney_or_obama_through_nov11.csv", encoding = "UTF-8")

full_LAtimes_df = PQarchive_scrape_archives('11-30-2011','6-30-2012', 'latimes', 'LA Times', 
                                             query = 'romney OR obama', debug = False)
full_LAtimes_df.to_csv("./LATimes_romney_or_obama_throughjun12.csv", encoding = "UTF-8")

full_LAtimes_df = PQarchive_scrape_archives('6-30-2012','11-7-2012', 'latimes', 'LA Times', 
                                             query = 'romney OR obama', debug = False)
full_LAtimes_df.to_csv("./LATimes_romney_or_obama_throughnov12.csv", encoding = "UTF-8")