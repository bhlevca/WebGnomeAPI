.. keywords
   winds, movers, GFS, NAM, meteorological

Choose **Load Wind** to load wind data on a regular or curvilinear grid (e.g. output from a meteorological model). 
At present, only specific file formats are supported (eventually any CF-compliant file should be compatible). Details on the 
supported file formats can be found in the |location_link|. 

Winds will be used both to move particles (based on windage parameter) and for oil weathering calculations if desired. Note, that if multiple winds are created or loaded (including both Point Winds and/or Gridded winds) the **first** one that was added to the model will be used for weathering calculations. The "active" checkbox applies ONLY to transport.

"WebGNOME-ready" files for some publically available models can also be downloaded from |location_link2|.


.. |location_link| raw:: html

   <a href="https://response.restoration.noaa.gov/oil-and-chemical-spills/oil-spills/response-tools/gnome-references.html#dataformats" target="_blank">supported file formats document</a>

.. |location_link2| raw:: html

   <a href="https://gnome.orr.noaa.gov/goods" target="_blank">the GNOME Data Server (GOODS)</a>

