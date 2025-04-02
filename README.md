This is a repository for UFC fight predictions and data analysis. 

Here is how you use the various files:

FOR CREATING DATASET OF ALL FIGHTS:
  1. Open command prompt, change cd to wherever you have stored the scrapy spiders
  2. Run command "scrapy crawl UFC_fight_scrape -O ufc_all_fights.csv"

FOR CREATING DATASET OF ALL FIGHTERS:
  1. Open command prompt, change cd to wherever you have stored the scrapy spiders
  2. Run command "scrapy crawl ufc_roster_scrape -O ufc_all_fighters.csv"

FOR PREDICTING NEW EVENT FIGHT OUTCOMES:
  1. Open command prompt, change cd to wherever you have stored the scrapy spiders
  2. Run command prompt "scrapy crawl UFC_upcoming_event_scrape -O [event name].csv"
       - Fight night naming scheme: ufc_fn_fighter1lastname_fighter2lastname(_number).csv
       - UFC naming scheme: ufc_number.csv
  3. Open run_final.ipynb, change final line to create_final_comparison_df([relative path to upcoming_event csv])
  (IF DASHBOARD DESIRED)
  4. Open ufc_dashboard.py, change line 6 path_to_csv to the absolute path to absolute path ending in "[event name]_final.csv"
  5. Change cd to wherever you have stored the dashboard file
  6. Run command prompt "streamlit run ufc_dashboard.py"
