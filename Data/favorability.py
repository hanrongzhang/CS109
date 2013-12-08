import pandas as pd
import datetime

def time_input_handler(aggregated_data):
	df = pd.read_csv(aggregated_data)

	time_list = []
	for i in df.date:
		datetime_formatted = datetime.datetime.strptime(i, "%Y-%m-%d")
		time_list.append(datetime_formatted)

	df['datetime'] = time_list
	return df

def compute_favorability(aggregated_data, time):


compute_favorability("all_data_sentiment.csv", 1)