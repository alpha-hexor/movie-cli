from ...utils.http_client import client
from ...utils.logger import get_logger
import json
from httpx import ReadTimeout
import base64

logger = get_logger("pop-extractor")


def pop_extractor(url:str,headers:dict):
    logger.debug(f"Extracting streamurl from: {url}")
    try:
        r = client.get(
            url,
            headers=headers,
            timeout=20
        )

        if r.status_code == 200:
            logger.debug(f"Streaming data found: {r.json()}") 
            try:
                data = json.loads(base64.b64decode(r.json()).decode("utf-8"))

                streaming_link = data["sources"][0]["file"] if data["sources"] else None

                return streaming_link
            except:
                logger.error("Streaming data not in basse64 format")
                pass           
        
        else:
            logger.error(f"Worker url status code: {r.status_code}")
            pass

    except ReadTimeout:
        logger.error("Worker Url down")
        pass
