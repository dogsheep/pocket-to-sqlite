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
    open(auth, "w").write(
        json.dumps(
            {
                "pocket_consumer_key": CONSUMER_KEY,
                "pocket_username": codes["username"],
                "pocket_access_token": codes["access_token"],
            },
            indent=4,
        )
        + "\n"
    )
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
@click.option("-a", "--all", is_flag=True, help="Fetch all items (not just new ones)")
@click.option("-s", "--silent", is_flag=True, help="Don't show progress bar")
def fetch(db_path, auth, all, silent):
    "Save Pocket data to a SQLite database"
    auth = json.load(open(auth))
    db = sqlite_utils.Database(db_path)
    last_since = None
    if not all and db["since"].exists():
        last_since = db["since"].get(1)["since"]
    fetch = utils.FetchItems(auth, since=last_since, record_since=lambda since: db["since"].insert({
        "id": 1,
        "since": since
    }, replace=True, pk="id"))
    if (all or last_since is None) and not silent:
        total_items = utils.fetch_stats(auth)["count_list"]
        with click.progressbar(fetch, length=total_items) as bar:
            utils.save_items(bar, db)
    else:
        # No progress bar
        print("Fetching items since {}".format(last_since))
        utils.save_items(fetch, db)
    utils.ensure_fts(db)
