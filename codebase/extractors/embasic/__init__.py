from ...utils.logger import get_logger
from ...utils.http_client import client
from ... import config
import re
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad
import json

logger = get_logger("embed-basic-logger")

#global shit
AES_key = "93422192433952489752342908585752".encode("utf-8")
AES_iv = "9262859232435825".encode("utf-8")
MAIN_URL = base64.b64decode(config.KDRAMA_CDN).decode("utf-8")




def encrypt_data(data:str)->str:
    cipher = AES.new(AES_key, AES.MODE_CBC, AES_iv)
    padded_data = data + (16 - len(data) % 16) * chr(16 - len(data) % 16)
    encrypted_bytes = cipher.encrypt(padded_data.encode("utf-8"))
    return base64.b64encode(encrypted_bytes).decode("utf-8")


def decrypt_data(encrypted_data:str)->str:
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        cipher = AES.new(AES_key, AES.MODE_CBC, AES_iv)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error("[*]Decryption failed")
        raise Exception(e)

def get_streaming_url(url:str)->dict:
    r=client.get(url,timeout=None)

    if r.status_code == 200:
        logger.debug(f"Fetching crypto value from: {url}")
        crypto_value = re.findall(r'data-name="crypto" data-value="(.*?)"',r.text)[0]

        logger.debug(f"Decrypting crypto value: {crypto_value}")
        decrypted_crypto_value = decrypt_data(crypto_value)

        #media id

        media_id = decrypted_crypto_value.split('&')[0]
        media_slug = decrypted_crypto_value[len(media_id):]
        logger.info(f"[*]Found media id: {media_id}")
        logger.info(f"[*]Found media slug: {media_slug}")


        #encrypt the media id
        encrypted_media_id = encrypt_data(media_id)

        #send the final ajax request
        enc_ajax_url = f"{MAIN_URL}/encrypt-ajax.php?id={encrypted_media_id}{media_slug}&alias={media_id}"
        
        logger.debug(f"Sending ajax request to: {enc_ajax_url}")
        
        r = client.get(
            enc_ajax_url,
            headers={
                "Referer":url,
                "X-Requested-With": "XMLHttpRequest"
            },
            timeout = None
        )


        encrypted_streaming_source = r.json()['data']

        logger.info("[*]Generating streaming link")

        streaming_source = json.loads(decrypt_data(encrypted_streaming_source))

        data = {
            'streaming_primary_url' :  streaming_source['source'][0]['file'],
            'streaming_backup_url' : streaming_source['source_bk'][0]['file'] if 'source_bk' in streaming_source else None
        }

        logger.info(f"[*]Streaming links generated: {data}")

        return data
        
    else:
        logger.error(f"Failed to fetch data from url: {url}")
        raise Exception("[-]Failed to fetch data")
    
