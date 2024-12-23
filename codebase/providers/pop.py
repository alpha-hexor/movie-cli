from ..utils.http_client import client
import json
from base64 import b64decode
from typing import List,Tuple
import re
from .. import config

class POP:
    def __init__(self):
        self.main_url = b64decode(config.POP_MAIN_URL).decode()

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
        
