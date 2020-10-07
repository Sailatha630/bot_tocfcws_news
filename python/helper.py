import re
import json
import datetime

# Replacer function
def replace_chunk(content, marker, chunk):
    replacer = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    chunk = "<!-- {} starts -->\n{}\n<!-- {} ends -->".format(marker, chunk, marker)
    return replacer.sub(chunk, content)

# Methods
def ord(n):
    return str(n)+("th" if 4<=n%100<=20 else {1:"st",2:"nd",3:"rd"}.get(n%10, "th"))


def dtStylish(dt,f):
    return dt.strftime(f).replace("{th}", ord(dt.day))


def pprint(string):
    json_formatted_str = json.dumps(string, indent=2)
    print(json_formatted_str)


def compare_time(timestamp):
    working_date = datetime.datetime.strftime(datetime.datetime.utcnow() - datetime.timedelta(minutes=5),"%Y-%m-%d %H:%M:%S") # 5 minutes ago
    diff = datetime.datetime.strptime(working_date, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    return int(round(int(diff.seconds) / 60, 0))