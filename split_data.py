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
total_frame = pd.read_csv("./all_data.csv", encoding = "UTF-8")
total_frame = total_frame.drop(['Unnamed: 0.1'],1)


def pres_filter(frame):
	total_frame = frame
	total_frame['candidate'] = ''
	romney_mask = ((total_frame.headline.str.contains("Romney")) & (~total_frame.headline.str.contains('Obama'))) | ((total_frame.abstract.str.contains("Romney")) & (~total_frame.abstract.str.contains("Obama")) & (~total_frame.headline.str.contains('Obama')))
	obama_mask = ((total_frame.headline.str.contains("Obama")) & (~total_frame.headline.str.contains('Romney'))) | ((total_frame.abstract.str.contains("Obama")) & (~total_frame.abstract.str.contains("Romney")) & (~total_frame.headline.str.contains('Romney')))
	total_frame.ix[romney_mask, 'candidate'] = "Romney"
	total_frame.ix[obama_mask, 'candidate'] = "Obama"
	return total_frame

total_frame = pres_filter(total_frame)
obama_frame = total_frame[total_frame['candidate'] == 'Obama']
romney_frame = total_frame[total_frame['candidate'] == 'Romney']
total_frame.to_csv("./all_data.csv", encoding = "UTF-8")
romney_frame.to_csv("./romney_data.csv", encoding = "UTF-8")
obama_frame.to_csv("./obama_data.csv", encoding = "UTF-8")
