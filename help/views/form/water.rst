.. keywords
   water, salinity, temperature, density, sediment, wave height, fetch

Water Properties
^^^^^^^^^^^^^^^^

Both salinity and temperature are needed to determine the density of seawater. Density is a major factor in determining whether an oil will float or sink. 

Water Temperature is can be set in multiple units. If you have no idea, you can often find data fr the US from at the `National Data Buoy Center <https://www.ndbc.noaa.gov/>`_.
* Enter a water temperature and select units from the drop-down menu.

* Select an approximate salinity value in Practical Salinity Units (PSU) from the drop-down menu or enter a custom value.

Sediment load is another process that can affect the behavior of an oil slick. Water with a high sediment load may cause oil to descend into the water column more rapidly, while water with a low sediment load may allow oil to remain on the surface of the water longer. 
* Select an approximate water sediment load (mg/L) from the drop-down menu or enter a custom value.

Wave heights are used to calculate wave energy and to estimate the rate of dispersion of oil from the surface slick into the water column. You can either have the wave climate computed from the wind or specify a known wave significant wave height. If computing from the Wind, you can specify the fetch over which it blows `fetch <https://en.wikipedia.org/wiki/Fetch_(geography)>`_. GNOME defaults to unlimited fetch -- if you specify a fetch, it will limit the wave energy, and thus result in smaller dispersion.

* The default option is if you select Compute from Wind (Unlimited Fetch)
* If you select Compute from Wind and Fetch, enter a value for Fetch and select the units from the drop-down menu. 
* If you select Known Wave Height, enter a value for height and select the units.
* If you select I'm in a River, enter a value for height and select the units. Note the Caution

Some water properties data sources:

|location_link1|

.. |location_link1| raw:: html

   <a href="https://www.nodc.noaa.gov/dsdt/cwtg/" target="_blank">NOAA Coastal Waters Temperature Guide</a>