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
    wp_pattern_good = re.compile(u'FMT=ABS')
    wp_pattern_bad = re.compile(u'washingtonpost_historical')
    
    # find each url
    for a in dom('table a'):
        # check if the a tag has a title, the title matches the Preview sring, and the href is not from the header faq section
        if ('title' in a.attrs) and (a.attrs['title'] == 'Preview&nbsp;(Abstract/Citation)') and (a.attrs['href'] != 'faq.html#abs'):
            # add url to url_list
            url_list += [str(a.attrs['href'])]

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
    PQarchive_full = pd.DataFrame(columns=['author','date', 'word_count','abstract','headline','source'])
    
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
            
            # add the abstract text to the article dict
            article['abstract'] = ''
            for p in dom('p'):
                if (re.search('<!-- begin main file: document -->', p.content) is None):
                    article['abstract'] += ' ' + plaintext(p.content)
        
            # go to each table row
            for td in dom('td'):
                if(re.search('\d+ words', td.content) is not None):
                    if debug: print td.content
                    try:
                        article['word_count'] = plaintext(td.content.split('The Wall Street Journal,')[1].split(' words')[0])
                    except:
                        print "Failed word count parse of: " + td.content
                        article['word_count'] = td.content
            
            # parse URL to find author and date
            try:
                article['date'] = plaintext(urlparse.parse_qs(urlparse.urlparse(url).query)['date'][0])
                article['author'] = plaintext(urlparse.parse_qs(urlparse.urlparse(url).query)['author'][0])
            except:
                print "Failed to except date or author for url: " + str(url)

            # append each article dict as a row to the full df, adding headline and source
            article['headline'] = dom('.docTitle')[0].content
            article['source'] = source
            PQarchive_full = PQarchive_full.append(article, ignore_index = True)
        
    return PQarchive_full

full_WSJ_df = PQarchive_scrape_archives('1-1-2011','9-30-2011', 'djreprints', 'The Wall Street Journal', debug = False).append(
    PQarchive_scrape_archives('9-30-2011','3-30-2012', 'djreprints', 'The Wall Street Journal', debug = False), ignore_index = True).append(
    PQarchive_scrape_archives('3-30-2012','7-30-2012', 'djreprints', 'The Wall Street Journal', debug = False), ignore_index = True).append(
    PQarchive_scrape_archives('7-30-2012','11-7-2012', 'djreprints', 'The Wall Street Journal', debug = False), ignore_index = True)
full_WSJ_df.to_csv("./WSJ_obama_romney.csv", encoding = "UTF-8")