import csv
import json
from textwrap import dedent, indent
import datetime
from email.utils import formatdate
import hashlib
import article

def get_articles(data):
    articles = list()
    for i in range(0,len(data)):
        link = data[i]["link"]["url"]
        title = data[i]["link"]["title"]
        time = data[i]["publishDate"]
        processed = datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
        output_time = formatdate(int(processed.strftime('%s')))
        id = hashlib.md5(f"{title}-{link}".encode('utf-8')).hexdigest()
        articles.append(article.article(id, title, link, output_time))
    return articles

def rss_output(path, articles_list):

    with open(path, 'w') as rssfile:
        print(dedent(f'''
            <?xml version="1.0" encoding="UTF-8"?>
            <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
             <channel>
              <title>TOCFCWS RSS Feed</title>
              <link>https://app.thechels.uk</link>
              <description>Latest official cfc news</description>
              <atom:link href="http://app.thechels.uk/tocfcws.xml" rel="self" type="application/rss+xml" />
              <lastBuildDate>{formatdate()}</lastBuildDate>
            ''').strip(), file=rssfile)

        for article in articles_list:
            print(indent(dedent(f'''
                <item>
                 <description>{article.title}</description>
                 <pubDate>{article.timestamp}</pubDate>
                 <guid isPermaLink="false">{article.id}</guid>
                </item>
            ''').strip(), "  "), file=rssfile)

        print(dedent('''
             </channel>
            </rss>'''
        ), file=rssfile)
