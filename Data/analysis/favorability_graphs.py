import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import datetime

def plot_favorability(dataframe, avg_method, title, color='k', poll='no'):
	'''
	Given a dataframe and a method of generating favorability scores, plot 
	those scores over time. Optional argument color for matplotlib color 
	and whether polling data should be overlaid.
	'''

	df = pd.read_csv(dataframe)

	time_list =[]
	for i in df.date:
		datetime_formatted = datetime.datetime.strptime(i, "%Y-%m-%d")
		time_list.append(datetime_formatted)

	df['datetime'] = time_list

	x = df['datetime']
	y = df[avg_method]

	plt.title(title)
	plt.plot(x,y, color)
	plt.xlabel('Time')
	plt.xticks(fontsize = 'small', rotation = 45)

	plt.axhline(0, color='k', alpha=0.6, ls='--')

	plt.ylabel('Media Favorability')

	# if poll == True:


	plt.show()

plot_favorability('obama_analysis_v1.csv', 'running_pos_avg', 'Obama, Running Average', color = 'b')
plot_favorability('obama_analysis_v1.csv', 'geom_avg', 'Obama, Geometric average', color = 'b')

