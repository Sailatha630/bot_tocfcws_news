# importing modules
import os
import json
import pathlib
import helper
import article
import outputs
import numpy as np

# setup
root = pathlib.Path(__file__).parent.parent.resolve()

with open( root / "source.json", 'r+') as filehandle:
    news_data = json.load(filehandle)["newsFeed"]
    articles_list = outputs.get_articles(news_data)

# output
if __name__ == "__main__":
        string_output = ""
        print("count of articles in list: ", len(articles_list))
        outputs.rss_output('tocfcws.xml', articles_list)
        for article in articles_list:
            print("★ ", article.title)
            string_output += f'<li><a href="{article.url}">{article.title}</a><br/><small>{article.timestamp}</small></li>\n'
        # update the index page
        index_page = root / "index.html"
        index_contents = index_page.open().read()
        final_output = helper.replace_chunk(index_contents, "news_marker", f"<ul>\n{string_output}</ul>")
        index_page.open("w").write(final_output)
