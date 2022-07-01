# import
from requests import get
import json
import pathlib
import os
endpoint = "https://www.chelseafc.com/en/api/news/listing?pageIndex=1&pageSize=1"

def get_news_data(endpoint):
    response = get(endpoint, timeout=20)
    if response.status_code >= 400:
        raise RuntimeError(f"Request failed: { response.text }")
    return response.json()

# output
if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.parent.resolve()
    with open( root / "source.json", 'r+') as filehandle:
        data = json.load(filehandle)
        new_data = get_news_data(endpoint)
        filehandle.seek(0)
        json.dump(new_data, filehandle, indent=4)
