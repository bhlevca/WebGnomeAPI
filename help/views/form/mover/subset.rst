.. keywords
   subset, model, goods, ofs

The form to the right of the map has options for selecting the download parameters for the model output including the time range, time zone,  and the bounding box for the region of interest. 

**Time options**

The available model output time range is shown at the top of the form in UTC. Any time interval within this range can be selected. The specified **Start Time** and **End Time** will be interpreted as UTC. A "buffer" of 6 hours is added to the specified start/end times as the output time step of the model may not align perfectly with the user specified time. This will ensure model output covers the entire time interval being modeled.

The model output can be converted to a local time zone if desired (using the **Adjust Timezone** option. For example, if the scenario is to be modeled in EST, enter -4 in this box as UTC is 4 hours ahead of Eastern Standard.

**Bounding box**

The model domain (for non-global models) is displayed on the map. The bounding box of the region of interest can be specifed either by clicking and dragging a rectangle on the map (release mouse button to draw the rectangle) or specify latitude and longitude values in the form for **West**, **North**, **East**, and **South** boundaries. If a map has been added to the model, the bounding box of the map is selected by default.



**Additional options**

* To download only surface currents, check **Surface Only** . At present, this is always checked as the 3-D currents are not (yet) utilized in WebGNOME.

* To download a map matching the selected region (rectangle) and add it to the model, check **Include Map**. This will replace any existing map previously added.

* If the ocean model output includes surface winds, an option to **Include Winds** will be available. If checked, winds will be included in the download and a wind mover will be created simulanteously with the currents.




