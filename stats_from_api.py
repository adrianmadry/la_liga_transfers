import requests
import pandas as pd
import time
from typing import Any

# Function that get response from API and handling potential errors
def get_api_response(url: str, api_headers: dict[str, str], queryparams: dict[str, Any]) -> dict[str, Any]:

    try:
        response = requests.get(url, headers=api_headers, params=queryparams)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        raise errh
    except requests.exceptions.ReadTimeout as errt:
        raise errt
    except requests.exceptions.ConnectionError as errc:
        raise errc
    except requests.exceptions.MissingSchema as errmiss:
        raise errmiss
    except requests.exceptions.RequestException as errexc:
        raise errexc

    if response.status_code in range (200, 299):
      return response.json()
    else:
      raise Exception(f'Unexpected status code {response.status_code}')


# Function to check total pagination of API response and return list of data from all pages
def gather_all_pages_data(data: dict[str, Any], url: str, api_headers: dict[str, str], queryparams: dict[str, Any]) -> list[dict]:
    total_pagination = data['paging']['total']

    if  total_pagination == 1:
        all_pages_data = data['response']

    else:
        # print(f'No of pages for this season is {total_pagination}')
        all_pages_data = []
        for page_num in range(1, total_pagination + 1): # Iterating through all reponse pages
            queryparams["page"] = page_num # add to query no of page from get data
            response = get_api_response(url, api_headers, queryparams)
            page_data = response['response']
            # print(f'Page number is {page_num}')
            # print(f'Response lenght is {len(page_data)}')
            all_pages_data.extend(page_data)
            # print(f'Data List lenght is {len(all_pages_data)}')

            time.sleep(10)

    return all_pages_data


# Function that verify if given endpoint is correct and return key to filter data
def endpoint_validation(endpoint: str) -> str:
  if endpoint == 'players':
      return 'statistics'
  elif endpoint == 'transfers':
      return endpoint
  else:
      raise ValueError("Invalid endpoint. Only 'players' or 'transfers' are allowed.")

# Function to extract and organize data
# Function transform input data by filtering based on given endpoint ('players' or 'transfers')
# It separates events, such as transfers or statistics, from nested dictionaries into individual event dictionaries
def extract_data(dataset: list[dict], endpoint: str) -> list[dict]:
  # Check if given endpoint is correct and set key_to_filter accordingly
  key_to_filter = endpoint_validation(endpoint)

  extracted_list = []
  for record in dataset:
      # Iterate through each 'list_elem' in the selected key (either 'statistics' or 'transfers')
      for list_elem in record[key_to_filter]:
          # Create a new dictionary for each 'list_elem' 
          new_dict = {'player': record['player'], key_to_filter: list_elem}
          extracted_list.append(new_dict)

  return extracted_list
    

# Function to fetch data from API and return DataFrame object
def fetch_data_from_api(url: str, endpoint: str, api_headers: dict[str, str], queryparams: dict[str, Any]) -> pd.DataFrame:
    url = url + endpoint 
    data = get_api_response(url, api_headers, queryparams)
    all_pages_data = gather_all_pages_data(data, url, api_headers, queryparams)
    extracted_data = extract_data(all_pages_data, endpoint)   
    df = pd.json_normalize(extracted_data)
    return df


# Function to retrieve players statistics for specified league and specified season range
# Function output is separate CSV file for each season
def get_players_stats(url: str, api_key:str, start_season: int, end_season: int, league_id: int) -> None:
    headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": api_key}

    for season_id in range(start_season, end_season + 1):        
        df = fetch_data_from_api(url=url, endpoint='players', api_headers=headers, queryparams={"league": league_id, "season": season_id})
        df.to_csv(f'./data/stats_from_season_{season_id}.csv', encoding='utf-8-sig')
        

def list_of_ints(list_to_handle: list[range | int]) -> list[int]:
    list_of_teams_ids = []
    for list_elem in list_to_handle:
        if isinstance(list_elem, range): # Get sep INTs from range
            for item in list_elem:
                list_of_teams_ids.append(item)

        elif isinstance(list_elem, int):
            list_of_teams_ids.append(list_elem)

        else:
            raise ValueError("""teams_ids parameter should be list containing only RANGE or INT data types !
            For range please use syntax 'range(int,int)'
                                """) 
    return list_of_teams_ids


def get_transfers_data(url: str, api_key:str, teams_ids: list[range | int]) -> None:
    headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": api_key}
    csv_headers = True # Parameter to controll writeting headers to CSV
    list_of_teams_ids = list_of_ints(teams_ids)
    
    # Get data for each team ID and save it all to one CSV file  
    for team_id in list_of_teams_ids: 
        df = fetch_data_from_api(url, 'transfers', api_headers=headers, queryparams={"team": team_id})
        with open('./data/transfers_from_api.csv', 'a+', newline='', encoding='utf-8-sig') as file:
                df.to_csv(file, header=csv_headers)
        csv_headers = False # No headers should be appended to CSV after get 1st team data


# get_transfers_data(url="https://v3.football.api-sports.io/", api_key="xxxxxxx", teams_ids=[755, range(756, 760)])
# get_players_stats(url="https://v3.football.api-sports.io/", api_key="xxxxxxx", start_season=2015, end_season=2016, league_id=140) 
  