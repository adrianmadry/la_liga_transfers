import requests
import pandas as pd
import time


def stats_for_season(season_id):
    querystring = {"league": "140", "season": season_id} 
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    no_of_pages = data['paging']['total']
    a = 1 
    season_data = []
    print('No of pages for this season is', no_of_pages)

    # Iterating through all reponse pages
    for a in range(1, no_of_pages + 1):
        querystring = {"league": "140", "season": season_id, "page": a} 
        response = requests.get(url, headers=headers, params=querystring)
        page_data = response.json()['response']
        print('Page number is', a)
        print('Response lenght is', len(page_data))
        
        season_data.extend(page_data)
        print('Data List lenght is', len(season_data))
        
        time.sleep(10)
          
    # Make new list with players with more than 1 club in season 
    more_clubs = []
    for record in season_data:
        if len(record['statistics']) > 1:
            # Make new dict for each club 
            for stats in record['statistics']:
                player_name = record['player']
                player_stats = {'player': player_name, 'statistics': stats}
                more_clubs.append(player_stats)
                        
    # Filter original data by including only players with 1 club in season
    filtered_data = []
    for record in season_data:
        if len(record['statistics']) == 1:
            filtered_data.append(record)
            
    season_data = filtered_data
            
    # Get rid of list in season_data statistics key
    season_data_fixed = []
    for data in season_data:
        new_dict = {'player': data['player'], 'statistics': data['statistics'][0]}
        season_data_fixed.append(new_dict)
        
    # Merge data and save it to csv     
    whole_data = season_data_fixed + more_clubs
    df = pd.json_normalize(whole_data)
    df.to_csv(f'./data/stats_from_season_{season_id}.csv', encoding='utf-8-sig')

# Connect with API
url = "https://v3.football.api-sports.io/players"


headers = {
	"x-rapidapi-host": "v3.football.api-sports.io",
	"x-rapidapi-key": "XXXXXXXXXXXXXXXXXXXXXXXXXXX" # Insert user API key
}

# Scrap data and add to CSV       
for season_id in range(2016, 2023):
    stats_for_season(season_id)
   
       
 
    