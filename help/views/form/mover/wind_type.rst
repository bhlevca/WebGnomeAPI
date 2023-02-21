.. keywords
   winds, movers

Choose **Load NetCDF Winds** to load wind data or model output on a regular, curvilinear, or triangular grid in NetCDF format. 
At present, only specific output formats are supported (eventually any CF-compliant file with the necessary variables should be compatible; see |file_formats_link| for more details.). 

The **Point Wind** option is used to load a single point wind (e.g. a time series of winds from a buoy or a NOAA/NWS point forecast. The wind is then applied uniformly over the entire region being modeled.

Choose the **Select Wind for Specified Region** option to download wind information from a list of available operational models run by NOAA or other agencies. Note, this feature is under active development and may be unreliable.


.. |file_formats_link| raw:: html

   <a href="https://response.restoration.noaa.gov/oil-and-chemical-spills/oil-spills/response-tools/gnome-references.html#dataformats" target="_blank">GNOME supported file formats document</a>

.. |goods_link| raw:: html

   <a href="https://gnome.orr.noaa.gov/goods" target="_blank">the GNOME Data Server (GOODS)</a>
