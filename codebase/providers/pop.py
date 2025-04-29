from ..utils.http_client import client
from ..utils.logger import get_logger
from ..extractors.tmdb import extarct_tmdb
from base64 import b64decode
from typing import List,Tuple
import re
from .. import config

logger = get_logger("POP-logger")

class POP:
    def __init__(self):
        self.main_url:str = b64decode(config.POP_MAIN_URL).decode()
        self.tv_media_url:str = "" #only needed for tv stuff
        self.season:str = ""

    def search(self,query:str,**kwargs)->List[Tuple[str,str]]:
        """
        function to search for media
        """
        media_type = kwargs.get("type")

        r = client.get(
            f"{self.main_url}/search/{query.replace(" ", "%20")}",
            timeout= None
        )

        if r.status_code == 200:
            results = re.findall(r'<div class=\"relative group overflow-hidden\">\s+<a href=\"(.*?)\"\s+class=".*?">\s+<picture>\s+<img .+? data-src=".*?" alt="(.*?)"',r.text)

            if media_type == "movie":
                search_result= [r for r in results if "/movie/" in r[0]]
            
            else:
                search_result = [r for r in results if "/tv-show/" in r[0]]

        else:
            search_result = []
            raise Exception("Search operation failed")

        return search_result if len(search_result) > 0 else None
    
    @staticmethod
    def get_metadata(url:str)->dict:
        """
        get tmdb id, tracking data, ssignature
        """
        data = {}
    
        r = client.get(url,timeout=None)

        if r.status_code == 200:
            data["tmdb_id"] = re.findall(r'\s+tmdbId:\s+&#039;(\d+)&#039;',r.text)[0]
            data["sig"] = re.findall(r'sign:\s+&#039;(.*?)&#039;',r.text)[0]
            data['track'] = re.findall(r'trackingData:\s+&#039;(.*?)&#039;',r.text)[0]

            logger.debug(f"Media metadata found: {data} from url: {url}")

            return data
        else:
            raise Exception(f"{url} is not reachable")

    def movie_streaming(self,url:str)->None:
        """
        start streaming movies
        """
        data = self.get_metadata(url=url)

        media_data = extarct_tmdb(tmdb_id=data["tmdb_id"],media_type="movie",sig=data["sig"],track = data["track"])

        logger.debug(f"Extracted streamming links: {media_data}")

        if media_data["streaming_primary_url"] or media_data["streaming_backup_url"]:
            return media_data
        else:
            logger.error("No streaming link found")
            raise Exception(f"[-]No sreaming link found")
    
    def get_episode_data(self,url:str)->dict:

        url = url.replace('/tv-show/','/episode/')
        self.tv_media_url = url
        url+= '/1-1'

        tmdb_id = self.get_metadata(url=url)["tmdb_id"]

        r = client.get(
            f"https://api.tmdb.org/3/tv/{tmdb_id}?append_to_response=external_ids",
            headers={
                "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmYWNkMmE1YWE0YmMwMzAyZjNhZmRlYTIwZGQ2YWRhZSIsInN1YiI6IjY1OTEyNjU1NjUxZmNmNWYxMzhlMWRjNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5boG-w-nlk-SWB8hvFeWq_DNRbrU6n5XEXleVQ1L1Sg"
            }
        )

        if r.status_code ==200:
            seasons = r.json()["seasons"]
            season_data = {}

            for s in seasons:
                if s['season_number'] != 0:
                    season_data[s['season_number']] = s['episode_count']
        

            self.season = int(input(f"[*]Enter season-{len(list(season_data.keys()))}: "))

            return {"episode_count": season_data[self.season]}

        else:
            logger.error("Authorization token expired for tmdb client")
            raise Exception("[-]Tmdb api call failed")


        
    def episode_data(self,episode_number:int):

        logger.info(f"[*]Streaming episode {episode_number}")
        
        ep_url = f"{self.tv_media_url}/{self.season}-{episode_number}"
        
        data = self.get_metadata(url=ep_url)
        
        media_data = extarct_tmdb(tmdb_id=data["tmdb_id"],media_type="tv",sig=data["sig"],track = data["track"],season=self.season,episode=episode_number)

        logger.debug(f"Extracted streamming links: {media_data}")

        if media_data["streaming_primary_url"] or media_data["streaming_backup_url"]:
            return media_data
            
        else:
            logger.error("No streaming link found")
            raise Exception(f"[-]No streaming link found") 