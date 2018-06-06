from nose.tools import *


def test_search_generate_keyword_set():
    from app.utils.search import generate_keywords

    keys = generate_keywords('some movie name')
    assert_list_equal(['some movie name'], keys)

    keys = generate_keywords('some movie name (TV)')
    assert_list_equal(['some movie name (TV)', 'some movie name'], keys)

    keys = generate_keywords('some movie name (TV)', '2010')
    assert_list_equal(['some movie name (TV) 2010', 'some movie name (TV)', 'some movie name'], keys)


def test_unit_converter_size_human_to_float():
    from app.utils.unit_converter import size_human_to_float

    assert_equal(1, size_human_to_float('1 KB', 'KB'))
    assert_equal(1024 * 1024, size_human_to_float('1 GB', 'KB'))
    assert_equal(0.49, size_human_to_float('500 MB', 'GB'))

    assert_equal(0.75, size_human_to_float('807086080 \n 769.7 MB ↓', 'GB'))
    assert_almost_equal(1495, size_human_to_float('807086080 \n 1.46 GB ↓', 'MB'), delta=1)

    assert_raises(ValueError, size_human_to_float, '1 KB', 'XB')
    assert_raises(ValueError, size_human_to_float, '1 XB', 'KB')


def test_unit_converter_duration_human_to_sec():
    from app.utils.unit_converter import duration_human_to_sec

    assert_equal(60, duration_human_to_sec('00:01:00'))
    assert_equal(60, duration_human_to_sec('0:01:00'))
    assert_equal(3700, duration_human_to_sec('01:01:40'))
