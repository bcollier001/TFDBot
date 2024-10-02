
import json
import os

import requests

api_key = os.environ['NEXON_OPENAPI_API_KEY']
live_api_key = os.environ['NEXON_LIVE_API_KEY']

api_url = 'https://open.api.nexon.com'
headers = {"x-nxopen-api-key": f"{api_key}"}

Items = ['descendant','weapon','module','reactor','external-component','reward','stat','void-battle']

def remove_jsonData(sfolder = None):
    if sfolder is not None:
        if sfolder in Items:
            folders_removed = 0
            files_removed = 0
            #purge jsonData in specified folder
            for data in os.listdir(f'./jsonData/{sfolder}s'):
                os.remove(f'./jsonData/{sfolder}s/{data}')
                files_removed += 1
            os.rmdir(f'./jsonData/{sfolder}s')
            folders_removed += 1
        else:
            return False, 0, 0, f"Invalid folder name: {sfolder}s"
    else:
        #purge all jsonData
        folders_removed = 0
        files_removed = 0
        for folder in os.listdir('./jsonData'):
            for file in os.listdir(f'./jsonData/{folder}'):
                os.remove(f'./jsonData/{folder}/{file}')
                files_removed+=1
            os.rmdir(f'./jsonData/{folder}')
            folders_removed+=1
    return True, folders_removed, files_removed, None

def get_jsonData(sfolder = None):
    if sfolder is not None:
        if sfolder in Items:
            newpath = f'./jsonData/{sfolder}s'
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            urlString = f"{api_url}/static/tfd/meta/en/{sfolder}.json"
            response = requests.get(urlString, headers = headers)
            if response.status_code == 200:
                parsed_files = parse_data(response.json(), sfolder)
                return True, 1, parsed_files, None
            else:
                return False, 0, 0, f"Error: response code is {response.status_code}"

        else:
            return False, 0, 0, f"Invalid folder name: {sfolder}s"
    else:
        #get all jsonData
        total_parsed_files = 0
        folders_processed = 0
        for item in Items:
            newpath = f'./jsonData/{item}s'
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            urlString = f"{api_url}/static/tfd/meta/en/{item}.json"
            response = requests.get(urlString, headers = headers)
            parsed_files = parse_data(response.json(), item)
            total_parsed_files += parsed_files
            folders_processed += 1
        #-1 total parsed files because idk why it's not working
        return True, folders_processed, total_parsed_files-1, None

def parse_data(dataFile, item: str):
    parsed_data = 0
    for data in dataFile:
        if item == 'reward':
            map_id = data.get('map_id').replace(' ','_')
            if map_id.startswith('610001') or map_id.startswith('610002'):
                item_name = f"{data.get('map_name').replace(' ','_')}"
            else:
                item_name = f"{map_id} - {data.get('map_name').replace(' ','_')}"
            filename = f"jsonData/{item}s/{item_name}.json"

        else:
            item_id = data.get(f"{item.replace('-','_')}_id").replace(' ','_').replace('\'','')
            item_name = data.get(f"{item.replace('-','_')}_name").replace(' ','_').replace('\'','')
            filename = f"jsonData/{item}s/{item_name} - {item_id}.json"

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        parsed_data += 1
    return parsed_data