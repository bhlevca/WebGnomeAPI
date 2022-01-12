"""
placeholder / mockup for libgoods

For the moment, this is where we will define the interaction between the
webgnome_api and libgoods.
"""

import urllib

GOODS_URL = 'https://gnome.orr.noaa.gov/goods/'


def get_map(north_lat,
            south_lat,
            west_lon,
            east_lon,
            resolution='appropriate',
            cross_dateline=False,
            ):

    # some error checking:
    if north_lat > 90:
        raise ValueError(f'latitude cannot be larger than 90. Got{north_lat}')
    # lots more to be done here


    # this is what the current GOODS API requires
    req_params = {'err_placeholder':'',
                  'NorthLat': north_lat,
                  'WestLon': west_lon,
                  'EastLon': east_lon,
                  'SouthLat': south_lat,
                  'xDateline': int(cross_dateline),
                  'resolution': 'i',
                  'submit': 'Get Map',
                  }

    query_string = urllib.parse.urlencode(req_params)
    data = query_string.encode( "ascii" )

# url = url + "?" + query_string

# with urllib.request.urlopen( url ) as response:
#     response_text = response.read()
#     print( response_text )

    goods_resp = urllib.request.urlopen(GOODS_URL + 'tools/GSHHS/coast_extract',
                                        data)


    return goods_resp



