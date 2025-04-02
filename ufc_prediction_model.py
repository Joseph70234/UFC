import pandas as pd
from ufc_cleaner import clean_ufc_fights
from ufc_feature_engineer import ufc_feat_eng
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import GridSearchCV

def create_prediction_model(new_event_df_loc):
    
    # read in CSVs
    new_event_df = pd.read_csv(new_event_df_loc)
    all_fights_df = pd.read_csv('./ufc_scraper/spiders/ufc_all_fights.csv')

    # clean fights
    new_event_df = clean_ufc_fights(new_event_df)
    all_fights_df = clean_ufc_fights(all_fights_df)

    # feature engineer fights
    new_event_df = ufc_feat_eng(new_event_df, 'yes')
    all_fights_df = ufc_feat_eng(all_fights_df, 'no')

    columns_to_keep = [
        'height_diff', 'weight_diff', 'reach_diff', 'age_diff', 
        'SLpM_diff', 'StrAcc_diff', 'SApM_diff', 'StrDef_diff', 
        'TDAvg_diff', 'TDAcc_diff', 'TDDef_diff', 'SubAvg_diff',
        'wins_diff', 'losses_diff', 'draws_diff', 'win_rate_diff', 
        'fighter1_Stance_encoded', 'fighter2_Stance_encoded', 'stance_diff'
    ]

    # Select only the specified columns to keep
    X = all_fights_df[columns_to_keep]
    y = all_fights_df['fight_outcome_encoded']  # Target variable

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # verify the split
    print(f"Training data: {X_train.shape[0]} samples")
    print(f"Testing data: {X_test.shape[0]} samples")

    # Define parameter grid for Random Forest
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }

    # Initialize the model
    rf_model = RandomForestClassifier(random_state=42)

    # Perform Grid Search
    grid_search = GridSearchCV(rf_model, param_grid, cv=5, n_jobs=-1, verbose=2)

    # Fit grid search
    grid_search.fit(X_train, y_train)

    # Make predictions with the best model
    y_pred_best = grid_search.best_estimator_.predict(X_test)

    # Evaluate the performance
    print(f"Best Model Accuracy: {accuracy_score(y_test, y_pred_best):.4f}")

    new_event_dropped_cols_df = new_event_df[columns_to_keep]

    prediction = grid_search.best_estimator_.predict(new_event_dropped_cols_df)

    probabilities = grid_search.best_estimator_.predict_proba(new_event_dropped_cols_df)

    final_dict = {}

    i = 0
    for item in prediction:
        final_dict[new_event_df['fighter1'][i]] = probabilities[i][1]
        final_dict[new_event_df['fighter2'][i]] = probabilities[i][0]
        i += 1

    return final_dict