Current Patterns
======================================

The currents in the entrance to Panama Canal are primarily tidally driven -- the tidal currents are simulated with a flood current pattern tied to the tide station at Balboa, near the Bridge of the Americas. 

Outside the entrance to the canal, there is a coastal current in the Bay of Panama that is driven by the circulation in the greater Gulf of Panama. The current pattern simulated in GNOME captures the flow as modified by the local shoreline and bathymetry. But the overall strength of the flow is determined by the larger scale circulation in the Gulf of Panama. Typically, the flow is counter-clockwise, and about 0.4 knots (0.2 m/s) at the scaling location, located at:   8.7534°N--79.6358°W.

The coastal current is not driven by local consitions, but rather by the circulation in the Gulf of Panama. While 
global circulation models do not have high enough resolution to capture the flow in the Bay of Panama, they do capture the general flow in the Gulf of Panama, and can be used to scale the local current pattern.

One source of results from global circulation model is the |ioos_link|. There are currently two global models accessible through that system: The US Navy Global Ocean Forecast System (GOFS), and the NOAA Real Time Ocean Forecast System (RTOFS). The results from these models can be selected in the IOOS EDS Viewer, and the predicted velocities at a specified point can be determined. The GNOME coastal current scale should be set to the approximate value near the location: 8.75°N--79.64°W.

Note that the current pattern is set for a counter-clockwise circulation, so that the direction of flow at the reference point is to the SSW. If the global model predicts flow in the opposite direction (NNE), the value can be set to a negative number to simulate a clockwise flow in the Bay of Panama.


The current patterns were created with the NOAA Current Analysis for Trajectory Simulation (CATS) hydrodynamic application.

.. |ioos_link| raw:: html

   <a href="https://eds.ioos.us/map" target="_blank">NOAA IOOS EDS</a>

