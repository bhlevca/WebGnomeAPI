"""
Defines conftest for pytest.
The scope="module" on the fixtures ensures it is only invoked once per
test module
"""
import pytest


# adding a skip slow tests option
# copied from:
# https://docs.pytest.org/en/6.2.x/example/simple.html#control-skipping-of-tests-according-to-command-line-option
def pytest_addoption(parser):
    parser.addoption(
        "--skipslow", action="store_true", default=False, help="skip the slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skipslow"):
        # --skipslow given in cli: skip slow tests
        skip_slow = pytest.mark.skip(reason="need --skipslow option to skip")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

