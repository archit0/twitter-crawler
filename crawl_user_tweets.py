import requests
import logging
import warnings
import json
import re
import time
from bs4 import BeautifulSoup

# Loggers and warning
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
f = open("user_tweets.csv", "w+")

unique_hashtag_counts = {}
total_combined_tweets = 0
def crawl_a_user_tweets(username):
    global total_combined_tweets
    global unique_hashtag_counts
    print("Crawling: {}".format(username))
    url = "https://twitter.com/{}".format(username)
    # constants
    headers = {
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        'x-devtools-emulate-network-conditions-client-id': "72AE4A1C66EE2A3EB91EE7AF6D32704F",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'referer': "https://twitter.com/{}".format(username),
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
        'cache-control': "no-cache",
        }
    response = requests.get(url, headers=headers)
    data = response.text
    cookies = response.cookies
    soup = BeautifulSoup(data)
    start_index = data.index('max-position="')
    end_index = data.index('" d', start_index + 1)
    max_pos = data[start_index + 14: end_index]

    def save(username, handle, tweet_text, time_stamp):
        tweet_text = tweet_text.replace('\n', " ")
        data = "{}|@|{}|@|{}|@|{}\n".format(
            username,
            handle,
            tweet_text,
            time_stamp
        )
        f.write(data)
        f.flush()
        hashtags = re.findall(r"#(\w+)", tweet_text)
        for each in hashtags:
            unique_hashtag_counts[each] = unique_hashtag_counts.get(each, 0) + 1

    def normal_parse(soup):
        contents = soup.findAll('div', class_='content')
        for each_content in contents:
            try:
                username = each_content.find('strong', class_='fullname').contents[0]
                handle = each_content.find('a', class_='js-user-profile-link')['href']
                tweet_text = each_content.find('p', class_='tweet-text').text
                time_stamp = each_content.find('a', class_='tweet-timestamp')['title']
                save(username, handle, tweet_text, time_stamp)
            except Exception as e:
                pass

        return len(contents)

    total = normal_parse(soup)
    print("\tTWEETS CRAWLED : {}".format(total))
    if total > 0:
        header = {
            'referer': url,
            'accept': "application/json, text/javascript, */*; q=0.01",
            'x-requested-with': "XMLHttpRequest",
            'x-twitter-active-user': "yes",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
            'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        }
        while True:
            try:
                query_string = {
                    "include_available_features": "1",
                    "include_entities": "1",
                    "max_position": max_pos,
                    "reset_error_state":"false"
                }
                req = requests.get(
                    'https://twitter.com/i/profiles/show/{}/timeline/tweets'.format(username),
                    params=query_string,
                    headers=header,
                    cookies=cookies
                )
                cur_data = json.loads(json.dumps(json.loads(req.content.decode('utf-8'))))

                cookies = req.cookies
                max_pos = cur_data['min_position']
                cur_total = normal_parse(
                    BeautifulSoup(
                        cur_data['items_html']
                        .strip()
                        .replace('\n',' ')
                    )
                )
                if cur_total == 0:
                    print("BREAKING")
                    import ipdb; ipdb.set_trace()

                total += cur_total
                print("\tTWEETS CRAWLED : {}".format(total))
                # print("\tSleeping for: {}".format(cur_data['new_latent_count']/100))
                # time.sleep(cur_data['new_latent_count']/10)
            except Exception as e:
                print("*"*50)
                print(str(e))
                print("STOPPING")
                print("*"*50)
                break
    total_combined_tweets += total

with open("tweets.csv") as data:
    content = data.read().split('\n')

crawler_user_dict = {}
for row in content:
    attrs = row.split('|@|')
    if len(attrs) > 1:
        username = attrs[1]
        try:
            if username not in crawler_user_dict:
                crawler_user_dict[username] = True
                crawl_a_user_tweets(username)
        except Exception as e:
            print(e)

print("*" * 100)
print("TOTAL UNIQUE USERNAME: {}".format(len(crawler_user_dict)))
print("TOTAL TWEETS BY THESE USERS: {}".format(total_combined_tweets))
print(unique_hashtag_counts)
print("*" * 100)
