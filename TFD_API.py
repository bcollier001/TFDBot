import os
import requests

API_KEY = os.environ['NEXON_OPENAPI_API_KEY']
LIVE_API_KEY = os.environ['NEXON_LIVE_API_KEY']

headers = {"x-nxopen-api-key": f"{API_KEY}"}


api_url = 'https://open.api.nexon.com'
OUID = '/tfd/v1/id'
#https://open.api.nexon.com/tfd/v1/id?user_name=brandon.tcollier25%234479

mastery_rank_icon_urls = {
    '1': 'https://tfd.wiki/images/thumb/7/72/Icon_MasteryRank_Symbol_001.png/200px-Icon_MasteryRank_Symbol_001.png',
    '2': 'https://tfd.wiki/images/thumb/2/2e/Icon_MasteryRank_Symbol_002.png/200px-Icon_MasteryRank_Symbol_002.png',
    '3': 'https://tfd.wiki/images/thumb/9/93/Icon_MasteryRank_Symbol_003.png/200px-Icon_MasteryRank_Symbol_003.png',
    '4': 'https://tfd.wiki/images/thumb/9/93/Icon_MasteryRank_Symbol_004.png/200px-Icon_MasteryRank_Symbol_004.png',
    '5': 'https://tfd.wiki/images/thumb/6/62/Icon_MasteryRank_Symbol_005.png/200px-Icon_MasteryRank_Symbol_005.png',
    '6': 'https://tfd.wiki/images/thumb/b/b8/Icon_MasteryRank_Symbol_006.png/200px-Icon_MasteryRank_Symbol_006.png',
    '7': 'https://tfd.wiki/images/thumb/8/8a/Icon_MasteryRank_Symbol_007.png/200px-Icon_MasteryRank_Symbol_007.png',
    '8': 'https://tfd.wiki/images/thumb/7/75/Icon_MasteryRank_Symbol_008.png/200px-Icon_MasteryRank_Symbol_008.png',
    '9': 'https://tfd.wiki/images/thumb/6/6d/Icon_MasteryRank_Symbol_009.png/200px-Icon_MasteryRank_Symbol_009.png',
    '10': 'https://tfd.wiki/images/thumb/7/71/Icon_MasteryRank_Symbol_010.png/200px-Icon_MasteryRank_Symbol_010.png',
    '11': 'https://tfd.wiki/images/thumb/c/c0/Icon_MasteryRank_Symbol_011.png/200px-Icon_MasteryRank_Symbol_011.png',
    '12': 'https://tfd.wiki/images/thumb/c/c1/Icon_MasteryRank_Symbol_012.png/200px-Icon_MasteryRank_Symbol_012.png',
    '13': 'https://tfd.wiki/images/thumb/8/86/Icon_MasteryRank_Symbol_013.png/200px-Icon_MasteryRank_Symbol_013.png',
    '14': 'https://tfd.wiki/images/thumb/4/46/Icon_MasteryRank_Symbol_014.png/200px-Icon_MasteryRank_Symbol_014.png',
    '15': 'https://tfd.wiki/images/thumb/d/d6/Icon_MasteryRank_Symbol_015.png/200px-Icon_MasteryRank_Symbol_015.png',
    '16': 'https://tfd.wiki/images/thumb/b/ba/Icon_MasteryRank_Symbol_016.png/200px-Icon_MasteryRank_Symbol_016.png',
    '17': 'https://tfd.wiki/images/thumb/1/15/Icon_MasteryRank_Symbol_017.png/200px-Icon_MasteryRank_Symbol_017.png',
    '18': 'https://tfd.wiki/images/thumb/d/d3/Icon_MasteryRank_Symbol_018.png/200px-Icon_MasteryRank_Symbol_018.png',
    '19': 'https://tfd.wiki/images/thumb/5/57/Icon_MasteryRank_Symbol_019.png/200px-Icon_MasteryRank_Symbol_019.png',
    '20': 'https://tfd.wiki/images/thumb/5/53/Icon_MasteryRank_Symbol_020.png/200px-Icon_MasteryRank_Symbol_020.png',
    '21': 'https://tfd.wiki/images/thumb/2/28/Icon_MasteryRank_Symbol_021.png/200px-Icon_MasteryRank_Symbol_021.png',
    '22': 'https://tfd.wiki/images/thumb/6/6c/Icon_MasteryRank_Symbol_022.png/200px-Icon_MasteryRank_Symbol_022.png',
    '23': 'https://tfd.wiki/images/thumb/9/9c/Icon_MasteryRank_Symbol_023.png/200px-Icon_MasteryRank_Symbol_023.png',
    '24': 'https://tfd.wiki/images/thumb/5/5c/Icon_MasteryRank_Symbol_024.png/200px-Icon_MasteryRank_Symbol_024.png',
    '25': 'https://tfd.wiki/images/thumb/7/78/Icon_MasteryRank_Symbol_025.png/200px-Icon_MasteryRank_Symbol_025.png',
    '26': 'https://tfd.wiki/images/thumb/6/6a/Icon_MasteryRank_Symbol_026.png/200px-Icon_MasteryRank_Symbol_026.png',
    '27': 'https://tfd.wiki/images/thumb/3/3d/Icon_MasteryRank_Symbol_027.png/200px-Icon_MasteryRank_Symbol_027.png',
    '28': 'https://tfd.wiki/images/thumb/8/87/Icon_MasteryRank_Symbol_028.png/200px-Icon_MasteryRank_Symbol_028.png',
    '29': 'https://tfd.wiki/images/thumb/c/c5/Icon_MasteryRank_Symbol_029.png/200px-Icon_MasteryRank_Symbol_029.png',
    '30': 'https://tfd.wiki/images/thumb/7/70/Icon_MasteryRank_Symbol_030.png/200px-Icon_MasteryRank_Symbol_030.png'
}

def search_ouid(username: str):
    username = username.replace('#','%23')
    urlString = f"{api_url}{OUID}?user_name={username}"
    response = requests.get(urlString, headers = headers)
    return response.json()

def search_player_descendant(username: str):
    #https://open.api.nexon.com/tfd/v1/user/descendant?ouid=70035...
    ouid_response = search_ouid(username)
    if 'error' not in ouid_response:
        urlString = f"{api_url}/tfd/v1/user/descendant?ouid={ouid_response['ouid']}"
        response = requests.get(urlString, headers = headers)
        return response.json()
    else:
        return ouid_response

def search_playerBasic_descendant(username: str):
    #https://open.api.nexon.com/tfd/v1/user/basic?ouid=70035...
    ouid_response = search_ouid(username)
    if 'error' not in ouid_response:
        urlString = f"{api_url}/tfd/v1/user/basic?ouid={ouid_response['ouid']}"
        response = requests.get(urlString, headers = headers)
        return response.json()
    else:
        return ouid_response