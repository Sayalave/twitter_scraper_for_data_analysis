#!/usr/bin/env python

from scraper.scrape import Scrape
from scraper.transform import Transform
from scraper.visualize import Visualize
import argparse
import pandas as pd
import os


class Execute(object):
    def __init__(self):
        ap = argparse.ArgumentParser()
        ap.add_argument("-keyword", required=True)
        ap.add_argument("-start", required=True)
        ap.add_argument("-end", required=True)
        ap.add_argument("-keyword_type", required=True)
        ap.add_argument("-keys_path", required=True)
        ap.add_argument("--delay", required=False, default='1')
        ap.add_argument("--chromedriver_path", required=False,
                        default='/usr/local/bin/chromedriver')
        self.args = vars(ap.parse_args())
        self.path_raw_data = f"{os.path.expanduser('data')}/" \
                             f"{self.args['keyword']}/.raw_data/df_raw.csv"

    def scrape(self):
        scraper = Scrape(
            keyword=self.args['keyword'],
            start=self.args['start'],
            end=self.args['end'],
            keyword_type=self.args['keyword_type'],
            keys_path=self.args['keys_path'],
            delay=self.args['delay'],
            chromedriver_path=self.args['chromedriver_path']
        )
        scraper.extract_all_ids()
        scraper.get_metadata()

    def transform(self):
        if pd.read_csv(self.path_raw_data).empty:
            return 'There is no raw data to transform'

        transform = Transform(
            keyword=self.args['keyword']
        )

        transform.get_df_clean_data()
        transform.get_df_grouped_date()
        transform.get_df_key_topics()
        transform.get_df_most_mentioned_users()
        transform.get_df_most_mentioned_hashtags()
        transform.get_df_most_active_users()
        transform.get_df_most_retweeted_users()
        transform.get_df_users_by_followers()
        transform.get_df_cohashtags_matrix()
        transform.get_df_tweets_sorted_by_retweets()

    def visualize(self):
        if pd.read_csv(self.path_raw_data).empty:
            return 'There is no raw data to transform'

        visualize = Visualize(
            keyword=self.args['keyword']
        )

        visualize.visualize_grouped_date()
        visualize.visualize_key_topics()
        visualize.visualize_most_mentioned_users()
        visualize.visualize_most_mentioned_hashtags()
        visualize.visualize_most_active_users()
        visualize.visualize_most_retweeted_users()
        visualize.visualize_users_by_followers()

    def execute_all(self):
        self.scrape()
        self.transform()
        self.visualize()


if __name__ == '__main__':
    Execute().execute_all()
