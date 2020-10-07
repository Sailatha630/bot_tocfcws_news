# importing modules
import os
import json
import pathlib
import tweepy
import datefinder
from requests import get
import helper

root = pathlib.Path(__file__).parent.parent.resolve()
tweet_on = int(os.getenv("tweet"))
tweet_window = int(os.getenv("window")) or 5
minute_offset = 65

auth = tweepy.OAuthHandler(os.getenv("c_key"), os.getenv("c_secret"))
auth.set_access_token(os.getenv("a_token"), os.getenv("a_secret"))
api = tweepy.API(auth)


class article:
    def __init__(self, title, url, timestamp):
        self.title = title
        self.url = (
            url.replace("prod-content-cdn", "www")
            .replace("content/chelseafc/", "")
            .replace(".html", "")
        )
        self.timestamp = timestamp

    def __repr__(self):
        return repr((self.title, self.url, self.timestamp))


def get_news(num):
    endpoint = os.getenv("json_url")
    response = get(endpoint, timeout=20)
    articles = list()
    if response.status_code >= 400:
        raise RuntimeError(f"Request failed: { response.text }")
    data = response.json()["newsFeed"][:num]
    for i in range(0, num):
        link = data[i]["link"]["url"]
        title = data[i]["link"]["title"]
        time = data[i]["publishDate"]
        try:
            published_matches = list(datefinder.find_dates(time))
            if len(published_matches) > 0:
                published_str_dt = published_matches[0].strftime("%Y-%m-%d %H:%M:%S")
            else:
                published_str_dt = ""
        except KeyError:
            print("error with publishing " + title)
            published_str_dt = ""
        articles.append(article(title, link, published_str_dt))
    return articles


# output
if __name__ == "__main__":
    index_page = root / "index.html"
    index_contents = index_page.open().read()
    string_output = ""
    for article in get_news(8):
        output_builder = f"{article.title} :- {article.url}"
        print("★", article.title)
        string_output += f'<li><a href="{article.url}">{article.title}</a><br/><small>{article.timestamp}</small></li>\n'
        if helper.compare_time(article.timestamp) < int(tweet_window):
            if tweet_on == 1:
                tweet_string = f"★ {output_builder}"
                print("tweet length: ", len(tweet_string))
                try:
                    api.update_status(status=tweet_string)
                except:
                    print("Error", tweet_string)
    final_output = helper.replace_chunk(
        index_contents, "news_marker", f"<ul>\n{string_output}</ul>"
    )
    index_page.open("w").write(final_output)
