import datetime
import os
import tweepy
from scraper.save import Save
from selenium import webdriver
from time import sleep
import pickle5 as pickle
import json
import pandas as pd


class Scrape(object):

    def __init__(self, keyword, start, end, keyword_type, keys_path,
                 delay=10, chromedriver_path='/usr/local/bin/chromedriver',
                 include_retweets='false'):
        """
        Collects all tweet ids published in a given time frame that include a
        given keyword or hashtag, or published by a given account, depending
        on the parameter keyword_type. For each day, the class saves a pickle
        file and then for the next day it loads and update that same file.
        If the program crashes, this behaviour helps to pick up the collection
        of ids on the date when the collection crashed. The function saves the
        ids as a pickle file in the given path.

        Args:
            - keyword (str): hashtag, account, or query. If it's query and more
                than one word is used, white spaces should be passed as
                underscores. If it's a hashtag, it should not include '#'.
            - start (str): date when the data collection starts.
                Format: 'YYYY-MM-DD'
            - end (str): date when the data collection ends.
                Format: 'YYYY-MM-DD'
            - keyword_type (str): it can be 'hashtag', 'query', or 'account'.
            - save_path (str): path where the program will save the Twitter ids.
        """
        # Set URL parameters
        self.start = start
        self.end = end
        self.keyword = keyword.lower()
        self.keyword_type = keyword_type.lower()
        self.delay = int(delay)
        self.save_path = os.path.expanduser('data')
        self.chromedriver_path = chromedriver_path
        # noinspection SpellCheckingInspection
        self.include_retweets = 'include%3Aretweets' \
            if include_retweets.lower() == 'true' else ''

        # Get twitter keys
        with open(keys_path, 'r') as file:
            keys = json.load(file)
        self.consumer_key = keys['consumer_key']
        self.consumer_secret = keys['consumer_secret']
        self.access_token = keys['access_token']
        self.access_token_secret = keys['access_token_secret']

        # Create a new directory to save raw data if it doesn't exist
        self.path_raw_data = f"{self.save_path}/{self.keyword}/raw_data"
        if not os.path.exists(self.path_raw_data):
            os.makedirs(self.path_raw_data)

    def get_metadata(self):
        """
        Gets metadata for all of the Twitter ids extracted by extract_all_ids.

        Args:
            - None, but it uses attributes from initializing the class.
        Returns:
            - None, but is saves
        """
        # Load the list of tweet ids
        with open(f'{self.path_raw_data}/ids.pickle', 'rb') as handle:
            list_of_lists = pickle.load(handle)
            # Flatten list and dedup again just to make sure if it is not null
            if not list_of_lists:
                return "There are no tweet ids to extract metadata"
            else:
                # "not sublist" returns True if list is empty, so we use "not
                # not sublist" to return True if list is not empty
                ids = list(set([item for sublist in list_of_lists
                                if not not sublist for item in sublist]))

        print('Total ids to be processed: {}'.format(len(ids)))

        # Set credentials
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.access_token, self.access_token_secret)
        api = tweepy.API(auth)

        # Set batch list to only call the API once every 100 ids
        floor_batch_lst = list(range(0, len(ids), 100))
        total_ids = len(ids)
        batch_list = [(i, i+100) if i+100 < total_ids else (i, total_ids)
                      for i in floor_batch_lst]

        all_data = []
        for floor, ceil in batch_list:
            print(f'Currently getting {floor} - {ceil} ids out of {total_ids}')
            ids_batch = ids[floor:ceil]
            response = api.statuses_lookup(ids_batch, tweet_mode='extended')
            # Getting tweet in JSON format uses private attribute and may
            # break in the future
            tweets = [dict(tweet._json) for tweet in response]
            all_data += tweets
        print('Metadata collection complete!')

        # Metadata comes in JSON format, so we convert it to CSV and also drop
        # observations without tweet id
        df = pd.DataFrame(all_data).dropna(subset=['entities'])
        save_data = Save(
            df, self.save_path, self.keyword, 'raw_data', 'df_raw', False)
        save_data.save_data()

    def extract_all_ids(self):
        # Convert dates to datetime to manipulate them more easily
        start_date = datetime.datetime.strptime(self.start, '%Y-%m-%d')
        final_date = datetime.datetime.strptime(self.end, '%Y-%m-%d')

        # Iterate over each day between start_date and end_date
        ids_pickle_path = f"{self.path_raw_data}/ids.pickle"
        while str(start_date.date()) != str(final_date.date()):
            # Load previously saved ids if available. If note, start from zero
            if os.path.exists(ids_pickle_path):
                with open(ids_pickle_path, 'rb') as handle:
                    ids = pickle.load(handle)
            else:
                ids = []
            # Get ids
            new_ids = self._extract_ids_from_one_day(str(start_date.date()))
            # Append new ids found
            ids.append(new_ids)
            # Update pickle file with new ids
            with open(f'{self.path_raw_data}/ids.pickle', 'wb') as handle:
                pickle.dump(ids, handle, protocol=pickle.HIGHEST_PROTOCOL)
            # Increment start_date by one day
            start_date += datetime.timedelta(days=1)

    def _extract_ids_from_one_day(self, start_date):
        """
        Get ids of all tweets posted on a given date defined by the start_date
        parameter.
        Args:
            - start_date (str): The date of interest to extract data.
                Format: 'YYYY-MM-DD'
        Returns:
            - ids (list): The list of ids published on the start_date.
        """
        # Generate URL using the keyword and the lower and upper date bounds
        until = (datetime.datetime.strptime(start_date, '%Y-%m-%d') +
                 datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        url = self._form_url(keyword_type=self.keyword_type, since=start_date,
                             until=until, keyword=self.keyword)
        print(f"Getting data from {start_date} until {until} for "
              f"keyword {self.keyword} with URL...\n{url}")

        # Start session, open URL, and give it a few seconds to load
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(executable_path=self.chromedriver_path,
                                  chrome_options=chrome_options)
        driver.get(url)
        sleep(self.delay)

        # Extract the ids of the first tweets. Also stop if no tweet is found
        # that day. The Selenium object is found by looking for all href tags
        # that contain the string '/status/'
        ids = driver.find_elements_by_xpath('//a[contains(@href,"/status/")]')
        ids = [self._parse_ids(element) for element in ids]
        if len(ids) == 0:
            print(f"There were no tweets posted by/with {self.keyword} "
                  f"on {start_date}")

            # Close driver
            driver.quit()
            return

        # Scroll down to see if there were more tweets published that day
        print('Scrolling down to get more tweets')
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(self.delay)
        next_ids = driver.find_elements_by_xpath(
            '//a[contains(@href,"/status/")]')
        next_ids = [self._parse_ids(element) for element in next_ids]

        # Check if we got any new tweet ids after scrolling down. If we didn't
        # continue scrolling down to until we don't get any new tweet id
        new_tweets = set(next_ids) - set(ids)
        while len(new_tweets) > 0:
            # If we got new tweet ids, add them to the list
            ids.extend(next_ids)
            # Scroll down to continue checking if we can get additional
            # tweet ids
            print('Scrolling down to get more tweets')
            driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);')
            sleep(self.delay)
            next_ids = driver.find_elements_by_xpath(
                '//a[contains(@href,"/status/")]')
            next_ids = [self._parse_ids(element) for element in next_ids]
            new_tweets = set(next_ids) - set(ids)

        # Make sure we don't have duplicated tweet ids
        ids = list(set(ids))
        print(f"We found {len(ids)} for the keyword {self.keyword} "
              f"from {start_date} until {until} \n")

        # Close driver
        driver.quit()

        return ids

    def _form_url(self, keyword_type, since, until, keyword):
        """
        Generate the URL to extract all tweets posted with/by the given
        keyword for a single date. The URL adapts if the keyword is a
        query, hashtag, or account.
        Args:
            - since (str): The date of interest to extract data.
                Format: 'YYYY-MM-DD'
            - until (str): The date of interest to extract data plus one day.
                It serves as upper bound for the query. Format: 'YYYY-MM-DD'
            - keyword (str): The keyword used for the query.
        Returns:
            - url (str): The URL for the query.
        """
        if keyword_type == 'account':
            return f'https://twitter.com/search?f=tweets&vertical=default' \
                   f'&q=(from%3A{keyword})%20since%3A{since}' \
                   f'%20until%3A{until}{self.include_retweets}&src=typed_query'
        elif keyword_type == 'hashtag':
            return f'https://twitter.com/search?f=tweets&vertical=default' \
                   f'&q=(%23{keyword})%20since%3A{since}' \
                   f'%20until%3A{until}{self.include_retweets}&src=typed_query'
        elif keyword_type == 'query':
            keyword = keyword.replace("_", '%20')
            return f'https://twitter.com/search?f=tweets&vertical=default' \
                   f'&q={keyword}%20since%3A{since}' \
                   f'%20until%3A{until}{self.include_retweets}&src=typed_query'
        else:
            return print('Only user, hashtag or keyword data can be True')

    @staticmethod
    def _parse_ids(element):
        # noinspection SpellCheckingInspection
        """
                Extracts the tweet id from a Selenium WebElement that contains an href
                tag with the URL to a unique tweet. The URL's format is
                https://twitter.com/{USERNAME}/status/TWITTERID. If the URL has an
                additional '/' after the tweet id, it means that the URL includes
                pictures or something else, so we continue cleaning the URL until we
                get the id.
                Args:
                    + element (selenium.WebElement): A Selenium object found by looking for all href tags
                      that contain the string '/status/'.
                Returns:
                    + tweet_id (str): The Twitter id extracted from the href tag.
                """
        tweet_id = element.get_attribute('href').split('status/')[-1]
        tweet_id = tweet_id.split('/')[0] \
            if len(tweet_id.split('/')) > 1 else tweet_id
        return tweet_id
