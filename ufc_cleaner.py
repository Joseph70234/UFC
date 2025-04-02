import pandas as pd
import numpy as np
import re
from datetime import date

def clean_ufc_fights(df):
    # drop useless columns
    try:
        drop_cols = ['fighter1_Name', 'fighter1_Nickname',
                'fighter2_Name', 'fighter2_Nickname']
        df.drop(columns = drop_cols, axis=1, inplace=True)
    except:
        pass

    # clean reach cols
    df['fighter1_Reach'] = df['fighter1_Reach'].str.replace('"', '')
    df['fighter2_Reach'] = df['fighter2_Reach'].str.replace('"', '')

    # separate record
    df[['fighter1_Wins', 'fighter1_Losses', 'fighter1_Draws']] = df['fighter1_Record'].str.extract(r'(\d+)-(\d+)-(\d+)')
    df[['fighter2_Wins', 'fighter2_Losses', 'fighter2_Draws']] = df['fighter2_Record'].str.extract(r'(\d+)-(\d+)-(\d+)')

    # define height to inches function
    def height_to_inches(height):
        if pd.isna(height) or height == '--':
            return np.nan
        match = re.match(r"(\d+)' *(\d+)\"", height)
        if match:
            feet, inches = map(int, match.groups())
            return feet * 12 + inches
        return np.nan

    df['fighter1_Height_in'] = df['fighter1_Height'].apply(height_to_inches)
    df['fighter2_Height_in'] = df['fighter2_Height'].apply(height_to_inches)

    # remove text from weight column
    def clean_thing(weight):
        if pd.isna(weight) or weight == '--':
            return np.nan
        try:
            return int(''.join(filter(str.isdigit, weight)))
        except:
            return np.nan

    df['fighter1_Weight'] = df['fighter1_Weight'].apply(clean_thing)
    df['fighter2_Weight'] = df['fighter2_Weight'].apply(clean_thing)

    df['fighter1_StrAcc'] = df['fighter1_StrAcc'].apply(clean_thing)
    df['fighter1_StrDef'] = df['fighter1_StrDef'].apply(clean_thing)
    df['fighter1_TDAcc'] = df['fighter1_TDAcc'].apply(clean_thing)
    df['fighter1_TDDef'] = df['fighter1_TDDef'].apply(clean_thing)

    df['fighter2_StrAcc'] = df['fighter2_StrAcc'].apply(clean_thing)
    df['fighter2_StrDef'] = df['fighter2_StrDef'].apply(clean_thing)
    df['fighter2_TDAcc'] = df['fighter2_TDAcc'].apply(clean_thing)
    df['fighter2_TDDef'] = df['fighter2_TDDef'].apply(clean_thing)

    # change date to proper format
    df['fighter1_DOB'] = pd.to_datetime(df['fighter1_DOB'], format='%b %d, %Y', errors='coerce')
    df['fighter2_DOB'] = pd.to_datetime(df['fighter2_DOB'], format='%b %d, %Y', errors='coerce')

    # Get today's date
    today = pd.Timestamp(date.today())

    # Calculate age
    df['fighter1_Age'] = (today - df['fighter1_DOB']).dt.days // 365
    df['fighter2_Age'] = (today - df['fighter2_DOB']).dt.days // 365

    # replace missing value representations
    df.replace('--', pd.NA, inplace=True)

    # drop fights with missing data
    df = df.dropna()

    # drop old columns
    drop_cols = ['fighter1_Record', 'fighter2_Record',
                'fighter1_Height', 'fighter2_Height',
                'fighter1_DOB', 'fighter2_DOB']
    df = df.drop(columns=drop_cols)

    # change types
    df.loc[:, 'fighter1_Weight'] = df['fighter1_Weight'].astype(float)
    df.loc[:, 'fighter1_Reach'] = pd.to_numeric(df['fighter1_Reach'], errors='coerce')
    df.loc[:, 'fighter1_StrAcc'] = df['fighter1_StrAcc'].astype(float)
    df.loc[:, 'fighter1_StrDef'] = df['fighter1_StrDef'].astype(float)
    df.loc[:, 'fighter1_TDAcc'] = df['fighter1_TDAcc'].astype(float)
    df.loc[:, 'fighter1_TDDef'] = df['fighter1_TDDef'].astype(float)

    df.loc[:, 'fighter1_Wins'] = df['fighter1_Wins'].astype(int)
    df.loc[:, 'fighter1_Losses'] = df['fighter1_Losses'].astype(int)
    df.loc[:, 'fighter1_Draws'] = df['fighter1_Draws'].astype(int)

    df.loc[:, 'fighter2_Weight'] = df['fighter2_Weight'].astype(float)
    df.loc[:, 'fighter2_Reach'] = pd.to_numeric(df['fighter2_Reach'], errors='coerce')
    df.loc[:, 'fighter2_StrAcc'] = df['fighter2_StrAcc'].astype(float)
    df.loc[:, 'fighter2_StrDef'] = df['fighter2_StrDef'].astype(float)
    df.loc[:, 'fighter2_TDAcc'] = df['fighter2_TDAcc'].astype(float)
    df.loc[:, 'fighter2_TDDef'] = df['fighter2_TDDef'].astype(float)

    df.loc[:, 'fighter2_Wins'] = df['fighter2_Wins'].astype(int)
    df.loc[:, 'fighter2_Losses'] = df['fighter2_Losses'].astype(int)
    df.loc[:, 'fighter2_Draws'] = df['fighter2_Draws'].astype(int)

    # save to csv
    return df

first_df = pd.read_csv('./ufc_scraper/spiders/ufc_all_fights.csv')
final_df = clean_ufc_fights(first_df)
final_df.to_csv('clean_ufc_all_fights.csv', index=False)