# ### Libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ### Connect with URL
url= "https://en.wikipedia.org/wiki/2024_MotoGP_World_Championship"
headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

response= requests.get(url, headers= headers)
print(f"Status Code: {response.status_code}")
print(f"Page size: {len(response.text)} characters")

if response.status_code== 200:
    print("SUCCESS! Wikipedia responded!")
else:
    print(f"Error: {response.status_code}")


# ### Fetch Tables
soup= BeautifulSoup(response.text, 'html.parser')

# Find all tables with class 'wikitable'
tables= soup.find_all('table', {'class': 'wikitable'})
print(f"Found {len(tables)} tables on the page")


for i, table in enumerate(tables[:3]):
    print(f"\n--- Table {i+1} ---")
    # Get first row to see column headers
    first_row= table.find('tr')
    headers= [th.get_text(strip=True) for th in first_row.find_all('th')]
    print(f"Headers: {headers[:6]}")

race_table= tables[2]

first_row= race_table.find('tr')
all_headers= [th.get_text(strip= True) for th in first_row.find_all('th')]
print(f"All headers: {all_headers}")
print()

race_data= []
rows= race_table.find_all('tr')[1:]

for row in rows:
    cols= row.find_all(['td', 'th'])
    row_data= [col.get_text(strip= True) for col in cols]
    
    if len(row_data) >= 4:
        race_data.append(row_data)

print(f"Extracted {len(race_data)} races!")
print("\nFirst 3 races:")
for i, race in enumerate(race_data[:3], 1):
    print(f"{i}. {race[:5]}") 

df= pd.DataFrame(race_data)
df

# ### Find and Fetch the table with Winners
for i, table in enumerate(tables[:7]): 
    first_row= table.find('tr')
    headers= [th.get_text(strip= True) for th in first_row.find_all('th')]
    
    if any(word in ' '.join(headers).lower() for word in ['winner', 'pole', '1st', 'podium']):
        print(f"Table {i+1} - HAS WINNER INFO!")
        print(f"Headers: {headers[:8]}")
        print()

winners_table= tables[3]

first_row= winners_table.find('tr')
winner_headers= [th.get_text(strip=True) for th in first_row.find_all('th')]
print(f"All headers: {winner_headers}\n")

winner_data = []
rows= winners_table.find_all('tr')[1:]

for row in rows:
    cols= row.find_all(['td', 'th'])
    row_data= [col.get_text(strip=True) for col in cols]
    
    if len(row_data) >= 5:
        winner_data.append(row_data)

print(f"Extracted {len(winner_data)} race results!")

df_winners= pd.DataFrame(winner_data, columns= winner_headers)

print(f"\nDataFrame shape: {df_winners.shape}")
print("\nFirst 5 races with winners:")
print(df_winners[['Round', 'Grand Prix', 'Winning rider']].head())

# ### Merge the 2 Tables
df.columns= ['Round', 'Date', 'Grand Prix', 'Circuit']

df_complete= df.merge(
                      df_winners[['Round', 'Winning rider', 'Pole position', 'Fastest lap']], 
                        on='Round',
                      how='left'
                     )

print(f"Merged DataFrame: {df_complete.shape}")
print("\nFirst 5 complete race records:")
print(df_complete.head())

output_file= '004_data/motogp_2024_results.csv'
df_complete.to_csv(output_file, index=False)
print(f"\nData saved to: {output_file}")
print(f"Scraping complete! {len(df_complete)} races saved!")