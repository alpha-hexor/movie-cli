from ..utils.http_client import client
from ..utils.logger import get_logger
from ..extractors.embasic import get_streaming_url
from base64 import b64decode
from typing import List,Tuple
from .. import config
import re

logger = get_logger("kdram-logger")

class Drama:
    def __init__(self):
        self.main_url = b64decode(config.KDRAMA_URL).decode()
        self.episodes_data = []

    def search(self,query:str,**kwargs)->List[Tuple[str,str]]:
        """
        function to search for media
        """

        r = client.get(
            f"{self.main_url}/search?keyword={query.replace(" ", "+")}&type=movies",
            headers={
                "x-requested-with": "XMLHttpRequest"
            }
        )

        if r.status_code == 200:
            data = r.json()
            search_results = [(f"{self.main_url}{i['url']}", i['name']) for i in data]

            return search_results if len(search_results) >0 else None
        else:
            raise Exception("Search operation failed")
        
    def get_episode_data(self,url:str):
        logger.info(f"Fetching episode data from {url}")
        
        r = client.get(url)

        if r.status_code == 200:
            self.episodes_data = re.findall(
                r'href="(.*-episode-\d+\.html)" class="img"',
                r.text
            )

            if len(self.episodes_data) > 0:
                return {'episode_count': len(self.episodes_data)}
            else:
                raise Exception("[-]No episode found")            
        else:
            raise Exception("[-]Failed to fetch episode data")
        
    def episode_data(self,episode_number:int)->dict:
        logger.info(f"[*]Streaming episode {episode_number}")
            
        ep_url = f"{self.main_url}{self.episodes_data[-episode_number]}"
            
        logger.debug(f"[*]Fetching iframe link from {ep_url}")
            
        r = client.get(ep_url)

        if r.status_code == 200:
            iframe_link = re.findall(r'iframe .+? src="(.*?)"',r.text)[0]
            
            logger.debug(f"[*]Iframe link: https:{iframe_link}")
            
            r =client.get(f"https:{iframe_link}")
            
            cdn_link = str(r.url)
            
            logger.debug(f"[*]CDN LINK: {cdn_link}")
            
            streaming_data = get_streaming_url(url=cdn_link)

            return streaming_data

        else:raise Exception("[-]Connection failed")