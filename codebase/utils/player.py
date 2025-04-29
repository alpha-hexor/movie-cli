import subprocess
from .logger import get_logger

logger = get_logger("Media-Player")

def start_streaming(**kwargs)->None:
    streaming_data:dict = kwargs.get("streaming_data")

    streaming_url = streaming_data.get("streaming_primary_url") if streaming_data.get("streaming_primary_url") else streaming_data.get("streaming_backup_url")[0]

    logger.debug(f"Streaming from: {streaming_url}")
    player_args = [
        'mpv',
        '--fullscreen',
        f'{streaming_url}'
    ]

    if "subtitle_url" in streaming_data:
        logger.debug(f"Subtitle url: {streaming_data['subtitle_url']}")

        player_args.append(f'--sub-file={streaming_data["subtitle_url"]}')

    if "referrer" in streaming_data:
        logger.debug(f"Referrer url: {streaming_data['referrer']}")
        player_args.append(f'--referrer={streaming_data["referrer"]}')

    player = subprocess.Popen(player_args,shell=False)
    player.wait()
    player.kill()


