# importing modules
import os
import json
import pathlib
import tweepy
import helper
import article
import numpy as np

# setup
root = pathlib.Path(__file__).parent.parent.resolve()
auth = tweepy.OAuthHandler(os.getenv("c_key"), os.getenv("c_secret"))
auth.set_access_token(os.getenv("a_token"), os.getenv("a_secret"))
api = tweepy.API(auth)
tweet_on = int(os.getenv("tweet") or 1) # master switch
endpoint = os.getenv("json_url")
# local or prod
if(endpoint is None):
    with open( root / "example.json", 'r+') as filehandle:
        demo_data = json.load(filehandle)["newsFeed"]
        articles_list = helper.get_articles(demo_data)
else:
    new_data = helper.get_news(endpoint)
    articles_list = helper.get_articles(new_data)

# Update the keys
with open( root / "news.json", 'r+') as filehandle:
    old_keys = json.load(filehandle)
    new_keys = list()
    for article in articles_list:
        new_keys.append(article.id)
    saving_keys = sorted(np.unique(old_keys + new_keys))
    filehandle.seek(0)
    json.dump(saving_keys, filehandle, indent=4)

# output
if __name__ == "__main__":
    if(tweet_on == 1):
        string_output = ""
        for article in articles_list:
            tweet_builder = f"★ {article.title} :- {article.url}"
            if(article.id not in old_keys):
                try:
                    print(f"{tweet_builder} ({article.timestamp})")
                    api.update_status(status=tweet_builder)
                except:
                    print("Error: ", article.title)
        string_output += f'<li><a href="{article.url}">{article.title}</a><br/><small>{article.timestamp}</small></li>\n'
        # update the index page
        index_page = root / "index.html"
        index_contents = index_page.open().read()
        final_output = helper.replace_chunk(index_contents, "news_marker", f"<ul>\n{string_output}</ul>")
        index_page.open("w").write(final_output)
    else:
        print("Tweet flag is set to off")
