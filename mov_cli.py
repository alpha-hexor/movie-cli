import httpx
import re
import json
from base64 import b64decode
from typing import List, Tuple
import time
import subprocess

#load the config data
try:
    with open("config.json","r") as f:
        config_data = json.load(f)
    f.close()
except FileNotFoundError:
    print("Config.json not found. It should be in the same directory as the program")


#load urls
main_url = b64decode(config_data["main_url"]).decode("utf-8")
cdn_1 = b64decode(config_data["cdn_url_1"]).decode("utf-8")
cdn_2 = b64decode(config_data["cdn_url_2"]).decode("utf-8")
player = config_data["media_player"]

#initialize httpx client
client = httpx.Client(
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'},
    follow_redirects=True
)

tmdb_client = httpx.Client(
    headers={
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmYWNkMmE1YWE0YmMwMzAyZjNhZmRlYTIwZGQ2YWRhZSIsInN1YiI6IjY1OTEyNjU1NjUxZmNmNWYxMzhlMWRjNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5boG-w-nlk-SWB8hvFeWq_DNRbrU6n5XEXleVQ1L1Sg" #use this shit
    }
)

#regex and stuff
SEARCH_REGEX = r'<div class=\"relative group overflow-hidden\">\s+<a href=\"(.*?)\"\s+class=".*?">\s+<picture>\s+<img .+? data-src=".*?" alt="(.*?)"'
TMDB_REGEX =  r'\s+tmdbId:\s+&#039;(\d+)&#039;'

def tmdb_extract(media_link:str)->str:
    try:
        r = client.get(media_link)
        tmdb_id = re.findall(TMDB_REGEX,r.text)[0]
    except:
        time.sleep(3)
        r = client.get(media_link)
        tmdb_id = re.findall(TMDB_REGEX,r.text)[0]
    
    return tmdb_id

def get_streaming_link(is_movie:bool,tmdb_id:str,season:str=None,episode:str=None)->Tuple[str,str]:
    if is_movie:
        try:
            r = client.get(
                f"{cdn_1}/movie/{tmdb_id}",
                headers={
                    'Accept': 'application/json', 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    "Referer": f"{main_url}/",
                    "Origin" : main_url
                },
                timeout=5
            )

            streaming_link , subtitle = r.json()["source"] , [s["url"] for s in r.json()["subtitles"] if "English" in s["lang"]][0]

        except httpx.ReadTimeout:
            r = client.get(
                f"{cdn_2}/api/getVideoSource?type=movie&id={tmdb_id}",
                headers={
                    "Referer": f"{cdn_2}/movie/{tmdb_id}"
                }
            )

            streaming_link, subtitle = r.json()["videoSource"] , [s['file'] for s in r.json()['subtitles'] if "English" in s['label']][0]
    
    else:
        try:
            r = client.get(
                f"{cdn_1}/tv/{tmdb_id}/{season}/{episode}",
                headers={
                    'Accept': 'application/json', 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    "Referer": f"{main_url}/",
                    "Origin" : main_url
                },
                timeout=5
            )

            streaming_link , subtitle = r.json()["source"] , [s["url"] for s in r.json()["subtitles"] if "English" in s["lang"]][0]
        
        except httpx.ReadTimeout:
            r = client.get(
                f"{cdn_2}/api/getVideoSource?type=tv&id={tmdb_id}/{season}/{episode}",
                headers={
                    "Referer": f"{cdn_2}/tv/{tmdb_id}/{season}/{episode}"
                },
                timeout=None
            )

            streaming_link, subtitle = r.json()["videoSource"] , [s['file'] for s in r.json()['subtitles'] if "English" in s['label']][0]

    return streaming_link,subtitle

def media_player(streaming_link:str,subtitle_url:str)->None:
    player_args = [player,f"{streaming_link}"]

    if player == "mpv":
        player_args.append(f'--sub-file={subtitle_url}')
    else:
        print(f"Manually download and import subtitle from: {subtitle_url}")
    
    try:
        media_player = subprocess.Popen(player_args)
        media_player.wait()
        media_player.kill()

    except FileNotFoundError:
        print(f"[X]Can't find specified media player: {player}")
        print(f"[*]Streaming link: {streaming_link}")
        print(f"[*]Subtitle url: {subprocess}")

def handle_series(tmdb_id:str)->None:
    #gather season data from tmdb_database
    result = tmdb_client.get(
        f"https://api.tmdb.org/3/tv/{tmdb_id}?append_to_response=external_ids"
    ).json()

    seasons = result["seasons"]
    season_data = {}

    for s in seasons:
        if s['season_number'] != 0:
            season_data[s['season_number']] = s['episode_count']
            print(f"Season NUmber: {s['season_number']}/Total Ep: {s['episode_count']}")

    season = input("[*]Enter season: ")
    episode = input("[*]Enter episode number: ")

    total_episode = season_data[int(season)]

    streaming_link , subtitile_url = get_streaming_link(is_movie=False,tmdb_id=tmdb_id,season=season,episode=episode)

    media_player(streaming_link=streaming_link,subtitle_url=subtitile_url)

    curr_ep = int(episode) +1    
    while curr_ep <= total_episode:
        #ask for prompt
        c = input("[*]Do you want to continue[y/n]: ")

        if c == 'y':
            print(f"[*]Currently playing: {curr_ep}")
            streaming_link , subtitile_url = get_streaming_link(is_movie=False,tmdb_id=tmdb_id,season=season,episode=str(curr_ep))

            media_player(streaming_link=streaming_link,subtitle_url=subtitile_url)

            curr_ep +=1
        else:
            break


def search(query:str)->List[Tuple[str,str]]:
    r = client.get(
        f"{main_url}/search/{query.replace(" ", "%20")}"
    )

    search_result = re.findall(SEARCH_REGEX,r.text)

    return search_result

def main():
    query = input("[*]Enter query: ")
    search_result = search(query=query)

    for index,result in enumerate(search_result,start=1):
        print(f"[{index}]. {result[1]}")
    
    x = int(input("[*]Enter your option: "))-1

    media_link = search_result[x][0]

    if '/tv-show/' in media_link:
        media_link = media_link.replace('/tv-show/','/episode/')
        media_link = media_link + '/1-1'
    
    is_movie:bool = True if '/movie/' in media_link else False

    tmdb_id = tmdb_extract(media_link=media_link)

    if is_movie:
        streaming_url , subtitle_url = get_streaming_link(is_movie=True,tmdb_id=tmdb_id)

        media_player(streaming_link=streaming_url,subtitle_url=subtitle_url)
    
    else:
        handle_series(tmdb_id=tmdb_id)

if __name__ == "__main__":
    main()
