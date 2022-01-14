"""
tests for the libgoods module

NOTE: these are very fragile, and the whole thing needs refactoring

But as a start ...

And to have a way to run the code and document the API

uncomment the skip if it's causing issues
"""



import libgoods
import pytest


@pytest.mark.skip
def test_get_map():
    """
    A single map request

    NOTE: this, at some point, will no longer be a request
    """
    filename, contents = libgoods.get_map(north_lat=47.06693175688763,
                                          south_lat=46.78488364986247,
                                          west_lon=-124.26942110656861,
                                          east_lon=-123.6972360021842,
                                          resolution='i',
                                          cross_dateline=False,
                                          )

    assert filename == 'coast.bna'
    assert len(contents) > 0
    assert contents[:12] == '"Map Bounds"'



