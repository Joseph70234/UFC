import pandas as pd

def ufc_feat_eng(df, new_event):
    
    if new_event == 'no':
        # Encode fight_outcome (1 = fighter1 wins, 0 = fighter2 wins)
        df['fight_outcome_encoded'] = df['fight_outcome'].apply(lambda x: 1 if x == 'fighter1' else 0)
    
    # Create stat differentials
    df['height_diff'] = df['fighter1_Height_in'] - df['fighter2_Height_in']
    df['weight_diff'] = df['fighter1_Weight'] - df['fighter2_Weight']
    df['reach_diff'] = df['fighter1_Reach'] - df['fighter2_Reach']
    df['age_diff'] = df['fighter1_Age'] - df['fighter2_Age']

    # Striking differentials
    df['SLpM_diff'] = df['fighter1_SLpM'] - df['fighter2_SLpM']
    df['StrAcc_diff'] = df['fighter1_StrAcc'] - df['fighter2_StrAcc']
    df['SApM_diff'] = df['fighter1_SApM'] - df['fighter2_SApM']
    df['StrDef_diff'] = df['fighter1_StrDef'] - df['fighter2_StrDef']

    # Grappling differentials
    df['TDAvg_diff'] = df['fighter1_TDAvg'] - df['fighter2_TDAvg']
    df['TDAcc_diff'] = df['fighter1_TDAcc'] - df['fighter2_TDAcc']
    df['TDDef_diff'] = df['fighter1_TDDef'] - df['fighter2_TDDef']
    df['SubAvg_diff'] = df['fighter1_SubAvg'] - df['fighter2_SubAvg']

    # Experience differentials
    df['wins_diff'] = df['fighter1_Wins'] - df['fighter2_Wins']
    df['losses_diff'] = df['fighter1_Losses'] - df['fighter2_Losses']
    df['draws_diff'] = df['fighter1_Draws'] - df['fighter2_Draws']

    # Win rates
    df['fighter1_win_rate'] = df['fighter1_Wins'] / (df['fighter1_Wins'] + df['fighter1_Losses'] + df['fighter1_Draws'])
    df['fighter2_win_rate'] = df['fighter2_Wins'] / (df['fighter2_Wins'] + df['fighter2_Losses'] + df['fighter2_Draws'])
    df['win_rate_diff'] = df['fighter1_win_rate'] - df['fighter2_win_rate']

    # Encode stances (simple label encoding)
    stance_mapping = {stance: idx for idx, stance in enumerate(df['fighter1_Stance'].unique())}
    df['fighter1_Stance_encoded'] = df['fighter1_Stance'].map(stance_mapping)
    df['fighter2_Stance_encoded'] = df['fighter2_Stance'].map(stance_mapping)
    df['stance_diff'] = df['fighter1_Stance_encoded'] - df['fighter2_Stance_encoded']

    return df