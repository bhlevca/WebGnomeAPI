"""
Defines conftest for pytest.
The scope="module" on the fixtures ensures it is only invoked once per
test module
"""
import pytest


def pytest_addoption(parser):
    '''
        Place configuration options that apply to all tests here:
        --skipslow
          tests that have the @pytest.mark.slow decorator will be skipped

    '''
    parser.addoption('--skipslow', action='store_true', help='skip slow tests')


def pytest_runtest_setup(item):
    '''
    pytest builtin hook

    This is executed before pytest_runtest_call.
    pytest_runtest_call is invoked to execute the test item.
    So the code in here is executed before each test.
    '''
    if ('slow' in item.keywords and
        item.config.getoption('--skipslow')):
        pytest.skip('--skipslow option skipped this test')
