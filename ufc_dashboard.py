import streamlit as st
import pandas as pd
import re

# Load your UFC dataset (replace with your file path)
path_to_csv = 'C:/Users/theon/OneDrive/Desktop/Giga Projects/UFC_scraper/ufc_fn_Moreno_Erceg_final.csv'
match = path_to_csv.split('/')[-1]
df = pd.read_csv(path_to_csv)

# Set up the dashboard title
event_title = match.replace('_final.csv', '')
event_title = event_title.replace('_', ' ').upper()

st.title(f"{event_title} Matchup Dashboard")

# Create a list of fight pairs
fighters = list(df['Name'])
fights = {f'{fighters[i]} vs. {fighters[i + 1]}': [fighters[i], fighters[i + 1]] for i in range(0, len(fighters), 2)}

# Let the user select a fight
chosen_fight = st.selectbox("Select Fight", list(fights.keys()))

# Extract fighter names
fighter1, fighter2 = fights[chosen_fight]

# Get the data for each fighter
fighter1_data = df[df['Name'] == fighter1].iloc[0]
fighter2_data = df[df['Name'] == fighter2].iloc[0]

# List of stats to display in the table
stats = [
    'Record','Height', 'Weight', 'Reach', 'Stance', 'SLpM', 'StrAcc', 'SApM', 
    'StrDef', 'TDAvg', 'TDAcc', 'TDDef', 'SubAvg', 'pred_model'
]

# Create a dictionary to hold the data for the table
table_data = {
    'Stat': stats,
    fighter1: [fighter1_data[stat] for stat in stats],
    fighter2: [fighter2_data[stat] for stat in stats]
}

# Create a DataFrame for better visualization
comparison_df = pd.DataFrame(table_data)

# Display the comparison table without index
st.subheader("Fighter Stats Comparison")
st.table(comparison_df.set_index('Stat'))  # This removes the index and uses 'Stat' as the label
