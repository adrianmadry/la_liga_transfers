import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import MinMaxScaler


# Function to convert transfers fee expressed as STRING to FLOAT
def convert_to_number(value: str) -> float:
    value = value.upper().rstrip()
    if 'M' in value:
        return round(float(value.strip('M')), 2)
    elif 'K' in value:
        return round(float(value.strip('K')) / 1000, 2)
    else:
        return value



#### COLLECT DATA ####

# Import list of transfers
df_transfers = pd.read_csv('./data/transfers_from_api.csv', index_col=0, keep_default_na=False, na_values='')

# Import player's stats
df_stats = pd.DataFrame()
for year in range(2015, 2023):
    season_df = pd.read_csv(f'./data/stats_from_season_{year}.csv', index_col=0)
    df_stats = pd.concat([df_stats, season_df], ignore_index=True)

# Import list of spanish teams 
df_spanish_teams = pd.read_csv('./data/teams_from_Spain.csv', index_col=0)


#### DATA WRANGLING / DATA CLEANING ####

                            #### {df_transfers} ####
df_transfers = df_transfers.drop(['transfers.teams.in.logo', 'transfers.teams.out.logo'], axis=1)
df_transfers.drop_duplicates(inplace=True)
df_transfers.columns = [col.replace('.', '_') for col in df_transfers.columns]
df_transfers = df_transfers.dropna(subset=['transfers_teams_in_id'])

# Exclude from dataset Loan and Swap transfer types
df_transfers = df_transfers.dropna(subset='transfers_type')
valtodrop = ['Loan', 'End of Loan', 'Swap']
df_transfers = df_transfers[df_transfers['transfers_type'].isin(valtodrop) == False]

# Replace all data marked as "free" to value 0.0
df_transfers['transfers_type'] = np.where(df_transfers['transfers_type'].str.contains('free', case=False, na=False, regex=False), 0.0, df_transfers['transfers_type'])

# Replace all data marked as N/A|Unknown to None
df_transfers['transfers_type'] = np.where(df_transfers['transfers_type'].str.contains('N/A|Unknown', case=False, na=False, regex=True), np.nan, df_transfers['transfers_type'])

# Transform data to transfers_fee in EU (exchange rate valid on 25.06.23)
df_transfers['transfers_type'] = [convert_to_number((value).strip('$')) * 0.92 if isinstance(value, str) and '$' in value else 
                                  convert_to_number((value).strip('€')) if isinstance(value, str) and '€' in value else 
                                  convert_to_number(value) if isinstance(value, str) else
                                  value for value in df_transfers['transfers_type']]
df_transfers = df_transfers.rename(columns={'transfers_type': 'transfer_fee'})

# Change columns types
df_transfers['player_id'] = df_transfers['player_id'].astype('int')
df_transfers['transfers_teams_in_id'] = pd.to_numeric(df_transfers['transfers_teams_in_id']).astype('int')
df_transfers['transfers_date'] = pd.to_datetime(df_transfers['transfers_date'], errors='coerce') 

# Reset indexes
df_transfers = df_transfers.reset_index(drop=True)

# Create new column for season of transfer
"""
https://www.laliga.com/en-GB/transfers/laliga-easports?page=1

# Season 2018 is 2018/2019
# Summer transfer window is 18-07-01 - 18-09-01
# Winter transfer window is 19-01-01 - 19-02-01
# 
# So for every year:
# January, February, March - season of transfer is ({year} - 1)
# April to December        - season of transfer is {year}
"""

df_transfers['season_of_transfer'] = np.where(df_transfers['transfers_date'].dt.month.isin(range(1,4)),
                          df_transfers['transfers_date'].dt.year - 1,
                          df_transfers['transfers_date'].dt.year)

# Create new column for transfer window period
df_transfers['transfers_window'] = ['Summer' if tdate.month in range(7, 9) else
                                    'Winter' if tdate.month in range(1, 2) else
                                    'Other' for tdate in df_transfers['transfers_date']]


                            #### {df_stats} ####                        
# Rename column names
df_stats.columns = df_stats.columns.str.replace('.', '_')

# Get rid of duplicated rows
df_stats.drop_duplicates(inplace=True)

col_to_check = ['player_id', 'statistics_team_id', 'statistics_league_season', 'statistics_games_minutes', 'statistics_games_rating', 'statistics_passes_total']
df_stats.drop_duplicates(subset=col_to_check, inplace=True)

# Drop rows with None values in 'team_name'
mask = df_stats['statistics_team_name'].isna()
df_stats = df_stats.drop(df_stats[mask].index)

# Change  columns types
df_stats[['player_id', 'player_age', 'statistics_league_season']] = df_stats[['player_id', 'player_age', 'statistics_league_season']].astype('int')

# Convert 'player_height' columns as float
df_stats['player_height'] = np.where(df_stats['player_height'].str.contains('cm', regex=False), df_stats['player_height'].str.rstrip('cm'), np.nan)
df_stats['player_height'] = df_stats['player_height'].astype('float') 

# Calculate 'performance_metric' parameter to evaluate players performance
# Create DafaFrame that includes data to calculate 'performance_metric'
selected_columns = ['statistics_games_rating', 'statistics_goals_total', 'statistics_goals_assists', 'statistics_passes_key', 'statistics_goals_saves', 'statistics_tackles_total', 'statistics_tackles_interceptions']
weights = [0.25, 0.15, 0.1, 0.1, 0.2, 0.1, 0.1] # assaign weights for parameters in {selected_columns}

performance_data_df = df_stats[selected_columns]
performance_data_df.fillna(0.0, inplace=True)

# Normalize data and calculate 'performance_metric'
scaler = MinMaxScaler()
normalized_data = scaler.fit_transform(performance_data_df)

performance_metric = (normalized_data * weights).sum(axis=1)
df_stats['performance_metric'] = performance_metric

                            #### {df_spanish_teams} ####
# Rename column names
df_spanish_teams.columns = df_spanish_teams.columns.str.replace('.', '_')

#### MERGE DATASETS ####
# {merged_df} - List of players transferred to La liga clubs in the seasons from 2015/16 to 2022/23 and  their statistics in the first season after transfer

df_merged = df_transfers.merge(df_stats, how='inner', 
                               left_on=['player_id', 'player_name', 'transfers_teams_in_name', 'season_of_transfer'],
                               right_on=['player_id', 'player_name', 'statistics_team_name', 'statistics_league_season'])
    
# Create new column for categorize transfers 
df_merged['transfer_type'] = [None if np.isnan(id)  else
                              'Spanish' if id in df_spanish_teams['team_id'].unique() else
                              'Foreign' for id in df_merged['transfers_teams_out_id'].astype(float)]
     
#### EXPORT DATA TO DATABASE ####
server = 'DESKTOP-FK1AJ2V'
database = 'la_liga_transfers'
driver = 'ODBC Driver 17 for SQL Server'
engine = create_engine(f'mssql+pyodbc://@{server}/{database}?driver={driver}')

with engine.connect() as con:
    df_merged.to_sql(name='merged_data', con=con, if_exists='replace', index=False)
    df_spanish_teams.to_sql(name='spanish_teams', con=con, if_exists='replace', index=False)


