from util import *
from word_defs import WordDefs
import pytest


LIST_0 = lambda: [1, 2, 3, 4, 5, 6]


def test_move_hz():
    l = LIST_0()
    with pytest.raises(ValueError):
        move_element_in_list(l, 5, 'hz')
    with pytest.raises(IndexError):
        move_element_in_list(l, 100, 'up')
    with pytest.raises(IndexError):
        move_element_in_list(l, -1, 'up')


def test_move_up():
    l = LIST_0()
    l = move_element_in_list(l, 0, 'up')
    assert l == LIST_0()

    l = LIST_0()
    l = move_element_in_list(l, 1, 'up')
    assert l == [2, 1, 3, 4, 5, 6]

    l = LIST_0()
    l = move_element_in_list(l, 5, 'up')
    assert l == [1, 2, 3, 4, 6, 5]

    l = LIST_0()
    l = move_element_in_list(l, 3, 'up')
    assert l == [1, 2, 4, 3, 5, 6]


def test_move_down():
    l = LIST_0()
    l = move_element_in_list(l, 0, 'down')
    assert l == [2, 1, 3, 4, 5, 6]

    l = LIST_0()
    l = move_element_in_list(l, 4, 'down')
    assert l == [1, 2, 3, 4, 6, 5]

    l = LIST_0()
    l = move_element_in_list(l, 5, 'down')
    assert l == LIST_0()


def test_move_bottom():
    l = LIST_0()
    l = move_element_in_list(l, 5, 'bottom')
    assert l == LIST_0()

    l = LIST_0()
    l = move_element_in_list(l, 0, 'bottom')
    assert l == [2, 3, 4, 5, 6, 1]

    l = LIST_0()
    l = move_element_in_list(l, 2, 'bottom')
    assert l == [1, 2, 4, 5, 6, 3]


def test_move_top():
    l = LIST_0()
    l = move_element_in_list(l, 0, 'top')
    assert l == LIST_0()

    l = LIST_0()
    l = move_element_in_list(l, 4, 'top')
    assert l == [5, 1, 2, 3, 4, 6]

    l = LIST_0()
    l = move_element_in_list(l, 5, 'top')
    assert l == [6, 1, 2, 3, 4, 5]


@pytest.fixture()
def an_empty_word_def():
    word = 'эйлерс'
    r = get_redis()
    wd = WordDefs(r, word)
    wd.delete()
    yield WordDefs(r, word)
    wd.delete()


@pytest.fixture()
def redis_db():
    return get_redis()


def test_add_defs(an_empty_word_def: WordDefs):
    wd = an_empty_word_def
    wd.append_word_defs([
        {
            'text': 'магазинчик еды ололо',
            'imageURL': 'https://sun1-30.userapi.com/MDG7sfdXSkuD_6QtIhONI24931_SmcR3r8prpA/0D2GyafId-0.jpg'
        },
        {
            'text': 'принцип кино - больше сцен',
        }
    ])
    defs = wd.load_defs()
    assert len(defs) == 2
    assert defs[0]['text'] == 'магазинчик еды ололо'
    assert defs[1]['text'] == 'принцип кино - больше сцен'

    wd.load_defs(forced=True)

    assert len(defs) == 2
    assert defs[0]['text'] == 'магазинчик еды ололо'
    assert defs[1]['text'] == 'принцип кино - больше сцен'


def test_ve(redis_db):
    wd = WordDefs(redis_db, 'ВЕ')
    wd.append_word_defs([
        {
            'text': 'efflj weflej lwefj jwelfjwe flewjf wlfjwelj fweflw fjlwe'
        }
    ])