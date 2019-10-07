import click
import json
import urllib.parse
import requests
import sqlite_utils
from . import utils

CONSUMER_KEY = "87988-a6fd295a556dbdb47960ec60"


@click.group()
@click.version_option()
def cli():
    "Save Pocket data to a SQLite database"


@cli.command()
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to save tokens to, defaults to auth.json",
)
def auth(auth):
    "Save authentication credentials to a JSON file"
    response = requests.post(
        "https://getpocket.com/v3/oauth/request",
        {
            "consumer_key": CONSUMER_KEY,
            "redirect_uri": "https://getpocket.com/connected_applications",
        },
    )
    request_token = dict(urllib.parse.parse_qsl(response.text))["code"]
    click.echo("Visit this page and sign in with your Pocket account:\n")
    click.echo(
        "https://getpocket.com/auth/authorize?request_token={}&redirect_uri={}\n".format(
            request_token, "https://getpocket.com/connected_applications"
        )
    )
    input("Once you have signed in there, hit <enter> to continue")
    # Now exchange the request_token for an access_token
    response2 = requests.post(
        "https://getpocket.com/v3/oauth/authorize",
        {"consumer_key": CONSUMER_KEY, "code": request_token},
    )
    codes = dict(urllib.parse.parse_qsl(response2.text))
    codes["consumer_key"] = CONSUMER_KEY
    open(auth, "w").write(json.dumps(codes, indent=4) + "\n")
    click.echo("Authentication tokens written to {}".format(auth))


@cli.command()
@click.argument(
    "db_path",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.option(
    "-a",
    "--auth",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    default="auth.json",
    help="Path to auth tokens, defaults to auth.json",
)
@click.option("-s", "--silent", is_flag=True, help="Don't show progress bar")
def fetch(db_path, auth, silent):
    "Save Pocket data to a SQLite database"
    auth = json.load(open(auth))
    items = utils.fetch_all_items(auth)
    db = sqlite_utils.Database(db_path)
    # TODO: Progress bar if not silent
    utils.save_items(items, db)
    utils.ensure_fts(db)
