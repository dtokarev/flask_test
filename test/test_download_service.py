from nose.tools import assert_in, assert_equal

from app_parser.service import download_service


def test_service():
    download_service.forget_all_downloads()

    download_service.remember_download(1)
    download_service.remember_download(2)
    download_service.remember_download(2)
    download_service.remember_download(3)

    ids = download_service.get_all_downloads()
    assert_equal(3, len(ids))
    assert_in(3, ids)
