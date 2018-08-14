from nose.tools import assert_in, assert_not_in, assert_equal

from app_parser.service import download_service


def test_service():
    download_service.forget_all()
    download_service.remember(1)
    download_service.remember(2)
    download_service.remember(2)
    download_service.remember(3)

    ids = download_service.get_all()

    assert_equal(3, len(ids))
    assert_in(3, ids)

    download_service.forget(3)

    ids = download_service.get_all()
    assert_not_in(3, ids)

