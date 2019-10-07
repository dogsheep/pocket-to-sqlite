from pocket_to_sqlite import utils
import pytest
import json
import sqlite_utils
from sqlite_utils.db import ForeignKey
import pathlib


def load():
    json_path = pathlib.Path(__file__).parent / "pocket.json"
    return json.load(open(json_path, "r"))


@pytest.fixture(scope="session")
def converted():
    db = sqlite_utils.Database(":memory:")
    utils.save_items(load(), db)
    utils.ensure_fts(db)
    return db


def test_tables(converted):
    assert {
        "items_authors",
        "items_fts",
        "authors",
        "items",
        "items_fts_config",
        "items_fts_idx",
        "items_fts_data",
        "items_fts_docsize",
    } == set(converted.table_names())


def test_item(converted):
    item = list(converted["items"].rows)[0]
    assert {
        "item_id": 2746847510,
        "resolved_id": 2746847510,
        "given_url": "http://people.idsia.ch/~juergen/deep-learning-miraculous-year-1990-1991.html",
        "given_title": "Deep Learning: Our Miraculous Year 1990-1991",
        "favorite": 0,
        "status": 0,
        "time_added": 1570303854,
        "time_updated": 1570303854,
        "time_read": None,
        "time_favorited": None,
        "sort_id": 206,
        "resolved_title": "Deep Learning: Our Miraculous Year 1990-1991",
        "resolved_url": "http://people.idsia.ch/~juergen/deep-learning-miraculous-year-1990-1991.html",
        "excerpt": "The Deep Learning (DL) Neural Networks (NNs) of our team have revolutionised Pattern Recognition and Machine Learning, and are now heavily used in academia and industry [DL4].",
        "is_article": 1,
        "is_index": 0,
        "has_video": 0,
        "has_image": 1,
        "word_count": 11415,
        "lang": "en",
        "time_to_read": 52,
        "top_image_url": "http://people.idsia.ch/~juergen/miraculous-year754x395.png",
        "image": '{"item_id": "2746847510", "src": "http://people.idsia.ch/~juergen/lstmagfa288.gif", "width": "0", "height": "0"}',
        "images": '{"1": {"item_id": "2746847510", "image_id": "1", "src": "http://people.idsia.ch/~juergen/lstmagfa288.gif", "width": "0", "height": "0", "credit": "", "caption": ""}, "2": {"item_id": "2746847510", "image_id": "2", "src": "http://people.idsia.ch/~juergen/deepoverview466x288-6border.gif", "width": "0", "height": "0", "credit": "", "caption": ""}}',
        "listen_duration_estimate": 4419,
    } == item


def test_authors(converted):
    authors = list(converted["authors"].rows)
    assert [
        {
            "author_id": 120590166,
            "name": "Link.",
            "url": "http://people.idsia.ch/~juergen/heatexchanger/heatexchanger.html",
        }
    ] == authors
