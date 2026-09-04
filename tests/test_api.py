import pytest

import server
from tests.fake_redis import FakeRedis
from word_defs import WordDefs
from word_permutation import WordPermutations
from word_usage import WordUsage


@pytest.fixture()
def redis_db():
    return FakeRedis()


@pytest.fixture()
def client(monkeypatch, redis_db):
    monkeypatch.setattr(server, "redis_db", redis_db)
    server.app.config.update(TESTING=True)
    return server.app.test_client()


def test_definition_round_trip_and_legacy_storage(redis_db):
    definitions = WordDefs(redis_db, " test ")
    assert definitions.append_word_defs([
        {"text": "first definition", "dic": "internal"},
        {"text": "second definition", "imageURL": "https://example.test/image.png"},
    ]) is True

    assert definitions.get_defs() == [
        {"text": "first definition", "dic": "internal", "id": 0},
        {
            "text": "second definition",
            "imageURL": "https://example.test/image.png",
            "dic": "internal",
            "id": 1,
        },
    ]
    assert definitions.append_word_defs({"text": "first definition"}) is False

    legacy = WordDefs(redis_db, "legacy")
    redis_db.set(legacy.word_def_key(), '[{"text": "legacy definition"}]')
    assert legacy.load_defs() == [{"text": "legacy definition"}]


def test_definition_edit_move_and_remove(redis_db):
    definitions = WordDefs(redis_db, "word")
    definitions.append_word_defs([
        {"text": "first definition"},
        {"text": "second definition"},
    ])

    definitions.move_def(1, "top")
    definitions.update_def(0, {"text": "updated definition"})
    definitions.remove_def(1)

    assert definitions.get_defs() == [
        {"text": "updated definition", "dic": "internal", "id": 0}
    ]


def test_word_usage_preserves_rate_and_best_score_rules(redis_db):
    usage = WordUsage(redis_db, "WORD")
    assert usage.to_json() == {
        "word": "WORD",
        "usage": 0,
        "rate": 0.0,
        "best": {"profile_id": 0, "score": 0},
    }

    usage.increment_word_usage()
    assert redis_db.get(WordUsage.KEY_MAX_WORD_USAGE) == "1"
    usage.update_max_score(10, 20)
    usage.update_max_score(11, 20)

    result = usage.to_json()
    assert result["usage"] == 1
    assert result["rate"] == 100.0
    assert result["best"] == {"profile_id": 10, "score": 20}


def test_permutation_storage_and_sampling(monkeypatch, redis_db):
    permutations = WordPermutations(redis_db, "RUS")
    permutations.add_to_list("WORD", 10, 4)
    permutations.add_to_list("TEST", 20, 4)
    items = list(permutations.get_all_from_bucket(4, "< 5"))

    monkeypatch.setattr("word_permutation.random.sample", lambda values, size: values[:size])
    assert permutations.subsample(items, 2) == [
        {"word": "TEST", "rating": 20, "variants": 4},
        {"word": "WORD", "rating": 10, "variants": 4},
    ]


def test_permutation_bucket_boundaries_do_not_overlap(redis_db):
    permutations = WordPermutations(redis_db)

    assert permutations.bucket_from_variant_count(50) == "41-50"
    assert permutations.bucket_from_variant_count(51) == "51-75"


def test_underfilled_permutation_bucket_returns_all_available_items(redis_db):
    permutations = WordPermutations(redis_db)
    permutations.add_to_list("WORD", 10, 4)

    assert permutations.subsample(
        permutations.get_all_from_bucket(4, "<5"), 2
    ) == [{"word": "WORD", "rating": 10, "variants": 4}]


@pytest.mark.parametrize("content", [None, [], {}, {"word": None}, {"word": "x"}])
def test_invalid_word_input_uses_historical_error(content):
    from util import get_word_from_request

    with pytest.raises(Exception, match="invalid word"):
        get_word_from_request(content)


@pytest.mark.parametrize(
    ("definition", "message"),
    [
        ({"text": "too short"}, "invalid definition text"),
        ({"text": "x" * 513}, "invalid definition text"),
        ({"text": "valid definition", "dic": "x" * 256}, "invalid dictionary name"),
        ({"text": "valid definition", "imageURL": "x" * 1024}, "invalid image URL"),
    ],
)
def test_definition_limits_are_enforced_without_assert(redis_db, definition, message):
    with pytest.raises(Exception, match=message):
        WordDefs(redis_db, "word").append_word_defs(definition)


def test_api_definition_and_usage_response_shapes(client):
    add_response = client.post("/add", json={
        "word": "test",
        "defs": [{"text": "test definition"}],
    })
    assert add_response.status_code == 200
    assert add_response.get_json() == {
        "was_definition_added": True,
        "result": "ok",
    }

    definitions_response = client.get("/defs/test")
    assert definitions_response.status_code == 200
    assert definitions_response.get_json() == {
        "word": "TEST",
        "usage": 0,
        "rate": 0.0,
        "best": {"profile_id": 0, "score": 0},
        "defs": [{"text": "test definition", "dic": "internal", "id": 0}],
        "result": "ok",
    }

    usage_response = client.get("/use/test/by/7/score/42")
    assert usage_response.status_code == 200
    assert usage_response.get_json() == {
        "word": "TEST",
        "usage": 1,
        "rate": 100.0,
        "best": {"profile_id": 7, "score": 42},
        "result": "ok",
    }


def test_api_error_envelope_is_unchanged(client):
    response = client.post("/add", json={"word": "x", "defs": []})

    assert response.status_code == 500
    assert response.get_json() == {"result": "error", "message": "invalid word"}


def test_invalid_definition_keeps_historical_500_status(client):
    response = client.post("/add", json={
        "word": "test",
        "defs": [{"text": "too short"}],
    })

    assert response.status_code == 500
    assert response.get_json() == {
        "result": "error",
        "message": "invalid definition text",
    }


def test_empty_permutation_api_response(client):
    response = client.get("/permuts/RUS/4/%3C5")

    assert response.status_code == 200
    assert response.get_json() == {"permuts": [], "result": "ok"}


def test_underfilled_permutation_api_returns_available_items(client, redis_db):
    WordPermutations(redis_db, "RUS").add_to_list("WORD", 10, 4)

    response = client.get("/permuts/RUS/4/%3C5")

    assert response.status_code == 200
    assert response.get_json() == {
        "permuts": [{"word": "WORD", "rating": 10, "variants": 4}],
        "result": "ok",
    }
