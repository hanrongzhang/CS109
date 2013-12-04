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

# Boston Globe -- Scraping

def Globe_url_list(start_date, end_date, page):
    '''
    Scrapes the Boston Globe archives to get a list of all URLs.
    
    Inputs: M(M)-D(D)-YYYY of start and end date, page number (1-indexed)
    Output: URL List
    '''

    # split dates into M, D, Y
    start_date = start_date.split('-')
    end_date = end_date.split('-')
    
    options = {}
    
    # run the query
    url = 'http://pqasb.pqarchiver.com/boston/results.html'
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
    options['QryTxt'] = 'romney OR obama'
    
    # try to get url with specified parameters
    try:
        html = requests.get(url, params=options).text
    except:
        print 'Unable to parse URL list for ' + str(url)
        return None
    
    # declare dom object to begin parsing the data
    dom = web.Element(html)
    
    url_list = []
    
    # find each url
    for a in dom('table a'):
        # check if the a tag has a title, the title matches the Preview sring, and the href is not from the header faq section
        if (('title' in a.attrs) and (a.attrs['title'] == 'Preview&nbsp;(Abstract/Citation)') 
            and (a.attrs['href'] != 'faq.html#abs')):
            # add url to url_list
            url_list += [str(a.attrs['href'])]

    return url_list


def Globe_scrape_archives(start_date, end_date):

    '''
    Scrape all articles, headlines, and descriptions from the Boston Globe Archives
    
    Inputs: begin_date, end_date in YYYY-M(M)-D(D) format (use datetime.datetime(year, month, day))
    Output: DataFrame with all inputs appended
    '''
    
    url_list = []
    
    # start page counter at 1
    i = 1
    
    # scrape first page of results
    new_url_list = Globe_url_list(start_date, end_date, i)
    
    # keep scraping until we run out of pages
    while new_url_list:
    
        # add 10 new urls to url_list
        url_list += new_url_list
        
        #Move to next page and scrape it
        i += 1
        new_url_list = Globe_url_list(start_date, end_date, i)
    
    # create DataFrame
    Globe_full = pd.DataFrame(columns=['author','date','section','word_count','abstract','headline','source'])
    
    url_count = 0
    
    print "This query will run for "  + str(len(list(set(url_list))))
    
    # loop through complete url list
    for url in list(set(url_list)):

        url_count += 1
        if url_count % 100 == 0:
            print url_count
        
        # get html from each url
        try:
            html = requests.get('http://pqasb.pqarchiver.com' + url).text
        except:
            continue
    
        # declare dom object to begin parsing the data
        dom = web.Element(html)

        prev_content = ''
        article = {}
        
        # don't scrape if no abstract
        if dom('p'):
            
            # find paragraph with abstract
            for p in dom('p'):
            
                # add the abstract text to the article dict
                article['abstract'] = ''
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
                
                # update prev_content for the next loop
                prev_content = td.content
            
            # append each article dict as a row to the full df, adding headline and source
            article['headline'] = dom('div.docTitle')[0].content
            article['source'] = 'Boston Globe'
            Globe_full = Globe_full.append(article, ignore_index = True)
        
    return Globe_full

full_Globe_df = Globe_scrape_archives('1-1-2011','11-6-2012')
full_Globe_df.to_csv("./Globe_election_2012.csv", encoding = "UTF-8")