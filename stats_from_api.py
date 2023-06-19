import requests
import pandas as pd
import time


# function to get player's statistics data from API
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

# function to get transfers data from API
def get_transfers(i):
    
    querystring = {"team": i} 
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()['response']
    
    # Make new list with players with more than 1 club in season 
    more_transfers = []
    for record in data:
        if len(record['transfers']) > 1:
            # Make new dict for each club 
            for transfer in record['transfers']:
                player_name = record['player']
                player_transfer = {'player': player_name, 'transfers': transfer}
                more_transfers.append(player_transfer)
            
    # Filter original data by including only players with 1 club in season
    filtered_data = []
    for record in data:
        if len(record['transfers']) == 1:
            filtered_data.append(record)
            
    # Get rid of list in season_data statistics key
    season_data_fixed = []
    for data in filtered_data:
        new_dict = {'player': data['player'], 'transfers': data['transfers'][0]}
        season_data_fixed.append(new_dict)
        
    # Merge data and append it to csv     
    whole_data = season_data_fixed + more_transfers
    df = pd.json_normalize(whole_data)
    
    return df
        

# Connect with API
url = "https://v3.football.api-sports.io/transfers"

headers = {
	"x-rapidapi-host": "v3.football.api-sports.io",
	"x-rapidapi-key": "xxxxxxxxxxxxxxxxxxxxxxxx" # Insert user API key
}

# Get statistics data and add to CSV       
for season_id in range(2015, 2023):
    stats_for_season(season_id)
    

# Get transfer data for each team
    # Teams IDs to get data 
teams_ids = [(529, 549), (711, 757), (797, 800)]

    # Create new CSV file      
with open('./data/transfers_from_api.csv', 'w', newline='', encoding='utf-8-sig') as f:
    pass

    # Get data from API and append to CSV    
a = 0 # flag for ommit headers  
for start, end in teams_ids:
    for i in range(start, end):
        df = get_transfers(i)
        
        if a == 0: # get headers in 1st iteration
            with open('./data/transfers_from_api.csv', 'a+', newline='', encoding='utf-8-sig') as file:
                df.to_csv(file, header=True)
            a += 1
            # print(f'I have aded 1st line, id = {i}')
        
        else: # rest data without headers
            with open('./data/transfers_from_api.csv', 'a+', newline='', encoding='utf-8-sig') as file:
                df.to_csv(file, header=False)
            # print(f'I have added another one, id = {i}')
        time.sleep(5)
   
       
 
    