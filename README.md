

### Docker instructions:
- `docker build --no-cache -t scraper .`
- `docker run --rm -v $(PWD)/data:/app/out/ -it scraper /usr/bin/python3 main.py --keyword gopro --start 2020-01-01 --end 2020-11-30 --keyword_type account --save_path out --keys_path twitter_keys.json --delay 1  --chromedriver_path /usr/bin/chromedriver`