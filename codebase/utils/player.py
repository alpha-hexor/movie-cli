import subprocess


def start_streaming(**kwargs)->None:
    streaming_url:str = kwargs.get("streaming_url")

    player_args = [
        'mpv',
        '--fullscreen',
        f"{streaming_url}"
    ]

    if "extra_args" in kwargs:
        player_args.append(kwargs["extra_args"])

    player = subprocess.Popen(player_args,shell=False)
    player.wait()
    player.kill()


