.. keywords
   wind, nws, constant wind, variable wind, point

Wind
^^^^^

Winds will be used both to move particles (based on windage parameter) and for oil weathering calculations if desired. Note, that if multiple winds are created or loaded (including both Point Winds and/or Gridded winds) the **first** one that was added to the model will be used for weathering calculations. The on/off checkbox applies ONLY to transport.

Note, when entering values use the convention adopted by meteorologists who define wind direction 
as the direction **from** which the wind is blowing. Also, wind speeds are assumed to be at a 10 meter 
reference height above the water surface. 

There are multiple options for adding wind data:

* It can be entered manually as a constant wind value or as a time-series.
* The latest point forecast can be automatically imported from the National Weather Service (NWS) for a specified location. 
* An existing file can be uploaded (|location_link|).

.. |location_link| raw:: html

   <a href="http://response.restoration.noaa.gov/oil-and-chemical-spills/oil-spills/response-tools/gnome-references.html#dataformats" target="_blank">supported file formats document</a>
