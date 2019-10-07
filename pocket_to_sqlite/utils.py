import datetime
import requests
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
        db["authors"].upsert_all(authors_to_save, pk="author_id")
    db["items"].upsert_all(items, pk="item_id", alter=True)
    db["items_authors"].upsert_all(
        items_authors_to_save,
        pk=("author_id", "item_id"),
        foreign_keys=("author_id", "item_id"),
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
        item[key] = int(item[key])

    for key in ("time_read", "time_favorited"):
        if not item[key]:
            item[key] = None


def ensure_fts(db):
    if "items_fts" not in db.table_names():
        db["items"].enable_fts(["resolved_title", "excerpt"], create_triggers=True)
