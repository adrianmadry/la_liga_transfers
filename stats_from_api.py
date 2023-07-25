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
        print("HTTP Error")
        print(errh.args[0])
    except requests.exceptions.ReadTimeout as errt:
        print("Time out")
        print(errt.args[0])
    except requests.exceptions.ConnectionError as errconn:
        print("Connection error")
        print(errconn.args[0])
    except requests.exceptions.MissingSchema as errmiss:
        print("Missing schema: include http or https")
        print(errmiss.args[0])
    except Exception as e:
        print("An unexpected error occurred:")
        print(e)

    if response.status_code == 200:
      return response.json()
    else:
      raise Exception(f'Unexpected status code {response.status_code}')

# Function to check total pagination of API response and return list of data from all pages
def gather_all_pages_data(data: dict[str, Any], url: str, api_headers: dict[str, str], queryparams: dict[str, Any]) -> list[dict]:
    total_pagination = data['paging']['total']

    if  total_pagination == 1:
        all_pages_data = data['response']

    else:
        print(f'No of pages for this season is {total_pagination}')
        all_pages_data = []
        # Iterating through all reponse pages
        for a in range(1, total_pagination + 1):
            queryparams["page"] = a
            response = get_api_response(url, api_headers, queryparams)
            page_data = response['response']
            print(f'Page number is {a}')
            print(f'Response lenght is {len(page_data)}')
            all_pages_data.extend(page_data)
            print(f'Data List lenght is {len(all_pages_data)}')

            time.sleep(10)

    return all_pages_data


# Function to get first element from list as dict object
def get_first_element(record: dict[str, Any], key: str) -> dict[str, dict]:
  new_dict = {'player': record['player'], key: record[key][0]}
  return new_dict



# --- Function to filter datasets and extract data from JSON file (by given key):
# 1. If record[key_to_filter] is list with 2 elements or more - create separate dict for each
# 2. If record[key_to_filter] is list with 1 element - get clean dict object---

def extract_data(dataset: list[dict], endpoint: str) -> list[dict]:
    # Check if given endpoint is correct and set key_to_filter accordingly
    if endpoint == 'players':
        key_to_filter = 'statistics'
    elif endpoint == 'transfers':
        key_to_filter = endpoint
    else:
        raise ValueError("Invalid endpoint. Only 'players' or 'transfers' are allowed.")

    extracted_list = []
    for record in dataset:
        if len(record[key_to_filter]) > 1:
            # Make new dict for each list element
            for list_element in record[key_to_filter]:
                player_name = record['player']
                player_data = {'player': player_name, key_to_filter: list_element}
                extracted_list.append(player_data)
        elif len(record[key_to_filter]) == 1:
            new_dict = get_first_element(record, key_to_filter)
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

# Function to append pd.DataFrame to CSV file
def append_dataframe_to_csv(data_frame: pd.DataFrame, get_headers: bool) -> None:
    with open('./data/transfers_from_api.csv', 'a+', newline='', encoding='utf-8-sig') as file:
                data_frame.to_csv(file, header=get_headers)


# Function to retrieve players statistics for specified league and specified season range
# Function output is separate CSV file for each season
def get_players_stats(url: str, api_key:str, start_season: int, end_season: int, league_id: int) -> None:
    headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": api_key}

    for season_id in range(start_season, end_season + 1):        
        df = fetch_data_from_api(url=url, endpoint='players', api_headers=headers, queryparams={"league": league_id, "season": season_id})
        df.to_csv(f'./data/stats_from_season_{season_id}.csv', encoding='utf-8-sig')
        

# Function to fetch transfers data from given teams IDs
# Output is one CSV file with transfer data for all teams
def get_transfers_data(url: str, api_key:str, teams_ids: list[range | int]) -> None:
  headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": api_key}
  
  csv_headers = True
  for list_elem in teams_ids:
    if isinstance(list_elem, range):
      # Iterate over range
      for item in list_elem:
        df = fetch_data_from_api(url, 'transfers', api_headers=headers, queryparams={"team": item})
        append_dataframe_to_csv(data_frame=df, get_headers=csv_headers)
        csv_headers = False # No headers should be appended to CSV after 1st team data append

    elif isinstance(list_elem, int):
      df = fetch_data_from_api(url, 'transfers', api_headers=headers, queryparams={"team": list_elem})
      append_dataframe_to_csv(data_frame=df, get_headers=csv_headers)
      csv_headers = False # No headers should be appended to CSV after 1st team data append

    else:
      raise ValueError('teams_ids parameter should be list containing only RANGE or INT data types !')



# get_transfers_data(url="https://v3.football.api-sports.io/", api_key="xxxxxxx", teams_ids=[755, range(756, 760)])
# get_players_stats(url="https://v3.football.api-sports.io/", api_key="xxxxxxx", start_season=2015, end_season=2016, league_id=140) 
  