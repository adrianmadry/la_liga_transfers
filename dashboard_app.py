import streamlit as st
import pandas as pd



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
selected_year = st.sidebar.selectbox('Year', list(reversed(range(2015,2023))))

# Get data from chosen year
playerstats = df[df['season_of_transfer'] == selected_year]

# Sidebar Team selection
sorted_unique_teams = sorted(playerstats['transfers_teams_in_name'].unique())
selected_teams = st.sidebar.multiselect('Team', sorted_unique_teams, sorted_unique_teams)

# Display stats
st.header('Display Player Stats of Selected Team(s)')
st.dataframe(playerstats[playerstats['transfers_teams_in_name'].isin(selected_teams)])
