import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from bs4 import BeautifulSoup

# Initialize the Chrome webdriver
driver = webdriver.Chrome()

# Load the webpage using Selenium
driver.get("https://www.betus.com.pa/sportsbook/mlb/")
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
# Find the script element containing the JSON-like data
script_element = driver.find_element(By.XPATH, "//script[@type='application/ld+json']")
script_content = script_element.get_attribute("innerHTML")  # Corrected method name

# Parse the JSON-like content
json_data = json.loads(script_content)

# Find all span elements with id "awayName" using XPath
away_name_elements = soup.select('div#awayTeamContainer span#awayName a')
home_name_elements = soup.select('div#homeTeamContainer span#homeName a')

# Initialize lists to store team names
away_team_list = [element.text.strip() for element in away_name_elements]
home_team_list = [element.text.strip() for element in home_name_elements]

# Print the collected away team names
print("Away Team List")
for away_team in away_team_list:
    print("Away Team Name:", away_team)

# Print the collected home team names
print("Home Team List")
for home_team in home_team_list:
    print("Home Team Name:", home_team)

# Create an empty list to store team names and moneylines
team_names = []
moneylines = []

quotes = driver.find_elements(By.CSS_SELECTOR, 'div.visitor-lines div.line-container, div.home-lines div.line-container')
# Iterate through each quote element and extract the text
for quote in quotes:
    bet_links = quote.find_elements(By.CSS_SELECTOR, 'a.bet-link')
    for link in bet_links:
        text = link.text.strip()
        # Handle "Ev" (even odds) case
        if text == "Ev":
            text = "+100"  # Default to +100 if "Ev" is encountered
        if re.match(r'^[+-]?\d+$', text):  # Check if the text is a number with optional sign + or -
            moneylines.append(text)

# Ensure that the number of moneylines matches the number of teams
while len(moneylines) < len(away_team_list) + len(home_team_list):
    moneylines.append('N/A')

# Create the dataframe
betus_data = {
    'Date': [],
    'Home Team': home_team_list,
    'Away Team': away_team_list,
    'Moneyline Home': [],
    'Moneyline Away': [],
    'Gametime': []
}

# Extract game details from the JSON data
date_texts = [event['startDate'][:10] for event in json_data]
game_times = [event['startDate'][11:19] for event in json_data]

# Assign date and game time values to the dataframe
betus_data['Date'] = date_texts[:len(home_team_list)]
betus_data['Gametime'] = game_times[:len(home_team_list)]

# Assign moneylines to corresponding teams
current_index = 0  # Track the current index in the original dataframe's moneylines

for i in range(len(home_team_list)):
    if current_index < len(moneylines):
        betus_data['Moneyline Away'].append(moneylines[current_index])
        current_index += 1
    else:
        betus_data['Moneyline Away'].append('N/A')
    if current_index < len(moneylines):
        betus_data['Moneyline Home'].append(moneylines[current_index])
        current_index += 1
    else:
        betus_data['Moneyline Home'].append('N/A')

betus_df = pd.DataFrame(betus_data)

# Print the Gametime list
print("Gametime:", betus_data['Gametime'])

# Print the BETUS Dataframe with the new Gametime column
print("\nBETUS Dataframe:")
print(betus_df)

# Create and print the BETUS MLB Output DF
betus_mlb_output_df = betus_df.drop(columns=['Date'])
betus_mlb_output_df = betus_mlb_output_df[['Gametime', 'Home Team', 'Away Team', 'Moneyline Home', 'Moneyline Away']]
betus_mlb_output_df = betus_mlb_output_df.rename(columns={'Moneyline Home': 'Home Odds', 'Moneyline Away': 'Away Odds'})

betus_mlb_output_df['Gametime'] = betus_mlb_output_df['Gametime'].str[:-3]

# Perform calculations on Home Odds and Away Odds columns and round to 2 decimal places
# Perform calculations on Home Odds and Away Odds columns and round to 5 decimal places
betus_mlb_output_df['Home Odds'] = betus_mlb_output_df['Home Odds'].apply(lambda x: round(abs((100 / float(x))) + 1, 5) if float(x) < 0 else round((float(x) / 100) + 1, 5))
betus_mlb_output_df['Away Odds'] = betus_mlb_output_df['Away Odds'].apply(lambda x: round(abs((100 / float(x))) + 1, 5) if float(x) < 0 else round((float(x) / 100) + 1, 5))


# Print the new dataframe
print("\nBETUS MLB Output DF:")
print(betus_mlb_output_df)

# Save the dataframe as an Excel file
excel_filepath = r"D:\D DriveBaseball\Executable\2-BETUS_Dataframe.xlsx"
betus_mlb_output_df.to_excel(excel_filepath, index=False)

print(f"Excel file saved successfully to: {excel_filepath}")

# Close the webdriver after scraping is done
driver.quit()
