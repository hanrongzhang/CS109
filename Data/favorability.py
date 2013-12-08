import pandas as pd
import datetime

def time_input_handler(aggregated_data):
	# reads from CSV and returns a df with 'datetime' column filled with datetime objects into memory

	df = pd.read_csv(aggregated_data)

	time_list = []
	for i in df.date:
		datetime_formatted = datetime.datetime.strptime(i, "%Y-%m-%d")
		time_list.append(datetime_formatted)

	df['datetime'] = time_list
	return df

def compute_favorability(data_df, date, candidate):
	# returns favorability score for candidate on date

	df_prepped = data_df[data_df['datetime'] <= date]
	df_prepped = df_prepped[data_df['candidate'] == candidate]

	for index, item in df_prepped.iterrows():
		mod_factor = (date - item['datetime']).days
		print mod_factor

# tests
df = time_input_handler("all_data_sentiment.csv")
test_date =  datetime.datetime.strptime("2011-03-04", "%Y-%m-%d")

compute_favorability(df, test_date, 'Romney')