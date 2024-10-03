
import json
import os

import requests

api_key = os.environ['NEXON_OPENAPI_API_KEY']
live_api_key = os.environ['NEXON_LIVE_API_KEY']

api_url = 'https://open.api.nexon.com'
headers = {"x-nxopen-api-key": f"{api_key}"}

Items = ['descendant','weapon','module','reactor','external-component','reward','stat','void-battle']

def remove_json(file = None):
    files_removed = []
    items_removed = 0
    if file is not None:
        file = file.lower()
        if file in Items:
            with open(f"jsonData/{file}s.json") as f:
                items_removed += len(json.load(f))
            os.remove(f"jsonData/{file}s.json")
            files_removed.append(file + 's')
        else:
            return False, [], 0, 0, f"Invalid file name: {file}s"
    else:
        for file in os.listdir('jsonData'):
            with open(f"jsonData/{file}") as f:
                items_removed += len(json.load(f))
            os.remove(f"jsonData/{file}")
            files_removed.append(file[:-5])
    return True, files_removed, items_removed, None
        
        
def fetch_json(file = None):
    files_fetched = []
    items_fetched = 0
    if file is not None:
        file = file.lower()
        if file in Items:
            urlString = f"{api_url}/static/tfd/meta/en/{file}.json"
            response = requests.get(urlString, headers = headers)
            if response.status_code == 200:
                json_data = response.json()
                items_fetched += len(json_data)
                with open(f"jsonData/{file}s.json", 'w') as f:
                    json.dump(json_data, f, indent=4)
                    files_fetched.append(file + 's')
            else:
                return False, files_fetched, items_fetched, f"Response Code: {response.status_code}"
        else:
            return False, files_fetched, items_fetched, f"Invalid file name: {file}s"
    else:
        for item in Items:
            urlString = f"{api_url}/static/tfd/meta/en/{item}.json"
            response = requests.get(urlString, headers = headers)
            if response.status_code == 200:
                json_data = response.json()
                items_fetched += len(json_data)
                with open(f"jsonData/{item}s.json", 'w') as f:
                    json.dump(json_data, f, indent=4)
                    files_fetched.append(item + 's')
            else:
                return False, files_fetched, items_fetched, f"Response Code: {response.status_code}"
    return True, files_fetched, items_fetched, None
