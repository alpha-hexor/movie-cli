import click
from codebase.providers.pop import POP
from codebase.providers.anime import Anime
from codebase.providers.kdrama import Drama
from codebase.utils.logger import get_logger


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
    name="search",
    help="Search for media"
)
@click.argument(
    "query",
    required=True,
)
@click.option(
    "-t",
    "--type",
    default="movie",
    help="Type of media to search for i.e [tv,movie,kdrama,anime]",
    required=True
)
@click.option(
    '-m',
    '--mode',
    default = 'sub',
    help = "Only applicable for anime provider[sub/dub].Default is sub"
)
def search(query:str,type:str,mode:str):
    # click.echo(click.style(f"[*]Searching for {query}:{type}",fg="green"))
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
                pass
            else:
                episode_data = provider.get_episode_data(media_url)

                if 'season_count' in episode_data :
                    pass
                
                
                else:
                    click.echo(click.style(f"Total episodes found: {episode_data['episode_count']}",fg="green"))
                    start_ep = click.prompt("[*]Enter episode to watch: ",type=int)

                    provider.stream_episode(start_ep = start_ep,end_ep = episode_data['episode_count'])

        else:
            click.echo(click.style("[-]No results found",fg="red"))
    else:
        click.echo(click.style("Invalid media type",fg="red"))


# add commands to the group
cli.add_command(search)

if __name__ == "__main__":
    cli()