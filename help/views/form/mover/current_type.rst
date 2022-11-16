.. keywords
   currents, movers, roms, fvcom, cats, hyrodynamic model

Choose **Load NetCDF Surface Currents** to load ocean current data or model output on a regular, curvilinear, or triangular grid in NetCDF format. 
At present, only specific output formats are supported (eventually any CF-compliant file with the necessary variables should be compatible). Typical output from ROMS or any UGRID/SGRID compliant format should be supported. 

"WebGNOME-ready" files for some publicly available models can also be downloaded from |goods_link|.

The **Load NOAA Emergency Response Model (CATS) output** is for loading the hydrodynamic model used by the NOAA Emergency Response Division. 

To select currents from available operational ocean models, choose **Select Currents for Specified Region**. Note, this feature is under active development and may be unreliable.

Choose **Load Deprecated ASCII Formats** for files using the PtCur, GridCur, or GridCurTime formats.

For more information on any of these formats, see the |file_formats_link|.

.. |file_formats_link| raw:: html

   <a href="https://response.restoration.noaa.gov/oil-and-chemical-spills/oil-spills/response-tools/gnome-references.html#dataformats" target="_blank">GNOME supported file formats document</a>

.. |goods_link| raw:: html

   <a href="https://gnome.orr.noaa.gov/goods" target="_blank">the GNOME Data Server (GOODS)</a>
