# Twitter Scraper for Data Analysis

## Description
- This package scrapes and process data from Twitter to generate tabular data and charts ready for data analysis.
- It can be used with any Twitter account, hashtag, or query for any period specified by a start and end date.
- Because I love cats, let's see an example for the account [@RealGrumpyCat](https://twitter.com/RealGrumpyCat) starting when the account was created (October 1, 2012) and ending on November 27, 2020. This is what the program generates for this example:
  - [Grouped date with the count of tweets published, retweets, and favorites by date](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/grouped_date)
  - [Key topics with the main topics found in the content of all tweets using TFIDF features](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/key_topics)
  - [Most active users with the count of tweets published by account](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/most_active_users)
  - [Most mentioned hashtags with the count of hashtags mentioned in all tweets by hashtag](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/most_mentioned_hashtags)
  - [Most mentioned users with the count of hashtags mentioned in all tweets by account](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/most_mentioned_hashtags)
  - [Most retweeted users with the count of retweets by account](https://github.com/Sayalave/twitter_scrapper/tree/master/example_output/realgrumpycat/most_retweeted_users)
  - [Co-hashtag matrix with a matrix for the co-occurrence of hashtags](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/co_hashtags_matrix)
  - [Cleaned data with the master data frame where each row is one tweet and each column is a processed tweet attribute](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/clean_data)
  - [Raw data with the data as scraped and returned by Twitter API](https://github.com/Sayalave/twitter_scrapper/blob/master/example_output/realgrumpycat/raw_data)
- The charts are in HTML format and won't be rendered by Github. You can download them and open the HTML files with your favorite browser. 

## Authentication
- The package uses both Selenium to get a list of Twitter IDs and Twitter API to pull metadata for each Twitter ID. For that reason, it is necessary to have Twitt
- Since it uses the Twitter API, the package needs a file with Twitter Developer keys in JSON format:
```json
{
  "consumer_key":"********",
  "consumer_secret":"********",
  "access_token":"********",
  "access_token_secret":"********"
}
```

## Parameters

- `keyword`: hashtag, account, or query. Query means words that should be present in the tweet. If it is query and more than one word is provided, underscores should be used to separate words.
- `keyword_type`: it can be hashtag, query, or account.
- `start`: date when the data collection starts. Format: 'YYYY-MM-DD'
- `end`: date when the data collection starts. Format: 'YYYY-MM-DD'
- `keys_path`: path to the JSON file with the Twitter Developer keys.  
- `delay`: (optional) seconds to wait between loading pages and scrolling down. 
- `chromedriver_path`: (optional) path to chromedriver executable.


## Instructions
### Docker:
- The easier way to run the program is using Docker.
- For example, the commands to get the data for the data for the RealGrumpyCat example. 
  1. Build the Dockerfile: `docker build --no-cache -t scraper .`
  2. Run a container `docker run --rm -v $(PWD)/data:/app/out/ -it scraper /usr/bin/python3 main.py -keyword RealGrumpyCat -start 2012-10-01 -end 2020-11-27 -keyword_type account --keys_path twitter_keys.json --delay 1 --chromedriver_path /usr/bin/chromedriver`
  3. See your data in your working directory under `~/data/`

### Command line:
- You can also run the program in Python.
- For example, after installing Python3, requirements, and the chromedriver executable, the commands to get the data for the RealGrumpyCat example would be:
  1. `python3 main.py -keyword RealGrumpyCat -start 2012-10-01 -end 2020-11-27 -keyword_type account --keys_path twitter_keys.json --delay 1 --chromedriver_path /usr/local/bin/chromedriver`