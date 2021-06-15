.. keywords
   trajectory, zoom, ruler, area, fixed, moving, spill

Map View
^^^^^^^^

This view shows the movement of the particles (oil) along with various basemaps and environmental data (e.g. currents and winds which can be turned on via the **Layers** menu).

**Navigating the Map**

Click and drag with a mouse to pan around the map. A scroll wheel can be used to zoom in and out. If you do not have a scroll wheel, the map can be zoomed by right clicking and dragging.

**Running the trajectory**

The time slider at the top of the screen shows the current displayed time step in the model. Once you click play, a blue progress bar shows the model being run *on the server*. If you pause the run, the model will continue to run but the display time will be paused.

|controls_img|

This is an important distinction because once the model is run on the server the results are cached for display. This means you can drag the display time backwards and forwards to quickly refresh the display. Note that pressing the rewind button will rewind the model on the server, hence losing this cache. To avoid this "hard rewind", simply drag the time indicator back to the beginning of the run to rewind the display only.


.. |controls_img| raw:: html

   <img src="img/trajectory_controls.png">


