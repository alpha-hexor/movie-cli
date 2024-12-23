import subprocess


def start_streaming(**kwargs)->None:
    streaming_url:str = kwargs.get("streaming_url")

    player_args = [
        'mpv',
        '--fullscreen',
        f"{streaming_url}"
    ]

    player = subprocess.Popen(player_args)
    player.wait()
    player.kill()


