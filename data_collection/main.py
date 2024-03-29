# -*- coding: utf-8 -*-

from twython import Twython
import re
import json
import os
import getopt
import sys
import time
import datetime

from web_scraping import get_tweet, am_i_using_tor

URL_COMPLETE_TWEET_REGEX = re.compile(r"… https://t\.co/(.*)+$")


def twython_authenticate():
    twitter = None
    with open("./config.json", 'r') as config_file:
        config = json.load(config_file)
        config_SRMDTC = config["apikeys"]["SRMDTC"]
        twitter = Twython(config_SRMDTC["app_key"], config_SRMDTC["app_secret"], config_SRMDTC["oauth_token"],
                          config_SRMDTC["oauth_token_secret"])
        twitter.verify_credentials()

    return twitter


def check_dirs():
    out = "./out"
    out_complete = "./out_complete"

    if not os.path.isdir(out):
        os.mkdir(out)

    if not os.path.isdir(out_complete):
        os.mkdir(out_complete)


def get_paths_and_geocode(query, latitude, longitude, radius):
    regex_replace_chars = re.compile(r"[#@áéíóúäëïöüÁÉÍÓÚñÑ]+", re.IGNORECASE)
    sanitized_file_name = re.sub(regex_replace_chars, '_', query)
    file_path = "./out/{}.json".format(sanitized_file_name)
    file_path_complete = "./out_complete/{}.json".format(sanitized_file_name)
	
    geocode = "{},{},{}".format(latitude, longitude, radius)
    return file_path, file_path_complete, geocode
	
	
def get_url_to_complete_tweet(text):
    result_search = re.search(URL_COMPLETE_TWEET_REGEX, text)
    # [2:] : remove "… "
    return result_search.group(0)[2:]
	
class Main:
    def __init__(self):
        self.twitter = twython_authenticate()
	
    def search_and_save(self, q, count=1000, latitude="19.4284700", longitude="-99.1276600", radius="20km", result_type="recent", include_entities=True):
        file_path, file_path_complete, geocode = get_paths_and_geocode(q, latitude, longitude, radius)

        check_dirs()

        print("Retrieving tweets for: \"{}\"...".format(q))
        tweets = self.twitter.search(q=q, count=count, geocode=geocode, result_type=result_type, include_entities=include_entities)

        print("Retrieving complete tweets...")

        tweets_for_pandas = ''
        i = 0
        for tweet in tweets["statuses"]:
            i += 1
            if tweet["truncated"] is True:
                url_to_complete_tweet = get_url_to_complete_tweet(tweet["text"])
                tweet["text"] = get_tweet(url_to_complete_tweet)
                tweet["url"] = url_to_complete_tweet
            tweets_for_pandas += "{}\r\n".format(json.dumps(tweet))

        print("# tweets: {}\r\n".format(i))

        with open(file_path, 'a') as file:
            file.write(tweets_for_pandas)

        with open(file_path_complete, 'a') as file:
            file.write(json.dumps(tweets))

        return
def main(keyword_list="./heal.list", keyword=False):
    print("Starting...")

    main_obj = Main()

    keywords = []
    # load keywords from file
    if keyword is False:
        with open(keyword_list, 'r') as list:
            keywords = [line.strip('\n') for line in list]
    else:
        keywords = [keyword]

    for curr_keyword in keywords:
        main_obj.search_and_save(curr_keyword, radius="150km")

    print("Done")
if __name__ == "__main__":
	while True:
		main()
		print("\nEjecutando proceso",datetime.datetime.now())
		time.sleep(3600)



	
	
