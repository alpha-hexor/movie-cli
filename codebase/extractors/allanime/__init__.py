from ... import config
from ...utils.logger import get_logger
from ...utils.http_client import client
import json
from base64 import b64decode

logger = get_logger("allanime-extractor")

#global shit
anime_base = b64decode(config.ANIME_BASE).decode("utf-8")
anime_ref = b64decode(config.ANIME_REF).decode("utf-8")

def decrypt(password: int, encrypted_part: str):
    decrypted = bytearray()
    for segment in bytearray.fromhex(encrypted_part):
        decrypted.append(segment ^ password)
    return decrypted.decode("utf-8")



def generate_stream_url(encrypted_urls:list):
    for url in encrypted_urls:
        decrypted_url = decrypt(password=56,encrypted_part=url)
        print(decrypted_url)

