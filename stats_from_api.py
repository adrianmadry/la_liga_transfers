import requests
import pandas as pd
import time

# Get data from API
url = "https://v3.football.api-sports.io/players"


headers = {
	"x-rapidapi-host": "v3.football.api-sports.io",
	"x-rapidapi-key": "b69bc50a7b3f69db6443565654f106fc"
}


querystring = {"league": "140", "season": "2021"} 
response = requests.get(url, headers=headers, params=querystring)
data = response.json()

no_of_pages = data['paging']['total']
a = 1 
season_data = []
print('No of pages for this season is', no_of_pages)

while a <= no_of_pages:
    querystring = {"league": "140", "season": "2021", "page": a} 
    response = requests.get(url, headers=headers, params=querystring)
    page_data = response.json()['response']
    print('Response lenght is', len(page_data))
    print('Page number is', a)
    
    season_data.extend(page_data)
    print('Data List lenght is', len(season_data))
    
    a += 1
    print(a)
    
    time.sleep(10)
    
    
# Make list with players with more than 1 club in season
more_clubs = []
for record in season_data:
    if len(record['statistics']) > 1:
        # make new for each club 
        for stats in record['statistics']:
            player_name = record['player']
            player_stats = (player_name, stats)
            more_clubs.append(player_stats)
            
# Turn tuples into dicts
more_clubs_dicts = []
for record in more_clubs:
    record_dict = {'player': record[0], 'statistics': record[1]} 
    more_clubs_dicts.append(record_dict)
            
# Erase players with more than 1 club from original list
for record in season_data:
    if len(record['statistics']) > 1:
        season_data.remove(record)
        
# Get rid of list in season_data statistics key
season_data_fixed = []
for data in season_data:
    new_dict = {'player': data['player'], 'statistics': data['statistics'][0]}
    season_data_fixed.append(new_dict)
    
 # Merge data and save it to csv     
whole_data = season_data_fixed + more_clubs_dicts
df = pd.json_normalize(whole_data)
season_num = 2021
df.to_csv(f'get_data_from_api_{season_num}.csv')




   
       
 
    