import pandas as pd
import os
from datetime import date
from ufc_prediction_model import *

def create_final_comparison_df(new_event_df_loc):

    # Load the all_fighters CSV
    all_fighters = pd.read_csv('./ufc_scraper/spiders/ufc_all_fighters.csv')

    # Load the new_event dataframe
    new_event_df = pd.read_csv(new_event_df_loc)

    # Extract fighter names from the new_event dataframe
    fighter1_names = new_event_df['fighter1_Name'].tolist()
    fighter2_names = new_event_df['fighter2_Name'].tolist()

    # Create an empty list to hold the fighter data
    fighter_data = []

    # For each pair of fighters (fighter1, fighter2)
    for f1, f2 in zip(fighter1_names, fighter2_names):
        # Extract the row for fighter 1
        f1_data = all_fighters[all_fighters['Name'] == f1].copy()
        f1_data.loc[:, 'Opponent'] = f2  # Add the opponent's name for fighter1
        fighter_data.append(f1_data)

        # Extract the row for fighter 2
        f2_data = all_fighters[all_fighters['Name'] == f2].copy()
        f2_data.loc[:, 'Opponent'] = f1  # Add the opponent's name for fighter2
        fighter_data.append(f2_data)

    # Combine all the data into one DataFrame
    final_df = pd.concat(fighter_data, ignore_index=True)

    # Ensure DOB is in datetime format and handle errors
    final_df['DOB'] = pd.to_datetime(final_df['DOB'], format='%b %d, %Y', errors='coerce')

    # Check for NaT values
    if final_df['DOB'].isna().any():
        print("Warning: Some dates were invalid and couldn't be parsed.")

    # Calculate the age based on the date of birth
    today = pd.Timestamp(date.today())
    final_df['Age'] = (today - final_df['DOB']).dt.days // 365

    pred_model = create_prediction_model(new_event_df_loc)
    final_df['pred_model'] = final_df['Name'].map(pred_model)

    # Save the final comparison DataFrame to CSV
    event_name = os.path.splitext(os.path.basename(new_event_df_loc))[0]
    final_df.to_csv(f'{event_name}_final.csv', index=False)

    print(f"Comparison DataFrame saved as {event_name}_final.csv")

