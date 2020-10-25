# importing modules
import os
import json
import pathlib
import tweepy
import helper
import article

root = pathlib.Path(__file__).parent.parent.resolve()
tweet_on = int(os.getenv("tweet") or 0)
endpoint = os.getenv("json_url") or ""

auth = tweepy.OAuthHandler(os.getenv("c_key"), os.getenv("c_secret"))
auth.set_access_token(os.getenv("a_token"), os.getenv("a_secret"))
api = tweepy.API(auth)

with open( root / "news.json", 'r+') as filehandle:
    data = json.load(filehandle)
    new_data = helper.get_news(endpoint)
    articles_list = helper.get_articles(new_data)
    new_keys = []
    for article in articles_list:
        new_keys.append(article.id)
    filehandle.seek(0)
    json.dump(new_keys, filehandle, indent=4)

# output
if __name__ == "__main__":
    index_page = root / "index.html"
    index_contents = index_page.open().read()
    string_output = ""
    for article in articles_list:
        output_builder = f"{article.title} :- {article.url}"
        print(f"★ {article.title} ({article.timestamp})")
        string_output += f'<li><a href="{article.url}">{article.title}</a><br/><small>{article.timestamp}</small></li>\n'
        if(tweet_on == 1 and article.id not in data):
            tweet_string = f"★ {output_builder}"
            print("tweet length: ", str(len(tweet_string)))
            try:
                api.update_status(status=tweet_string)
            except:
                print("Error", tweet_string)
    final_output = helper.replace_chunk(
        index_contents, "news_marker", f"<ul>\n{string_output}</ul>"
    )
    index_page.open("w").write(final_output)
