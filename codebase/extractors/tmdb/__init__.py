#create http urls and refs and pass to other extarctors
from base64 import b64decode
from ... import config
from .pop_extarctor import pop_extractor
from .autoem import auto_extractor
from ...utils.logger import get_logger

logger = get_logger("tmdb-extractor")

#some global shit
MAIN_POP_URL = b64decode(config.POP_MAIN_URL).decode()
POP_WORKER_URL = b64decode(config.POP_WORKER_URL).decode()
AUTO_CDN = b64decode(config.CDN_URL_1).decode()


POP_HEADERS = {
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": f"{MAIN_POP_URL}/",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": MAIN_POP_URL,
}

def extarct_tmdb(tmdb_id:str,media_type:str,**kwargs)->dict:
    data = {
        "streaming_primary_link" : "",
        "streaming_backup_url" : []
    }
    signature = kwargs.get('sig',"")
    tracking_data = kwargs.get('track','')

    if signature and tracking_data:
        #send to the pop extractor
        POP_HEADERS['X-Sign'] = signature

        url = f"{POP_WORKER_URL}/{tracking_data}"

        streaming_data = pop_extractor(url = url, headers=POP_HEADERS)

        if streaming_data:
            logger.debug(f"Popcorn streaming link found: {streaming_data}")
            data["streaming_backup_url"].append(streaming_data)

    if media_type == "movie":
        #autoembed extractor
        auto_url = f"{AUTO_CDN}/api/getVideoSource?type=movie&id={tmdb_id}"
        auto_headers = {"Referer": f"{AUTO_CDN}/movie/{tmdb_id}"}
    else:
        season = kwargs.get("season")
        episode = kwargs.get("episode")
        auto_url = f"{AUTO_CDN}/api/getVideoSource?type=tv&id={tmdb_id}/{season}/{episode}"
        auto_headers = {"Referer": f"{AUTO_CDN}/tv/{tmdb_id}/{season}/{episode}"}

    streaming_link , subtitle = auto_extractor(url=auto_url,headers=auto_headers)

    if streaming_link :
        logger.debug(f"Autoembed streaming link found: {streaming_link}")
        data["streaming_primary_link"] = streaming_link
            
        if subtitle:
            data["subtitle_url"] = subtitle
    

    return data