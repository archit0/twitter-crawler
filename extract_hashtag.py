import re

with open("user_tweets.csv") as data:
    content = data.read().split('\n')

unique_hashtag_counts = {}
for row in content:
    attrs = row.split('|@|')
    if len(attrs) >= 3:
        tweet_text = attrs[2]
        hashtags = re.findall(r"#(\w+)", tweet_text)
        for each in hashtags:
            each = each.lower()
            unique_hashtag_counts[each] = unique_hashtag_counts.get(each, 0) + 1

f = open("tt.txt", "w+")
for each in unique_hashtag_counts:
    count = unique_hashtag_counts[each]
    if count > 50:
        for i in range(0, count):
            f.write(each + "\n")
