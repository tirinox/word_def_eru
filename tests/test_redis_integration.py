import os
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests
from redis import Redis

from word_defs import WordDefs
from word_permutation import WordPermutations
from word_usage import WordUsage


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.environ.get("RUN_REDIS_INTEGRATION") != "1",
        reason="requires the isolated Redis integration environment",
    ),
]


@pytest.fixture()
def redis_db():
    database = Redis(
        host=os.environ["REDIS_HOST"],
        port=int(os.environ.get("REDIS_PORT", "6379")),
        db=int(os.environ.get("REDIS_DB", "0")),
        decode_responses=True,
    )
    database.ping()
    database.flushdb()
    yield database
    database.flushdb()


def test_concurrent_definition_updates_do_not_lose_data(redis_db):
    def add_definition(number):
        return WordDefs(redis_db, "CONCURRENT").append_word_defs({
            "text": f"concurrent definition number {number:03d}",
        })

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(add_definition, range(40)))

    definitions = WordDefs(redis_db, "CONCURRENT")
    definitions.load_defs()
    assert all(results)
    assert len(definitions.get_defs()) == 40
    assert {item["text"] for item in definitions.get_defs()} == {
        f"concurrent definition number {number:03d}" for number in range(40)
    }


def test_concurrent_usage_updates_keep_the_global_maximum(redis_db):
    first = WordUsage(redis_db, "FIRST")
    second = WordUsage(redis_db, "SECOND")
    usages = [first, second] * 100

    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(lambda usage: usage.increment_word_usage(), usages))

    assert first.get_word_usage_count() == 100
    assert second.get_word_usage_count() == 100
    assert first.get_max_usage() == 100


def test_concurrent_score_updates_keep_the_highest_score(redis_db):
    def update_score(score):
        WordUsage(redis_db, "SCORE").update_max_score(score, score)

    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(update_score, range(1, 101)))

    assert WordUsage(redis_db, "SCORE").get_best_profile_id_and_score() == (100, 100)


def test_containerized_gunicorn_api(redis_db):
    service_url = os.environ["SERVICE_URL"]

    welcome = requests.get(f"{service_url}/", timeout=3)
    assert welcome.status_code == 200
    assert welcome.text == "Welcome to word_def!"

    added = requests.post(
        f"{service_url}/add",
        json={"word": "compose", "defs": [{"text": "compose definition"}]},
        timeout=3,
    )
    assert added.status_code == 200
    assert added.json() == {"was_definition_added": True, "result": "ok"}

    definitions = requests.get(f"{service_url}/defs/compose", timeout=3)
    assert definitions.status_code == 200
    assert definitions.json()["defs"] == [
        {"text": "compose definition", "dic": "internal", "id": 0}
    ]

    permutations = WordPermutations(redis_db, "RUS")
    permutations.add_to_list("WORD", 10, 4)
    sampled = requests.get(f"{service_url}/permuts/RUS/4/%3C5", timeout=3)
    assert sampled.status_code == 200
    assert sampled.json() == {
        "permuts": [{"word": "WORD", "rating": 10, "variants": 4}],
        "result": "ok",
    }
