import os
import pandas as pd

# Define the file path
file_path = r'D:\D DriveBaseball\Executable'

# Get a list of all files in the directory
file_list = os.listdir(file_path)

# Filter Excel files
excel_files = [file for file in file_list if file.endswith('.xlsx') or file.endswith('.xls')]

if len(excel_files) < 2:
    print("Insufficient Excel files in the specified directory.")
else:
    # Sort the Excel files alphabetically
    excel_files.sort()

    # Create the full file paths for the first and second Excel files
    first_excel_file_path = os.path.join(file_path, excel_files[0])
    second_excel_file_path = os.path.join(file_path, excel_files[1])

    # Read the Excel files into DataFrames
    dataframe1 = pd.read_excel(first_excel_file_path)
    dataframe2 = pd.read_excel(second_excel_file_path)

    # Rename columns for clarity
    dataframe1.columns = ['Gametime', 'Home Team', 'Away Team', 'Home Odds DF1', 'Away Odds DF1']
    dataframe2.columns = ['Gametime', 'Home Team', 'Away Team', 'Home Odds DF2', 'Away Odds DF2']

    # Merge dataframes on 'Home Team' and 'Away Team' while keeping the order of dataframe1
    combined_dataframe = pd.merge(dataframe1, dataframe2[['Home Team', 'Away Team', 'Home Odds DF2', 'Away Odds DF2']],
                                  on=['Home Team', 'Away Team'], how='left')

    # Check lengths of dataframes
    if len(dataframe1) != len(dataframe2):
        # Identify repeated games in dataframe1
        game_count = combined_dataframe.groupby(['Home Team', 'Away Team']).cumcount()

        # Fill in 'N/A' for repeated games in df2 odds
        combined_dataframe.loc[game_count > 0, ['Home Odds DF2', 'Away Odds DF2']] = 'N/A'

    # Calculate Home Win Probability and Away Win Probability
    combined_dataframe['Home Win Probability'] = (1 / combined_dataframe['Home Odds DF1']).round(3)
    combined_dataframe['Away Win Probability'] = (1 / combined_dataframe['Away Odds DF1']).round(3)

    # Calculate EV Home
    combined_dataframe['EV Home'] = combined_dataframe.apply(
        lambda row: (((pd.to_numeric(row['Home Odds DF2'], errors='coerce')) - 1) * row['Home Win Probability']) - 
                    (1 * (row['Away Win Probability'])), axis=1
    ).round(3)

    # Calculate EV Away
    combined_dataframe['EV Away'] = combined_dataframe.apply(
        lambda row: (row['Away Win Probability'] * ((pd.to_numeric(row['Away Odds DF2'], errors='coerce')) - 1)) - 
                    ((row['Home Win Probability']) * 1), axis=1
    ).round(3)

    # Select the required columns for the combined dataframe
    combined_dataframe = combined_dataframe[['Home Team', 'Away Team', 'Home Odds DF1', 'Away Odds DF1', 'Home Odds DF2', 'Away Odds DF2',
                                             'Home Win Probability', 'Away Win Probability', 'EV Home', 'EV Away']]

    # Print the combined dataframe
    print("Combined Dataframe:")
    print(combined_dataframe)
