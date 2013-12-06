
#define needed date conversion functions
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




#clean globe data
globe_frame = pd.read_csv("./Globe_Data/Globe_election_2012.csv", encoding = "UTF-8")
globe_frame = globe_frame.drop(['section'], 1)
globe_frame['date'] = globe_frame.date.apply(globe_date_convert)



#clean guardian data
guardian_frame = pd.read_csv("./Guardian_Data/Guardian_2012_election_full.csv", encoding = "UTF-8")
guardian_frame = guardian_frame.drop(['id','sectionName','trailText','url'],1)

guardian_frame['date'] = guardian_frame.pub_date.apply(guardian_date_convert)
guardian_frame = guardian_frame.drop('pub_date',1)
guardian_frame.rename(columns={'standfirst': 'abstract'}, inplace=True)
guardian_frame['source'] = 'Guardian'

#clean LATimes data
latimes_frame = pd.read_csv("./LATimes_Data/LATimes_election_2012.csv", encoding = "UTF-8")
latimes_frame = latimes_frame.drop(['section'],1)
latimes_frame['date'] = latimes_frame.date.apply(globe_date_convert)

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

nyt_frame = nyt_frame.drop(['blog','pub_date','id','news_desk', 'word_count', 'url','lead_paragraph','seo_headline','snippet'],1)

#clean Washington Post data
wp_frame = pd.read_csv("./WashingtonPost_Data/WP_election_2012.csv", encoding = "UTF-8")
wp_frame = wp_frame.drop(['section'],1)
wp_frame['date'] = wp_frame.date.apply(globe_date_convert)

#clean wsj data
wsj_frame = pd.read_csv("./WSJ_data/WSJ_subset_2012.csv", encoding = "UTF-8")
wsj_frame['date'] = wsj_frame.pub_date.apply(nydn_date_convert)
wsj_frame = wsj_frame.drop(['url','pub_date'],1)
wsj_frame.rename(columns={'snippet':'abstract'},inplace=True)

wsj_frame = wsj_frame[wsj_frame['date'] > datetime.date(2012,1,1)]
wsj_frame = wsj_frame[wsj_frame['date'] < datetime.date(2012,11,6)]

#cleaning Newsday
newsday_frame = pd.read_csv("./Newsday_Data/newsday_romney_or_obama_newer.csv", encoding = "UTF-8")
newsday_frame = newsday_frame.drop(['section'],1)
newsday_frame['date'] = newsday_frame.date.apply(globe_date_convert)

#cleaning PANewspapers
pa_frame = pd.read_csv("./PA_newspapers_Data/PA_romney_or_obama_newer.csv", encoding = "UTF-8")
pa_frame = pa_frame.drop(['section'],1)
pa_frame['date'] = pa_frame.date.apply(globe_date_convert)

#combine dataframes
total_frame = globe_frame.append(guardian_frame,ignore_index=True)
total_frame = total_frame.append(latimes_frame,ignore_index=True)
total_frame = total_frame.append(nydn_frame,ignore_index=True)
total_frame = total_frame.append(nyt_frame,ignore_index=True)
total_frame = total_frame.append(wp_frame,ignore_index=True)
total_frame = total_frame.append(newsday_frame,ignore_index=True)
total_frame = total_frame.append(pa_frame,ignore_index=True)
total_frame = total_frame.drop(['Unnamed: 0'],1)
total_frame['id'] = list(xrange(len(total_frame.index)))
total_frame.to_csv("./all_2012_data.csv", encoding = "UTF-8")

