# import libraries
import scrapy
import csv
import random

# set up scrapy spider
class UFC_upcoming_event_scrape(scrapy.Spider):

    name = 'UFC_upcoming_event_scrape' # spider name
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"] # url to start at (only one here since it contains all events)

    # set scraping settings
    custom_settings = {
        #'LOG_LEVEL': 'CRITICAL'                        # change amount of logs printed to command prompt
        'DOWNLOAD_DELAY': 1,                                        # download delay in seconds
        'RANDOMIZE_DOWNLOAD_DELAY': True,                   # randomize delay slightly
        'CONCURRENT_REQUESTS': 2                             # keep concurrent requests low
    }

    # initialize containters
    processed_fights = set() # a set is like a list that ensures uniqueness, but no indexing
    fighter_stats = {}

    # basically ensures that the UFC_upcoming_event_scrape class is setup, then tells it to move on to next thing
    def __init__(self, *args, **kwargs):
        super(UFC_upcoming_event_scrape, self).__init__(*args, **kwargs)
        self.load_fighter_stats()

    # load stats from the ufc_all_fighters csv that has already been scraped
    def load_fighter_stats(self):
        try:
            with open('ufc_all_fighters.csv', 'r') as csvfile: 
                reader = csv.DictReader(csvfile)                       # reads each row in CSV as its own dictionary, e.g. {height: value, weight: value}
                for row in reader:
                    self.fighter_stats[row['Name'].strip()] = row       # stores the reader dictionary information in fighter_stats
        except Exception as e:                                          # handles errors
            with open('ufc_upcoming_event_debug.txt', 'a') as file:
                file.write(f"Error loading fighter stats CSV: {e}\n")

    # find the top event (upcoming event) on the all_fights webpage
    def parse(self, response):                                                      # self is instance of scrapy class set up previously; response is webpage HTML content
        event_links = response.css('tbody a::attr(href)').getall()                  # get all elements matching these HTML tags
        for link in event_links[0:1]:                                               # only follow first one
            print("EVENT LINK:", link)
            yield response.follow(link, self.parse_event, dont_filter=True)         # go to the link and begin parse_event function; dont_filter tells scrapy that we can revisit the same page if needed (default is no)

    # get links of all matchups in event
    def parse_event(self, response):
        
        fight_rows = response.css('tr.b-fight-details__table-row')                  # Extract fight links from the <tr> elements
    
        for row in fight_rows:
            link = row.attrib.get('data-link')              # Extract link from 'data-link' attribute
            if not link:                                    # Fallback to extracting from 'onclick' attribute
                onclick = row.attrib.get('onclick')
                if onclick:
                    link = onclick.split("'")[1]

            if link and 'fight-details' in link:                                    # follow link if it is for fight
                print("FIGHT LINK:", link)
                yield response.follow(link, self.parse_fight, dont_filter=True)

    # get data for the specific fights
    def parse_fight(self, response):
        try:
            fight_url = response.url
            if fight_url in self.processed_fights:          # check if fight has already been processed
                return

            self.processed_fights.add(fight_url)            # add fight to list of processed fights if it hasn't already been

            fighter1 = response.css('a.b-link.b-fight-details__person-link::text').getall()[0].strip()      # find fighter 1
            fighter2 = response.css('a.b-link.b-fight-details__person-link::text').getall()[1].strip()      # find fighter 2
            fighter_links = response.css('a.b-link.b-fight-details__person-link::attr(href)').getall()      # gather links to fighters

            event = response.css('h2.b-content__title a::text').get().strip()                               # find event they're participating in

            # debug
            with open('ufc_upcoming_event_debug.txt', 'a') as file:
                file.write(f"Processing: {event} - {fighter1} vs {fighter2} - URL: {response.url}\n")

            # gather stats of the fighters from the ufc_all_fighters csv, if possible
            fighter1_stats = self.fighter_stats.get(fighter1)
            fighter2_stats = self.fighter_stats.get(fighter2)

            # if fighter stats present in csv, build final output; else, scrape their pages
            if fighter1_stats and fighter2_stats:
                yield self.build_fight_output(response, fighter1, fighter2, event, fighter1_stats, fighter2_stats)
            else:
                if not fighter1_stats and fighter2_stats:
                    with open('ufc_upcoming_event_debug.txt', 'a') as file:
                        file.write(f"No data for {fighter1}")
                elif fighter1_stats and not fighter2_stats:
                    with open('ufc_upcoming_event_debug.txt', 'a') as file:
                        file.write(f"No data for {fighter2}")
                else:
                    with open('ufc_upcoming_event_debug.txt', 'a') as file:
                        file.write(f"No data for either {fighter1} or {fighter2}")
                yield response.follow(
                    fighter_links[0],
                    callback=self.parse_fighter,
                    meta={
                        'fighter1': fighter1,
                        'fighter2': fighter2,
                        'event': event,
                        'fighter2_link': fighter_links[1],
                        'fighter1_stats': fighter1_stats,
                        'origin_fight_url': response.url
                    },
                    dont_filter=True
                )

        # debug
        except Exception as e:
            with open('ufc_upcoming_event_debug.txt', 'a') as file:
                file.write(f"Error parsing fight page: {response.url} - {e}\n")

    # get fighter stats if not available in ufc_all_fighters
    def parse_fighter(self, response):
        
        fighter_info = {}

        try:
            record = response.css("h2.b-content__title span.b-content__title-record::text").get()
            fighter_info['record'] = record.strip() if record else "N/A"

            data_response = [item.strip() for item in response.css("div.b-list__info-box ul.b-list__box-list li::text").getall()]

            keys = ['height', 'weight', 'reach', 'stance', 'DOB', 'SLpM', 'StrAcc', 'SApM', 'StrDef', 'TDAvg', 'TDAcc', 'TDDef', 'SubAvg']
            for i, key in enumerate(keys):
                fighter_info[key] = data_response[1 + i * 2] if len(data_response) > 1 + i * 2 else "N/A"

        except Exception as e:
            with open('ufc_upcoming_event_debug.txt', 'a') as file:
                file.write(f"Error parsing fighter page: {response.url} - {e}\n")

        if response.meta['fighter1_stats'] is None:
            yield scrapy.Request(
                response.meta['fighter2_link'],
                callback=self.parse_fighter,
                meta=response.meta | {'fighter1_stats': fighter_info},
                dont_filter=True
            )
        else:
            yield self.build_fight_output(response, response.meta['fighter1'], response.meta['fighter2'], response.meta['event'], response.meta['fight_outcome'], response.meta['fighter1_stats'], fighter_info)

    def build_fight_output(self, response, fighter1, fighter2, event, fighter1_stats, fighter2_stats):
        output = {
            'fighter1': fighter1,
            'fighter2': fighter2,
            'event': event,
            #'fight_outcome': outcome,
            'origin_fight_url': response.meta.get('origin_fight_url', response.url)
        }

        for prefix, stats in [('fighter1_', fighter1_stats), ('fighter2_', fighter2_stats)]:
            for key, value in stats.items():
                output[f'{prefix}{key}'] = value

        return output