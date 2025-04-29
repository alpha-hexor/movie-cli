from ... import config
from ...utils.logger import get_logger
from ...utils.http_client import client
from base64 import b64decode

logger = get_logger("allanime-extractor")

#global shit
anime_base = b64decode(config.ANIME_BASE).decode("utf-8")
anime_ref = b64decode(config.ANIME_REF).decode("utf-8")

def decrypt(password: int, encrypted_part: str):
    logger.debug(f"Attemptinng decryption of encrypted_url: {encrypted_part[:8]}...")
    decrypted = bytearray()
    for segment in bytearray.fromhex(encrypted_part):
        decrypted.append(segment ^ password)
    return decrypted.decode("utf-8")


def generate_stream_url(encrypted_urls:list)->dict:

    stream_data:dict = {
        "streaming_backup_url" : []
    }

    for url in encrypted_urls:
        decrypted_url = decrypt(password=56,encrypted_part=url)
        print(decrypted_url)
        if decrypted_url.startswith("https:"):
            stream_data["streaming_primary_url"] = decrypted_url
        else:
            decrypted_url = decrypted_url.replace("clock", "clock.json")

            r =client.get(
                f"{anime_base}{decrypted_url}",
                headers={
                    "Referer" :anime_ref
                },
                timeout=None
            )

            if r.status_code == 200:
                link = r.json()["links"][0]["link"]
                #give priority to wixmp links
                if "repackager.wixmp.com" in link:
                    stream_data["streaming_primary_url"] = link


                if "streaming_primary_url" not in stream_data:
                    stream_data["streaming_primary_url"] = link
                else:
                    stream_data["streaming_backup_url"].append(link)

            else:
                logger.error(f"Stream generation failed for: {decrypted_url}")
                pass
    
    stream_data["referrer"] = anime_ref
    return stream_data

    
    



