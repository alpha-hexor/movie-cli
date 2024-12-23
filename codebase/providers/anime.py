from ..utils.http_client import client
from ..utils.logger import get_logger
from ..extractors.allanime import generate_stream_url
import json
from base64 import b64decode
from typing import List,Tuple
from .. import config
import re

logger = get_logger("anime-logger")

class Anime:
    def __init__(self):
        self.api_url:str = b64decode(config.ANIME_API).decode()
        self.ref_url: str= b64decode(config.ANIME_REF).decode()
        self.mode:str = ""
        self.anime_id:str = ""

    def search(self,query:str,**kwargs)->List[Tuple[str,str]]:

        self.mode = kwargs.get("mode")

        search_gql = """
        query(
            $search: SearchInput
            $limit: Int
            $page: Int
            $translationType: VaildTranslationTypeEnumType
            $countryOrigin: VaildCountryOriginEnumType
        ) {
            shows(
                search: $search
                limit: $limit
                page: $page
                translationType: $translationType
                countryOrigin: $countryOrigin
            ) {
                edges {
                    _id
                    name
                    availableEpisodes
                    __typename
                }
            }
        }
        """
        variables = {
            "search": {
                "allowAdult": True,
                "allowUnknown": False,
                "query": query
            },
            "limit": 40,
            "page": 1,
            "translationType": self.mode,
            "countryOrigin": "ALL"
        }

        payload = {
            "variables": json.dumps(variables),
            "query": search_gql
        }

        r = client.get(
            f"{self.api_url}/api",
            headers={
                "Referer" : self.ref_url
            },
            params=payload,
            timeout=None
        )

        if r.status_code == 200:
            data = r.json()
            search_result = [(f"https://allmanga.to/bangumi/{i["_id"]}",i["name"]) for i in data["data"]["shows"]["edges"]]
            return search_result if len(search_result) > 0 else None
        else:
            raise Exception("Search operation failed")
        
    def get_episode_data(self,url:str)->dict:
        logger.info(f"Fetching episode data from {url}")

        self.anime_id = url.split("/bangumi/")[-1]

        logger.debug(f"Anime id: {self.anime_id}")

        episodes_list_gql = """
        query ($showId: String!) {
            show(_id: $showId) {
                _id
                availableEpisodesDetail
            }
        }
        """

        variables ={
            "showId": self.anime_id
        }

        payload = {
            "variables" : json.dumps(variables),
            "query" : episodes_list_gql
        }

        r = client.get(
            f"{self.api_url}/api",
            headers={
                "Referer" : self.ref_url
            },
            params=payload,
            timeout=None
        )

        ep_count = r.json()["data"]["show"]["availableEpisodesDetail"][self.mode]

        if ep_count:
            return {
                "episode_count": len(ep_count)
            }
        else:
            raise Exception(f"[-]No episode found for mode: {self.mode}")
        

    def stream_episode(self,start_ep:int,end_ep:int):
        logger.info(f"Streaming episode from {start_ep} to {end_ep}")

        episode_embed_gql = """
        query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {
            episode(
                showId: $showId
                translationType: $translationType
                episodeString: $episodeString
            ) {
                episodeString
                sourceUrls
            }
        }
        """

        variables = {
            "showId": self.anime_id,
            "translationType": self.mode
        }

        for ep in range(start_ep,end_ep+1):
            logger.info(f"Generating streaming link for episode: {ep}, mode: {self.mode}")

            variables["episodeString"] =  f"{ep}"

            payload = {
                "variables" : json.dumps(variables),
                "query" : episode_embed_gql
            }

            r = client.get(
                f"{self.api_url}/api",
                headers={
                    "Referer" : self.ref_url
                },
                params=payload,
            )

            if r.status_code == 200:
                encrypted_urls = re.findall(r'"sourceUrl":"--(\w+)"',r.text)
                encrypted_urls = list(set(encrypted_urls))
                logger.debug(f"Unique encrypted urls found: {len(encrypted_urls)}")

                if encrypted_urls:
                    generate_stream_url(encrypted_urls = encrypted_urls)
                else:
                    logger.error(f"Encrypted urls are: {r.json()}")
                    raise Exception("Valid Urls not found")

            else:
                raise Exception("Failed to generate streaming link")


