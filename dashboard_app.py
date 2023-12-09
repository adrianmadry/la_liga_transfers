import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(page_title='Dashboard_app', page_icon=':soccer:', layout='wide')
st.title('La Liga Transfer Stats Dashboard')

st.markdown("""
This app displays statistics of players in first seasin after transfer to La Liga clubs
* **Python libraries:** pandas, streamlit
* **Data source:** [API-Football](https://www.api-football.com/).
""")


# Import data
df = pd.read_csv('./data/merged_df.csv')

# Sidebar for Year
st.sidebar.header('User Input Features')
years_list = list(reversed(range(2015,2023)))
years_list.append('ALL')
selected_year = st.sidebar.selectbox('Year', years_list, index=years_list.index('ALL'))

# Get data from chosen year
if selected_year == 'ALL':
    playerstats = df
else:
    playerstats = df[df['season_of_transfer'] == selected_year]

# Sidebar Team selection
sorted_unique_teams = sorted(playerstats['transfers_teams_in_name'].unique())
selected_teams = st.sidebar.multiselect('Team', sorted_unique_teams, sorted_unique_teams)

# Display raw data frame
st.subheader('Display Player Stats of Selected Team(s)')
filtered_df = playerstats[playerstats['transfers_teams_in_name'].isin(selected_teams)]
st.write('Data Dimension: ' + str(filtered_df.shape[0]) + ' rows and ' + str(filtered_df.shape[1]) + ' columns.')
hidden_data = st.expander('Click here to see raw data for Your selection')
hidden_data.dataframe(filtered_df)
st.text('')
st.text('')

# Declare columns (split dashboard layout)
col1, col2 = st.columns((1, 1.5))

# Display foreign vs spanish transfers plot
foreign_spanish = filtered_df['transfer_type'].value_counts(normalize=True) * 100

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(5,5))
ax.pie(foreign_spanish, labels=foreign_spanish.index, autopct='%1.1f%%')
ax.set_title('Percentage share for spanish and foreign transfers')
col1.pyplot(fig)

# Display Cumulative 'Transfer Fee' over time plot
fee_time_df = filtered_df.sort_values(by='transfers_date')
fee_time_df['transfers_date'] = pd.to_datetime(fee_time_df['transfers_date'])
fee_time_df['cumulative_transfer_fee'] = fee_time_df['transfer_fee'].fillna(0.0).cumsum()

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(fee_time_df['transfers_date'], fee_time_df['cumulative_transfer_fee'], color='steelblue')
ax.set_title('Cumulative Transfer Fee Over Time')
ax.set_xlabel('Transfer Date')
ax.set_ylabel('Cumulative Transfer Fee')
ax.grid(True)

col2.pyplot(fig)

# Correlation viewer
col3_spacer, col3, col4_spacer, col_4, col5_spacer = st.columns((.2, 1.5, .4, 4.4, .2)) # Declare columns (split dashboard layout)
col3.subheader('Correlation of Game Stats')
label_columns_dict_correlation = {"Goals": "statistics_goals_total", "Transfer Fee": "transfer_fee", "Player Age": "player_age", "Player_rating": "statistics_games_rating"}
with col3:
    st.markdown('Choose your stats?')    
    x_axis_selection = st.selectbox ("Which attribute do you want on the x-axis?", list(label_columns_dict_correlation.keys()))
    y_axis_selection = st.selectbox ("Which attribute do you want on the y-axis?", list(label_columns_dict_correlation.keys()))

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(6,4))
ax.scatter(filtered_df[label_columns_dict_correlation[x_axis_selection]], filtered_df[label_columns_dict_correlation[y_axis_selection]], alpha=0.5)
ax.set_title('correlation plot')
ax.grid(True)
col_4.pyplot(fig)

# TOP Players stats viewer
col6_spacer, col6, col7_spacer, col_7, col8_spacer = st.columns((.2, 2.0, .4, 4.4, .2)) # Declare columns (split dashboard layout)
col6.subheader('TOP Player Stats Viewer')
top_stats_dict_correlation = {'Performance Metric': 'performance_metric', 'Transfer Fee': 'transfer_fee', 'Goals Total': 'statistics_goals_total', 'Assist Total': 'statistics_goals_assists', 'Rating per game (mean)': 'statistics_games_rating', 'Player Age': 'player_age', 
 'Shots Total': 'statistics_shots_total', 'Game appearences': 'statistics_games_appearences', "Total min in game": 'statistics_games_minutes', 
 'Key Passes Total': 'statistics_passes_key', 'Pass Accuracy': 'statistics_passes_accuracy', 'Interceptions Total':'statistics_tackles_interceptions', 'Duels Won': 'statistics_duels_won'}
top_stats_df = filtered_df[['player_name'] + list(top_stats_dict_correlation.values())]

with col6:
    st.markdown('Choose your stats?')    
    x_axis_selection = st.selectbox ("Which statisctics would you like to see?", list(top_stats_dict_correlation.keys()))
       
newdf = top_stats_df[['player_name', top_stats_dict_correlation[x_axis_selection]]].dropna().sort_values(by=top_stats_dict_correlation[x_axis_selection], ascending=False).head(10)

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(6,4))
bars = ax.bar(newdf['player_name'], newdf[top_stats_dict_correlation[x_axis_selection]], color='lightsteelblue')

ax.set_xticklabels(newdf['player_name'], rotation=45, ha='right', size=8)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 2), ha='center', va='bottom')
ax.set_title(f'TOP 10 Players - {x_axis_selection} Stats')
ax.grid(True)
col_7.pyplot(fig)
   
