import click
from codebase.providers.pop import POP
from codebase.providers.anime import Anime
from codebase.providers.kdrama import Drama
from codebase.utils.logger import get_logger
from codebase.utils.player import start_streaming

logger = get_logger("cli-logger")

# provider mapper
provider_mapper = {
    "movie": POP,
    "tv": POP,
    "anime": Anime,
    "kdrama": Drama
}


@click.group()
def cli():
    pass

@click.command(
    name="stream",
    help="Stream for media"
)
@click.argument(
    "query",
    required=True,
)
@click.option(
    "-t",
    "--type",
    default="movie",
    help="Type of media to stream for i.e [tv,movie,kdrama,anime]. Default:movie",
    required=True
)
@click.option(
    '-m',
    '--mode',
    default = 'sub',
    help = "Only applicable for anime provider[sub/dub].Default is sub"
)
def stream(query:str,type:str,mode:str):
    logger.info(f"Searching for {query}:{type}")
    
    #use the provider mapper
    provider = provider_mapper.get(type)()
    if provider:

        search_result = provider.search(query,type=type,mode=mode)
        
        if search_result:
            for i,r in enumerate(search_result):
                click.echo(click.style(f"{i+1}. {r[1]} / {r[0]}",fg="blue"))

            # ask for the index to fetch episode data
            index = click.prompt("[*]Enter the index to fetch episode data",type=int)
            media_url = search_result[index-1][0]

            if type == "movie":
                media_data:dict = provider.movie_streaming(url=media_url)
                start_streaming(streaming_data = media_data)


            else:
                episode_data = provider.get_episode_data(media_url)
                
                click.echo(click.style(f"Total episodes found: {episode_data['episode_count']}",fg="green"))
                
                ep_range = click.prompt("[*]Enter episode range [start:end]: ",type=str)
                
                start_ep = int(ep_range.split(":")[0])
                
                end_ep = int(ep_range.split(":")[1])
                
                #loop through start to end
                for ep in range(start_ep,end_ep+1):
                    media_data:dict = provider.episode_data(episode_number=ep)
                    start_streaming(streaming_data = media_data)
        else:
            click.echo(click.style("[-]No results found",fg="red"))
    else:
        click.echo(click.style("Invalid media type",fg="red"))


# add commands to the group
cli.add_command(stream)

if __name__ == "__main__":
    cli()