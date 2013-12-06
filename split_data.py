total_frame = pd.read_csv("./all_2012_data.csv", encoding = "UTF-8")
total_frame = total_frame.drop(['Unnamed: 0.1'],1)

romney_frame = total_frame[total_frame['abstract'].isnull()]
romney_frame = test[test['headline'].str.contains("Romney")]
temp_frame = total_frame[total_frame['abstract'].notnull()]
temp_frame = temp_frame[temp_frame['abstract'].str.contains("Romney")]
romney_frame = romney_frame.append(temp_frame, ignore_index=True)

obama_frame = total_frame[total_frame['abstract'].isnull()]
obama_frame = test[test['headline'].str.contains("Obama")]
obama_frame = total_frame[total_frame['abstract'].notnull()]
obama_frame = temp_frame[temp_frame['abstract'].str.contains("Obama")]
obama_frame = obama_frame.append(temp_frame, ignore_index=True)

print obama_frame
