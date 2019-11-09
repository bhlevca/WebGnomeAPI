.. keywords
   currents, movers, CATS, hyrodynamic model
   
The **Name** by default is set from the uploaded file name. 

Set **Reference Point Scaling** to on to scale the currents. The scaling will be applied unfiformly across the grid based on the value specified at the reference point.

Setting the "Reference Point Value" will determine what scale to apply such that the currents at the reference point are exactly equal to that value. This is a steady state pattern. If a **Tide** file is loaded, this option will change to **Tide File Value Multiplied By**. Set this to 1 if you want the value to be exactly the value in the tide file. You can also scale the currents up or down or reverse using a negative value. 

The **Scale Reference Point** is entered as (longitude,latitude,0) or use the button to select on a map.

The button to the right of the **Tide** input box is used to select a tide file. The format is described in the |file_formats_link|.

.. |file_formats_link| raw:: html

   <a href="https://response.restoration.noaa.gov/oil-and-chemical-spills/oil-spills/response-tools/gnome-references.html#dataformats" target="_blank">GNOME supported file formats document</a>