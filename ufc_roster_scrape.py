import scrapy

class UFC_roster_scrape(scrapy.Spider):
    name = 'ufc_roster_scrape'
    start_urls = ['http://ufcstats.com/statistics/fighters?char=a&page=all',
                  'http://ufcstats.com/statistics/fighters?char=b&page=all',
                  'http://ufcstats.com/statistics/fighters?char=c&page=all',
                  'http://ufcstats.com/statistics/fighters?char=d&page=all',
                  'http://ufcstats.com/statistics/fighters?char=e&page=all',
                  'http://ufcstats.com/statistics/fighters?char=f&page=all',
                  'http://ufcstats.com/statistics/fighters?char=g&page=all',
                  'http://ufcstats.com/statistics/fighters?char=h&page=all',
                  'http://ufcstats.com/statistics/fighters?char=i&page=all',
                  'http://ufcstats.com/statistics/fighters?char=j&page=all',
                  'http://ufcstats.com/statistics/fighters?char=k&page=all',
                  'http://ufcstats.com/statistics/fighters?char=l&page=all',
                  'http://ufcstats.com/statistics/fighters?char=m&page=all',
                  'http://ufcstats.com/statistics/fighters?char=n&page=all',
                  'http://ufcstats.com/statistics/fighters?char=o&page=all',
                  'http://ufcstats.com/statistics/fighters?char=p&page=all',
                  'http://ufcstats.com/statistics/fighters?char=q&page=all',
                  'http://ufcstats.com/statistics/fighters?char=r&page=all',
                  'http://ufcstats.com/statistics/fighters?char=s&page=all',
                  'http://ufcstats.com/statistics/fighters?char=t&page=all',
                  'http://ufcstats.com/statistics/fighters?char=u&page=all',
                  'http://ufcstats.com/statistics/fighters?char=v&page=all',
                  'http://ufcstats.com/statistics/fighters?char=w&page=all',
                  'http://ufcstats.com/statistics/fighters?char=x&page=all',
                  'http://ufcstats.com/statistics/fighters?char=y&page=all',
                  'http://ufcstats.com/statistics/fighters?char=z&page=all',]

    def parse(self, response):
        # Get all fighter links on the current page
        fighter_links = response.css('td.b-statistics__table-col a::attr(href)').getall()
        if type(fighter_links) == list:
            for link in fighter_links:
                yield response.follow(link, self.parse_fighter)
        else:
            yield response.follow(fighter_links, self.parse_fighter)

    def parse_fighter(self, response):
        fighter_info = {}

        # Extract Name
        fighter_info['Name'] = response.css("h2.b-content__title span.b-content__title-highlight::text").get().strip()

        # Extract Nickname
        nickname = response.css("p.b-content__Nickname::text").get()
        fighter_info['Nickname'] = nickname.strip() if nickname else "."

        # Extract Record
        record = response.css("h2.b-content__title span.b-content__title-record::text").get()
        fighter_info['Record'] = record.strip() if record else "."

        # Extract Stats
        data_response = [item.strip() for item in response.css("div.b-list__info-box ul.b-list__box-list li::text").getall()]
        label_response = [item.strip() for item in response.css("div.b-list__info-box ul.b-list__box-list i::text").getall()]
        fighter_info['Height'] = data_response[1]
        fighter_info['Weight'] = data_response[3]
        fighter_info['Reach'] = data_response[5]
        fighter_info['Stance'] = data_response[7]
        fighter_info['DOB'] = data_response[9]
        fighter_info['SLpM'] = data_response[11]
        fighter_info['StrAcc'] = data_response[13]
        fighter_info['SApM'] = data_response[15]
        fighter_info['StrDef'] = data_response[17]
        fighter_info['TDAvg'] = data_response[21]
        fighter_info['TDAcc'] = data_response[23]
        fighter_info['TDDef'] = data_response[25]
        fighter_info['SubAvg'] = data_response[27]

        # Yield the fighter information
        yield fighter_info