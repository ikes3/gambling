from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd

# Initialize the Chrome webdriver
driver = webdriver.Chrome()
# Load the webpage using Selenium
driver.get("https://www.pinnacle.com/en/baseball/mlb/matchups/")

# Wait for 10 seconds
time.sleep(10)

# Get the HTML content after page load
html_content = driver.page_source

# Close the Selenium driver
driver.quit()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <span> elements with class "ellipsis"
all_spans = soup.find_all('span', class_='ellipsis')

print("moneyline odds:")
# Find all <span> elements with class "style_price__3Haa9"
price_spans = soup.find_all('span', class_='style_price__3Haa9')
for span in price_spans:
    print(span.text.strip())

# Find all elements with class "style_matchupDate__UG-mT"
matchup_dates = soup.find_all(class_='style_matchupDate__UG-mT')

print("matchup times:")

# Print the text content of each matchup date
for date in matchup_dates:
    print(date.text.strip())

# Extract home and away team names alternating from the all_spans list, ignoring the last team
home_teams = []
away_teams = []
matchup_dates_list = []
for i in range(len(all_spans) - 1):  # Ignore the last team
    if i % 2 == 0:
        away_teams.append(all_spans[i].text.strip())
    else:
        home_teams.append(all_spans[i].text.strip())

# Extract matchup dates
for date in soup.find_all(class_='style_matchupDate__UG-mT'):
    matchup_dates_list.append(date.text.strip())

# Extract home and away odds from the price_spans list, alternating to fill the columns
home_odds = [span.text.strip() for span in price_spans[1::2]]  # Start from index 1, step by 2
away_odds = [span.text.strip() for span in price_spans[::2]]  # Start from index 0, step by 2

# Check if the odds lists are 1 value short of the team lists
if len(home_odds) + 1 == len(home_teams):
    # Insert 'N/A' for the first row
    home_odds.insert(0, 'N/A')
    away_odds.insert(0, 'N/A')
elif len(home_odds) + 2 == len(home_teams):
    # Insert 'N/A' for the first and second rows
    home_odds.insert(0, 'N/A')
    home_odds.insert(1, 'N/A')
    away_odds.insert(0, 'N/A')
    away_odds.insert(1, 'N/A')

# Create a DataFrame
data = {'Gametime': matchup_dates_list, 'Home Team': home_teams, 'Away Team': away_teams,
        'Home Odds': home_odds, 'Away Odds': away_odds}
df = pd.DataFrame(data)
print("Pinnacle DF")
# Print the DataFrame
print(df)

# Create a new DataFrame by removing rows where 'Gametime' is 'Live Now'
filtered_df = df[df['Gametime'] != 'Live Now']


# Create the final DataFrame
pinnacle_mlb_output_df = filtered_df.reset_index(drop=True)

print("Pinnacle MLB Output DF")
# Print the new DataFrame
print(pinnacle_mlb_output_df)

file_path = r'D:\D DriveBaseball\Executable\1-Pinnacle_MLB_Output.xlsx'

# Save the DataFrame as an Excel file
pinnacle_mlb_output_df.to_excel(file_path, index=False)

# Print a message to confirm that the file has been saved
print(f"Pinnacle MLB Output DF has been saved as an Excel file to: {file_path}")