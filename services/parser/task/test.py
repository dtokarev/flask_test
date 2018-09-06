import unittest

from coverage import coverage

from . import cli


@cli.command()
def test():
    """Run all tests"""
    tests = [unit, functional]

    for t in tests:
        if not t():
            return 1

    return 0


@cli.command()
def test_unit():
    """Run all unit tests"""
    return 0 if unit() else 1


@cli.command()
def test_fun():
    """Run all unit tests"""
    return 0 if functional() else 1


def unit():
    tests = unittest.TestLoader().discover('test/unit', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    return result.wasSuccessful()


def functional():
    tests = unittest.TestLoader().discover('test/functional', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    return result.wasSuccessful()


@cli.command()
def cov():
    """Runs the unit tests with coverage."""
    cov = coverage(
        branch=True,
        include='project/*',
        omit=[
            'project/test/*',
            'project/config.py',
        ]
    )
    cov.start()

    result = unit()

    if result:
        cov.stop()
        cov.save()
        print('Coverage Summary:')
        cov.report()
        # cov.html_report()
        cov.erase()
        return 0
    return 1