from ...utils.http_client import client
from ...utils.logger import get_logger


logger = get_logger("autoembed-extractor")

def auto_extractor(url:str,headers:dict)->str:
    streaming_link = ""
    subtitle = ""
    logger.debug(f"Extracting streaming link from: {url} with headers: {headers}")
    r = client.get(
        url,
        headers=headers,
        timeout=None
    )

    if r.status_code == 200:
        data = r.json()
        streaming_link = data.get("videoSource",None)
        subtitle = next((s['file'] for s in data.get('subtitles', []) if "English" in s['label']), None)

        return streaming_link,subtitle
    
    else:
        logger.error("Autoemebed scrapper failed")
        return streaming_link,subtitle

