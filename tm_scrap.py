from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd


# Function that scrap data for specific season
def scrapper_for_season(season):

    url = f'https://www.transfermarkt.com/laliga/transfers/wettbewerb/ES1/plus/?saison_id={season}&s_w=&leihe=0&intern=0&intern=1'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    page = requests.get(url, headers=headers)

    soup1 = BeautifulSoup(page.content, "lxml")
    soup2 = BeautifulSoup(soup1.prettify(), "lxml")


    # Get 'Club Names" (from tables titles)
    h2_headings = soup2.find_all('h2')
    club_names = []
    h2_headings = soup2.find_all('h2', class_="content-box-headline content-box-headline--inverted content-box-headline--logo")           
    for h2 in h2_headings:
        club_names.append(h2.text.strip())
            
    # Get data from tables
    tables = soup2.find_all("table")
    i = 0  
                    
    for table in tables:
        first_col = table.find('th')
        if first_col is not None:   # Exclude tables without headers
            if first_col.text.strip() == "In":  # Filtering only by IN transfers tables
                body = table.find('tbody')
                rows = body.find_all('tr')
                for row in rows:
                    data = []
                    cells = row.find_all('td')
                    
                    for cell in cells:
                        
                        if cell.get('class') == ['no-border-rechts', 'zentriert']:   # Get 'Left'(club name) Column
                            a = cell.find('a')
                            data.append(a['title'])
                        
                        elif cell.find('img'):    # Get 'Left Club Country' from <img>
                            img = cell.find('img')
                            data.append(img['title'])
                            
                        else:   
                            data.append(cell.text.strip())
                                 
                    cleaned = data[0].split('\n') # Clean player's name
                    data[0] = cleaned[0]
                    data.append(club_names[i])  # Add 'Club name' for each row
                    data.append(season) # Add 'Year of transfer' for each row
                    
                    # Write data to CSV
                    with open(f'./data/Laliga_transfers.csv', 'a+', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(data)
                    
                i += 1
            
                  
# Get headings from table (+ add additional column names)   
url = 'https://www.transfermarkt.com/laliga/transfers/wettbewerb/ES1/plus/?saison_id=2022&s_w=&leihe=0&intern=0&intern=1'
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0", "Accept-Encoding":"gzip, deflate", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
page = requests.get(url, headers=headers)

soup1 = BeautifulSoup(page.content, "lxml")
soup2 = BeautifulSoup(soup1.prettify(), "lxml")

headings = []
first_in_table = soup2.find('div', class_='responsive-table')   # Scrap from first table of IN transfers
th_finder = first_in_table.find_all('th')

for th in th_finder:   
    header = th.text.strip()
    headings.append(header)

headings.append('Club name') 

# Add additional columns inside the headings list
index = headings.index('Left')
headings = headings[:index+1] + ['Left Club Country'] + headings[index+1:] + ['Year of transfer']

# Create new CSV file and insert headings        
with open(f'./data/Laliga_transfers.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(headings)
    
# Scrap data and add to CSV       
for season in range(2016, 2023):
    scrapper_for_season(season)
            

 



        
    
    

