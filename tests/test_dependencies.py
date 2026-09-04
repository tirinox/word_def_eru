from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from fuzzywuzzy import fuzz
from Levenshtein import distance
from PIL import Image
from tqdm import tqdm

import mysql.connector
import redis
import requests


def test_lxml_parser_is_available():
    soup = BeautifulSoup("<html><body><p>definition</p></body></html>", "lxml")

    assert soup.p.text == "definition"


def test_pillow_thumbnail_api_is_compatible():
    image = Image.new("RGB", (1280, 960), color="white")

    image.thumbnail((640, 480))

    assert image.size == (640, 480)


def test_fuzzy_matching_api_is_compatible():
    assert fuzz.token_set_ratio("люблю я спать", "люблю я спать и спать") == 100


def test_redis_and_mysql_connector_imports_are_compatible():
    assert redis.Redis is not None
    assert mysql.connector.connect is not None


def test_http_and_utility_dependency_apis_are_compatible():
    assert isinstance(UserAgent().random, str)
    assert distance("word", "words") == 1
    assert isinstance(requests.Session(), requests.Session)
    assert list(tqdm([1, 2], disable=True)) == [1, 2]
