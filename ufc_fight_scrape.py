import scrapy
import random
import csv

class UFC_fight_scrape(scrapy.Spider):
    name = 'UFC_fight_scrape'
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"]

    custom_settings = {
        'LOG_LEVEL': 'CRITICAL'
    }

    processed_fights = set()
    fighter_stats = {}

    def __init__(self, *args, **kwargs):
        super(UFC_fight_scrape, self).__init__(*args, **kwargs)
        self.load_fighter_stats()

    def load_fighter_stats(self):
        try:
            with open('ufc_fighters.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.fighter_stats[row['Name'].strip()] = row
        except Exception as e:
            with open('ufc_fights_debug.txt', 'a') as file:
                file.write(f"Error loading fighter stats CSV: {e}\n")

    def parse(self, response):
        event_links = response.css('tbody a::attr(href)').getall()
        for link in event_links[1:]:
            yield response.follow(link, self.parse_event, dont_filter=True)

    def parse_event(self, response):
        indiv_fight_links = response.css('tbody.b-fight-details__table-body a::attr(href)').getall()
        for link in indiv_fight_links:
            if 'fight-details' in link:
                yield response.follow(link, self.parse_fight, dont_filter=True)

    def parse_fight(self, response):
        try:
            fight_url = response.url
            if fight_url in self.processed_fights:
                return

            self.processed_fights.add(fight_url)

            fighter1 = response.css('a.b-link.b-fight-details__person-link::text').getall()[0].strip()
            fighter_links = response.css('a.b-link.b-fight-details__person-link::attr(href)').getall()
            fighter2 = response.css('a.b-link.b-fight-details__person-link::text').getall()[1].strip()

            outcome = self.determine_winner(response)

            event = response.css('h2.b-content__title a::text').get().strip()

            with open('ufc_fights_debug.txt', 'a') as file:
                file.write(f"Processing: {event} - {fighter1} vs {fighter2} - Outcome: {outcome} - URL: {response.url}\n")

            fighter1_stats = self.fighter_stats.get(fighter1)
            fighter2_stats = self.fighter_stats.get(fighter2)

            if fighter1_stats and fighter2_stats:
                yield self.build_fight_output(response, fighter1, fighter2, event, outcome, fighter1_stats, fighter2_stats)
            else:
                yield response.follow(
                    fighter_links[0],
                    callback=self.parse_fighter,
                    meta={
                        'fighter1': fighter1,
                        'fighter2': fighter2,
                        'event': event,
                        'fighter2_link': fighter_links[1],
                        'fight_outcome': outcome,
                        'fighter1_stats': fighter1_stats,
                        'origin_fight_url': response.url
                    },
                    dont_filter=True
                )

        except Exception as e:
            with open('ufc__fights_debug.txt', 'a') as file:
                file.write(f"Error parsing fight page: {response.url} - {e}\n")

    def determine_winner(self, response):
        if 'green' in response.css('i').getall()[0]:
            if 'gray' in response.css('i').getall()[1]:
                return "fighter1"
        elif 'gray' in response.css('i').getall()[0]:
            if 'green' in response.css('i').getall()[1]:
                return "fighter2"
        else:
            return "draw"

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
            with open('ufc_fights_debug.txt', 'a') as file:
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

    def build_fight_output(self, response, fighter1, fighter2, event, outcome, fighter1_stats, fighter2_stats):
        output = {
            'fighter1': fighter1,
            'fighter2': fighter2,
            'event': event,
            'fight_outcome': outcome,
            'origin_fight_url': response.meta.get('origin_fight_url', response.url)
        }

        for prefix, stats in [('fighter1_', fighter1_stats), ('fighter2_', fighter2_stats)]:
            for key, value in stats.items():
                output[f'{prefix}{key}'] = value

        return output