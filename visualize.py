from highcharts import Highchart
import pandas as pd
import os


# noinspection DuplicatedCode
class Visualize(object):

    def __init__(self, keyword, save_path):
        self.keyword = keyword
        self.save_path = save_path
        self.months_order = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                             "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    @staticmethod
    def func_save_html(path, html_str):
        return open(path, "w").write(html_str)

    def visualize_grouped_date(self):
        df_path = f'{os.path.expanduser(self.save_path)}/{self.keyword}/' \
                  f'grouped_date/grouped_date.csv'
        df = pd.read_csv(df_path)

        # Order month category
        df['month'] = df['month'].astype('category') \
            .cat.add_categories([month for month in self.months_order
                                 if month not in df.month.unique().tolist()])
        df.set_index(['year', 'month'], inplace=True)

        options = {
            'title': {'text': f'Count of tweets, retweets, and favorites by '
                              f'month for {self.keyword}'
                              f'from {df.index.min()[0]}-{df.index.min()[1]} '
                              f'to {df.index.max()[0]}-{df.index.max()[1]}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.index.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'Date (Year, Month)',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Count',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}'}
                      },
            'plotOptions': {'column': {'stacking': 'normal'}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.retweet_count.values.tolist(), 'line',
                       'Retweets count', color='#1998CB')
        h.add_data_set(df.favorite_count.values.tolist(), 'line',
                       'Favorites count', color='#F0CD13')
        h.add_data_set(df.tweets_published.values.tolist(), 'line',
                       'Tweets published count', color='#EC3C37')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}/' \
                          f'{self.keyword}/grouped_date/grouped_date.html'
        self.func_save_html(save_chart_path, h.htmlcontent)

    def visualize_key_topics(self):
        df_path = f'{os.path.expanduser(self.save_path)}/{self.keyword}/' \
                  f'key_topics/key_topics.csv'
        df = pd.read_csv(df_path)

        options = {
            'title': {'text': f'Top {df.shape[0]} key topics '
                              f'for {self.keyword}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.topic.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'Topic',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Importance in percentage (%)',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}%'},
                      'min': 0,
                      'max': df.weight_normalized.max()
                      },
            'plotOptions': {'series': {'showInLegend': False}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.weight_normalized.values.tolist(), 'bar',
                       'Retweets count', color='#1998CB')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}/' \
                          f'{self.keyword}/key_topics/key_topics.html'
        self.func_save_html(save_chart_path, h.htmlcontent)

    def visualize_most_mentioned_users(self):
        df_path = f'{os.path.expanduser(self.save_path)}/{self.keyword}/' \
                  f'most_mentioned_users/most_mentioned_users.csv'
        df = pd.read_csv(df_path)
        top_mentions = 20
        df = df.head(top_mentions)

        options = {
            'title': {'text': f'Top {top_mentions} most mentioned users '
                              f'for {self.keyword}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.user.values.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'User mentioned',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Count of mentions',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}'}
                      },
            'plotOptions': {'series': {'showInLegend': False}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.mentions_count.values.tolist(), 'bar',
                       'Mentions count', color='#1998CB')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}' \
                          f'/{self.keyword}/most_mentioned_users/' \
                          f'most_mentioned_users.html'
        self.func_save_html(save_chart_path, h.htmlcontent)

    def visualize_most_mentioned_hashtags(self):
        df_path = f'{os.path.expanduser(self.save_path)}/{self.keyword}/' \
                  f'most_mentioned_hashtags/' \
                  f'most_mentioned_hashtags.csv'
        df = pd.read_csv(df_path)
        top_hashtags = 20
        df = df.head(top_hashtags)

        options = {
            'title': {'text': f'Top {top_hashtags} most mentioned hashtags '
                              f'for {self.keyword}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.hashtags.values.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'Hashtags mentioned',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Count of hashtags',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}'}
                      },
            'plotOptions': {'series': {'showInLegend': False}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.hashtags_count.values.tolist(), 'bar',
                       'Mentions count', color='#1998CB')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}/' \
                          f'{self.keyword}/most_mentioned_hashtags/' \
                          f'most_mentioned_hashtags.html'
        self.func_save_html(save_chart_path, h.htmlcontent)

    def visualize_most_active_users(self):
        df_path = f'{os.path.expanduser(self.save_path)}/{self.keyword}/' \
                  f'most_active_users/' \
                  f'most_active_users.csv'
        df = pd.read_csv(df_path)
        top_users = 20
        df = df.head(top_users)

        options = {
            'title': {'text': f'Top {top_users} of the most active users '
                              f'for {self.keyword}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.user.values.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'User',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Tweets published',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}'}
                      },
            'plotOptions': {'series': {'showInLegend': False}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.tweets_published.values.tolist(), 'bar',
                       'Mentions count', color='#1998CB')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}/' \
                          f'{self.keyword}/most_active_users/' \
                          f'most_active_users.html'
        self.func_save_html(save_chart_path, h.htmlcontent)

    def visualize_most_retweeted_users(self):
        df_path = f'{os.path.expanduser(self.save_path)}/' \
                  f'{self.keyword}/most_retweeted_users/' \
                  f'most_retweeted_users.csv'
        df = pd.read_csv(df_path)
        top_users = 20
        df = df.head(top_users)

        options = {
            'title': {'text': f'Top {top_users} of the most retweeted '
                              f'users for {self.keyword}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.user.values.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'User',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Count number of times user '
                                        'was retweeted',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}'}
                      },
            'plotOptions': {'series': {'showInLegend': False}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.count_retweets.values.tolist(), 'bar',
                       'Mentions count', color='#1998CB')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}/' \
                          f'{self.keyword}/most_retweeted_users/' \
                          f'most_retweeted_users.html'
        self.func_save_html(save_chart_path, h.htmlcontent)

    def visualize_users_by_followers(self):
        df_path = f'{os.path.expanduser(self.save_path)}/' \
                  f'{self.keyword}/users_by_followers/' \
                  f'users_by_followers.csv'
        df = pd.read_csv(df_path)
        top_users = 20
        df = df.head(top_users)

        options = {
            'title': {'text': f'Top {top_users} of users by number '
                              f'of followers for {self.keyword}',
                      'style': {'fontSize': '20'}
                      },
            'xAxis': {'categories': df.user.values.tolist(),
                      'labels': {'style': {'fontSize': '13px'}
                                 },
                      'title': {'text': 'User',
                                'style': {'fontSize': '15'}
                                }
                      },
            'yAxis': {'title': {'text': 'Number of followers',
                                'style': {'fontSize': '15'}
                                },
                      'allowDecimals': False,
                      'labels': {'style': {'fontSize': '15px'},
                                 'format': '{value}'}
                      },
            'plotOptions': {'series': {'showInLegend': False}
                            },
            'chart': {'backgroundColor': 'white'}
        }

        # Create chart
        h = Highchart(width=1000, height=700)
        h.set_dict_options(options)
        h.add_data_set(df.count_followers.values.tolist(), 'bar',
                       'Mentions count', color='#1998CB')

        # Save chart
        save_chart_path = f'{os.path.expanduser(self.save_path)}/' \
                          f'{self.keyword}/users_by_followers/' \
                          f'users_by_followers.html'
        self.func_save_html(save_chart_path, h.htmlcontent)
