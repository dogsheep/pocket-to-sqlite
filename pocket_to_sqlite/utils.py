import datetime
import requests
import json
import time
from sqlite_utils.db import AlterError, ForeignKey


def save_items(items, db):
    for item in items:
        transform(item)
        authors = item.pop("authors", None)
        items_authors_to_save = []
        if authors:
            authors_to_save = []
            for details in authors.values():
                authors_to_save.append(
                    {
                        "author_id": int(details["author_id"]),
                        "name": details["name"],
                        "url": details["url"],
                    }
                )
                items_authors_to_save.append(
                    {
                        "author_id": int(details["author_id"]),
                        "item_id": int(details["item_id"]),
                    }
                )
            db["authors"].insert_all(authors_to_save, pk="author_id", replace=True)
        db["items"].insert(item, pk="item_id", alter=True, replace=True)
        if items_authors_to_save:
            db["items_authors"].insert_all(
                items_authors_to_save,
                pk=("author_id", "item_id"),
                foreign_keys=("author_id", "item_id"),
                replace=True
            )


def transform(item):
    for key in (
        "item_id",
        "resolved_id",
        "favorite",
        "status",
        "time_added",
        "time_updated",
        "time_read",
        "time_favorited",
        "is_article",
        "is_index",
        "has_video",
        "has_image",
        "word_count",
        "time_to_read",
        "listen_duration_estimate",
    ):
        if key in item:
            item[key] = int(item[key])

    for key in ("time_read", "time_favorited"):
        if key in item and not item[key]:
            item[key] = None


def ensure_fts(db):
    if "items_fts" not in db.table_names():
        db["items"].enable_fts(["resolved_title", "excerpt"], create_triggers=True)


def fetch_stats(auth):
    response = requests.get(
        "https://getpocket.com/v3/stats",
        {
            "consumer_key": auth["pocket_consumer_key"],
            "access_token": auth["pocket_access_token"],
        },
    )
    response.raise_for_status()
    return response.json()


class FetchItems:
    def __init__(self, auth, since=None, page_size=500, sleep=2, retry_sleep=3, record_since=None):
        self.auth = auth
        self.since = since
        self.page_size = page_size
        self.sleep = sleep
        self.retry_sleep = retry_sleep
        self.record_since = record_since

    def __iter__(self):
        offset = 0
        retries = 0
        while True:
            args = {
                "consumer_key": self.auth["pocket_consumer_key"],
                "access_token": self.auth["pocket_access_token"],
                "sort": "oldest",
                "state": "all",
                "detailType": "complete",
                "count": self.page_size,
                "offset": offset,
            }
            if self.since is not None:
                args["since"] = self.since
            response = requests.get("https://getpocket.com/v3/get", args)
            if response.status_code == 503 and retries < 5:
                print("Got a 503, retrying...")
                retries += 1
                time.sleep(retries * self.retry_sleep)
                continue
            else:
                retries = 0
            response.raise_for_status()
            page = response.json()
            items = list((page["list"] or {}).values())
            next_since = page["since"]
            if self.record_since and next_since:
                self.record_since(next_since)
            if not items:
                break
            yield from items
            offset += self.page_size
            if self.sleep:
                time.sleep(self.sleep)
