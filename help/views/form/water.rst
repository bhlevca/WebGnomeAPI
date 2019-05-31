.. keywords
   water, salinity, temperature, density, sediment, wave height, fetch

Water Properties
^^^^^^^^^^^^^^^^

Both salinity and temperature are needed to determine the density of seawater. Density is a major factor in determining whether an oil will float or sink. Salinity and Sediment load can play a role in OSA formation.

Water Temperature is can be set in multiple units. If you have no idea, you can often find data fr the US from at the `National Data Buoy Center <https://www.ndbc.noaa.gov/>`_.
* Enter a water temperature and select units from the drop-down menu.

* Select an approximate salinity value in Practical Salinity Units (PSU) from the drop-down menu or enter a custom value.

* Select an approximate water sediment load (mg/L) from the drop-down menu or enter a custom value.

The wave climate drives the dispersion process. You can either have the wave climate computed from the wind or specify a known wave significant wave height. If computing from the Wind, you can specify the `fetch <https://en.wikipedia.org/wiki/Fetch_(geography)>`_. GNOME defaults to unlimited fetch -- if yu specify a fetch, it will limit the wave energy, and thus result in smaller dispersion.

* If you select Compute from Wind and Fetch, enter a value for Fetch and select the units from the drop-down menu. If you select Known Wave Height, enter a value for height and select the units.

* Click Save.

Some water properties data sources:

|location_link1|

.. |location_link1| raw:: html

   <a href="https://www.nodc.noaa.gov/dsdt/cwtg/" target="_blank">NOAA Coastal Waters Temperature Guide</a>