import pandas as pd
import os
from ast import literal_eval
import unidecode
import string
import nltk
import sklearn
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from scraper.save import Save


class Transform(object):

    def __init__(self, keyword):
        self.keyword = keyword
        self.save_path = 'data'
        self.path_raw_data = f'{os.path.expanduser(self.save_path)}/{keyword}/' \
                             f'raw_data/df_raw.csv'
        self.clean_data_path = f'{os.path.expanduser(self.save_path)}/' \
                               f'{self.keyword}/clean_data/df_clean.csv'
        self.mapping_months = {1: 'JAN', 2: 'FEB', 3: 'MAR', 4: 'APR',
                               5: 'MAY', 6: 'JUN', 7: 'JUL', 8: 'AUG',
                               9: 'SEP', 10: 'OCT', 11: 'NOV', 12: 'DEC'}
        self.mapping_weekdays = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
                                 3: 'Thursday', 4: 'Friday', 5: 'Saturday',
                                 6: 'Sunday'}

    @staticmethod
    def _string_has_digits(word):
        return any(char.isdigit() for char in word)

    @staticmethod
    def _func_to_json(row):
        return literal_eval(row) if pd.notnull(row) else None

    def _text_cleaner(self, original_text):
        # Remove @ mentions and # hashtags before any cleaning because we
        # keep track of those in other fields and we don't want them to
        # count as words used in the text of the tweet
        text = [word for word in original_text.split()
                if not word.startswith('@') and not word.startswith('#')]

        # Cast back to string before cleaning and convert to lower case
        text = str(text).lower()

        # Remove punctuations from string
        punctuation = (
                string.punctuation + '¿').replace("#", "").replace("@", "")
        translator = str.maketrans(punctuation, ' ' * len(punctuation))
        text = text.translate(translator)

        # Tokenize text
        text = nltk.word_tokenize(str(text))
        text = [word for word in text
                if not word.startswith('@') or not word.startswith('#')]

        # Generate list of words that should be removed
        words_ignore = ['http', 'www', 'com', 'ly', 'bit', 'u', 'li', 'ht',
                        '’', 'rt', 'co', '...', 'https', "'", '"', ",", " ",
                        "", "gt"]
        words_ignore = \
            words_ignore + nltk.corpus.stopwords.words('spanish') \
            + nltk.corpus.stopwords.words('english') \
            + [word for word in list(string.ascii_lowercase)]
        text = [unidecode.unidecode(word) for word in text]
        text = [word for word in text if word not in words_ignore]

        # Remove words with digits
        text = [word for word in text if not self._string_has_digits(word)]

        # Join words with space
        text = ' '.join(word for word in text)

        return text

    def get_df_clean_data(self):
        df = pd.read_csv(self.path_raw_data)

        # Cast timestamp as datetime using EST as timezone. The column ts refers
        # to the timestamp when the tweet was published
        df['ts'] = pd.to_datetime(df['created_at'],
                                  utc=True,
                                  errors='coerce').dt.tz_convert('US/Eastern')

        # The raw data returns JSON strings, but when those JSON strings
        # are loaded to Pandas they are parsed only as strings
        cols_to_json = ['coordinates', 'entities', 'quoted_status',
                        'user', 'place']
        for col in cols_to_json:
            if col in df.columns:
                df[col] = df[col].apply(self._func_to_json)

        # Sometimes scraping for tweet ids returns noise records and we want
        # to make sure we don't have any records with null ids. We also want
        # to cast the ids as string to remove trailing zeros
        df['id'] = pd.to_numeric(df.id, errors='coerce')
        df = df[df.id.notnull()]
        df['id'] = df.id.astype(int).astype(str)

        # Cast boolean attributes
        df['is_quote'] = df['is_quote_status'].astype(bool)
        df['is_truncated'] = df['truncated'].astype(bool)

        # Process timestamp
        df['date'] = df['ts'].apply(lambda x: x.date())
        df['year'] = df['ts'].apply(lambda x: x.year)
        df['month_number'] = df['ts'].apply(lambda x: x.month)
        df['month_name'] = df['month_number'].map(self.mapping_months)
        df['day'] = df['ts'].apply(lambda x: x.day)
        df['weekday_num'] = df['ts'].apply(lambda x: x.dayofweek)
        df['date_weekday'] = df['weekday_num'].map(self.mapping_weekdays)
        df['time'] = df['ts'].apply(lambda x: x.time())
        df['hour'] = df['time'].apply(lambda x: x.hour)

        # Process location if available
        df['lon'] = df['coordinates'].apply(
            lambda x: x['coordinates'][0] if x is not None else None)
        df['lat'] = df['coordinates'].apply(
            lambda x: x['coordinates'][1] if x is not None else None)

        # Get the URL of each tweet
        df['url'] = df['id'].apply(
            lambda x: "https://twitter.com/i/web/status/" + str(x))

        # Process entities
        df['hashtags'] = df['entities'].apply(
            lambda x: ['#' + hashtag['text'].lower() for hashtag in
                       x['hashtags']] if pd.notnull(x) else '')

        df['user_mentions'] = df['entities'].apply(
            lambda x: ['@' + user['screen_name'].lower() for user in
                       x['user_mentions']] if pd.notnull(x) else '')

        # Process in_reply_to_screen_name
        df['reply_to_user'] = df['in_reply_to_screen_name'].apply(
            lambda x: '@' + x if pd.notnull(x) else '')

        # Process language
        df['lang'] = df['lang'].apply(
            lambda x: 'english'
            if x == 'en' else ('spanish' if x == 'sp' else 'other'))

        # Process place
        df['country'] = df['place'].apply(
            lambda x: x['country_code'] if pd.notnull(x) else np.NaN)
        df['city_state'] = df['place'].apply(
            lambda x: x['full_name'] if pd.notnull(x) else np.NaN)
        df['city'] = df['place'].apply(
            lambda x: x['name'] if pd.notnull(x) else np.NaN)

        # Process information from the users who published each tweet
        df['user_screen_name'] = df['user'].apply(
            lambda x: x['screen_name'].lower() if pd.notnull(x) else np.NaN)
        df['user_followers_count'] = df['user'].apply(
            lambda x: x['followers_count'] if pd.notnull(x) else 0).astype(int)
        df['user_friends_count'] = df['user'].apply(
            lambda x: x['friends_count'] if pd.notnull(x) else 0).astype(int)
        df['user_statuses_count'] = df['user'].apply(
            lambda x: x['statuses_count'] if pd.notnull(x) else 0).astype(int)
        df['user_location'] = df['user'].apply(
            lambda x: x['location'] if pd.notnull(x) else np.NaN)
        df['user_ts'] = pd.to_datetime(
            df['user'].apply(
                lambda x: x['created_at'] if pd.notnull(x) else np.NaN),
            utc=True).dt.tz_convert('US/Eastern')

        # Process quoted status, which indicates whether the tweet was
        # a retweet or quote
        if 'quoted_status' in df.columns:
            df['retweeted_dummy'] = df['quoted_status'].astype(bool)
            df['retweeted_user_screen_name'] = df['quoted_status'].apply(
                lambda x: x['user']['screen_name']
                if pd.notnull(x) else np.NaN)
            df['retweeted_retweet_count'] = df['quoted_status'].apply(
                lambda x: x['retweet_count']
                if pd.notnull(x) else np.NaN)
            df['retweeted_user_followers_count'] = df['quoted_status'].apply(
                lambda x: x['user']['followers_count']
                if pd.notnull(x) else np.NaN)
            df['retweeted_user_friends_count'] = df['quoted_status'].apply(
                lambda x: x['user']['friends_count']
                if pd.notnull(x) else np.NaN)
            df['retweeted_user_statuses_count'] = df['quoted_status'].apply(
                lambda x: x['user']['statuses_count']
                if pd.notnull(x) else np.NaN)
            df['retweeted_user_location'] = df['quoted_status'].apply(
                lambda x: x['user']['location']
                if pd.notnull(x) else np.NaN)

        # Process text
        df['text_clean'] = df['full_text'].apply(
            lambda x: self._text_cleaner(x))

        # Drop unnecessary columns
        # noinspection SpellCheckingInspection
        unnecessary_cols = [
            'contributors', 'favorited', 'geo', 'date_time', 'tokenize',
            'date_weekday_num', 'in_reply_to_screen_name',
            'in_reply_to_status_id', 'in_reply_to_status_id_str',
            'in_reply_to_user_id', 'in_reply_to_user_id_str',
            'is_quote_status', 'lang', 'place', 'possibly_sensitive',
            'quoted_status_id', 'quoted_status_id_str', 'retweeted', 'source',
            'truncated', 'user', 'entities', 'extended_entities',
            'coordinates', 'id_str'
        ]
        df.drop(unnecessary_cols, axis=1, inplace=True, errors='ignore')

        save_data = Save(
            df, self.save_path, self.keyword, 'clean_data', 'df_clean', True)
        save_data.save_data()

        return df

    def get_df_grouped_date(self):
        # Load cleaned data
        clean_data = pd.read_csv(self.clean_data_path)

        # Group by date and get sums and counts
        df = clean_data.groupby('date') \
            .agg({'retweet_count': 'sum',
                  'favorite_count': 'sum',
                  'date': 'count'}) \
            .rename({'date': 'tweets_published'}, axis=1) \
            .reset_index()

        # Process date fields
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month.map(self.mapping_months)
        df['year'] = df['date'].dt.year

        # Save cleaned data
        save_data = Save(
            df, self.save_path, self.keyword, 'grouped_date',
            'grouped_date', True)
        save_data.save_data()

        return df

    def get_df_key_topics(self, num_tfidf_feat=40):
        # Load cleaned data
        df = pd.read_csv(self.clean_data_path)

        # Create list of stop_words for the count vectorizer
        stop_words = nltk.corpus.stopwords.words('spanish') \
            + nltk.corpus.stopwords.words('english')

        # Instantiate count vectorizer
        count_vectorizer = sklearn.feature_extraction.text.CountVectorizer(
            min_df=1, ngram_range=(1, 2), stop_words=stop_words)
        tfidf = sklearn.feature_extraction.text.TfidfTransformer()

        # Cleaning tweets' text can generate nulls, so we make them empty
        # strings for the vectorizer
        df.text_clean.fillna(' ', inplace=True)

        # Fit count vectorizer to get counts and generate tfidf features
        count_vectorizer.fit(df.text_clean)
        counts = count_vectorizer.transform(df.text_clean)
        transformed_weights = tfidf.fit_transform(counts)
        weights = np.asarray(
            transformed_weights.mean(axis=0)).ravel().tolist()
        weights = pd.DataFrame(
            {'topic': count_vectorizer.get_feature_names(), 'weight': weights})
        df_tfidf = weights.sort_values('weight', ascending=False)

        # Get normalized weights between 0 and 1
        df_tfidf['weight_normalized'] = MinMaxScaler().fit_transform(
            np.array(df_tfidf.weight).reshape(-1, 1)) * 100

        # Only return the top x tfidf features
        df_tfidf = df_tfidf.head(num_tfidf_feat)

        # Save data
        save_data = Save(
            df_tfidf, self.save_path, self.keyword,
            'key_topics', 'key_topics', True)
        save_data.save_data()

        return df_tfidf

    def get_df_most_mentioned_users(self):
        # Load cleaned data and return if there were no users mentioned
        df = pd.read_csv(self.clean_data_path)

        # Flatten nested list of users mentioned per tweet
        df['user_mentions'] = df['user_mentions'].apply(
            lambda x: literal_eval(x) if pd.notnull(x) else '')
        users = [user.replace('@', '')
                 for sublist in df['user_mentions'].values for user in sublist]
        users_empty = True if len(users) == 0 else False
        if users_empty:
            return

        # Count number of times each user was mentioned
        df = pd.DataFrame({'user': users}) \
            .user.value_counts() \
            .reset_index() \
            .rename({'index': 'user', 'user': 'mentions_count'}, axis=1) \
            .sort_values('mentions_count', ascending=False)
        df['link'] = 'https://twitter.com/' + df['user']

        save_data = Save(
            df, self.save_path, self.keyword, 'most_mentioned_users',
            'most_mentioned_users', True)
        save_data.save_data()

        return df

    def get_hashtags_df(self):
        # Load cleaned data
        df = pd.read_csv(self.clean_data_path)
        # Flatten nested list of hashtags mentioned per tweet and
        # return empty data frame if there were no hashtags captured
        df['hashtags'] = df['hashtags'].apply(
            lambda x: literal_eval(x) if pd.notnull(x) else '')
        hashtags = [
            h for sublist in df['hashtags'].values for h in sublist]
        df = pd.DataFrame(hashtags, columns=['hashtags'])

        hashtags_empty = True if len(hashtags) == 0 else False
        if hashtags_empty:
            return pd.DataFrame()
        else:
            return df

    def get_df_most_mentioned_hashtags(self):
        # Load hashtags data
        df = self.get_hashtags_df()
        if df.empty:
            return

        # Count number of times each hashtag was mentioned
        df = df.hashtags.astype(str).value_counts() \
               .reset_index() \
               .rename({'index': 'hashtags', 'hashtags': 'hashtags_count'},
                       axis=1) \
               .sort_values('hashtags_count', ascending=False)

        # Remove from counts nulls and empty lists of hashtags
        df = df[
            (df.astype(str)['hashtags'] != '[]') &
            (df.hashtags != np.NaN) &
            (df.hashtags != '')
        ]

        save_data = Save(
            df, self.save_path, self.keyword, 'most_mentioned_hashtags',
            'most_mentioned_hashtags', True)
        save_data.save_data()

        return df

    def get_df_most_active_users(self):
        df = pd.read_csv(self.clean_data_path) \
            .user_screen_name.value_counts() \
            .reset_index() \
            .rename({'index': 'user', 'user_screen_name': 'tweets_published'},
                    axis=1) \
            .sort_values('tweets_published', ascending=False)
        df['link'] = 'https://twitter.com/' + df['user']

        save_data = Save(
            df, self.save_path, self.keyword,
            'most_active_users', 'most_active_users', True)
        save_data.save_data()

        return df

    def get_df_most_retweeted_users(self):
        # Load cleaned data
        df_clean = pd.read_csv(self.clean_data_path)

        # Return if no tweet was a retweet
        if 'retweeted_user_screen_name' not in df_clean.columns:
            return

        # Count how many times each retweeted user was retweeted and also
        # add the number of followers per user that was retweeted
        df = df_clean[df_clean.retweeted_user_screen_name.notnull()]
        df = df.groupby('retweeted_user_screen_name', as_index=False) \
            .id.count() \
            .merge(df_clean[['retweeted_user_screen_name',
                             'retweeted_user_followers_count']],
                   on='retweeted_user_screen_name', how='inner') \
            .rename({'retweeted_user_screen_name': 'user',
                     'id': 'count_retweets',
                     'retweeted_user_followers_count': 'count_followers'},
                    axis=1) \
            .drop_duplicates()
        df['link'] = 'https://twitter.com/' + df['user']
        df = df.groupby('user').max().reset_index()\
            .sort_values('count_retweets', ascending=False) \

        save_data = Save(
            df, self.save_path, self.keyword, 'most_retweeted_users',
            'most_retweeted_users', True)
        save_data.save_data()

        return df

    def get_df_users_by_followers(self):
        # Load cleaned data
        df = pd.read_csv(self.clean_data_path,
                         usecols=['user_screen_name', 'user_followers_count',
                                  'user_friends_count',
                                  'user_statuses_count']) \
            .rename({'user_screen_name': 'user',
                     'user_followers_count': 'count_followers',
                     'user_friends_count': 'count_following',
                     'user_statuses_count': 'count_tweets_published_all_time'},
                    axis=1) \
            .sort_values('count_followers', ascending=False) \
            .drop_duplicates()
        df['link'] = 'https://twitter.com/' + df['user']
        df = df.groupby('user').max().reset_index()\
            .sort_values('count_followers', ascending=False)

        save_data = Save(
            df, self.save_path, self.keyword, 'users_by_followers',
            'users_by_followers', True)
        save_data.save_data()

        return df

    def get_df_cohashtags_matrix(self):
        # Load hashtags data
        df = self.get_hashtags_df()
        if df.empty:
            return

        # Get one hot encoding of hashtags per tweet
        one_hot_encoding = pd.get_dummies(
            df.hashtags.apply(pd.Series).stack()).sum(level=0).astype(int)
        # Get co occurrence matrix by multiplying the one hot encoding by
        # its transpose
        df = one_hot_encoding.T.dot(one_hot_encoding)

        save_data = Save(
            df, self.save_path, self.keyword, 'co_hashtags_matrix',
            'co_hashtags_matrix', True)
        save_data.save_data()

        return df

    def get_df_tweets_sorted_by_retweets(self):
        df = pd.read_csv(self.clean_data_path) \
            .sort_values('retweet_count', ascending=False) \
            .reset_index(drop=True)
        df['link'] = 'https://twitter.com/' + df['user_screen_name']
        df = df[['user_screen_name', 'link', 'date', 'year', 'month_name',
                 'day', 'full_text', 'retweet_count', 'favorite_count',
                 'user_followers_count', 'user_friends_count',
                 'user_statuses_count']]

        save_data = Save(
            df, self.save_path, self.keyword, 'tweets_sorted_by_retweets',
            'tweets_sorted_by_retweets', True)
        save_data.save_data()

        return df
