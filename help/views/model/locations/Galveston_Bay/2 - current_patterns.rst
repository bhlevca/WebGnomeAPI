Current Patterns
==========================================

The Location File for Galveston Bay contains six current patterns. All current patterns were created with the NOAA Current Analysis for Trajectory Simulations (CATS) hydrodynamic model.

**1. Tidal Flow**

Tides dominate the circulation within Galveston Bay and are represented in the Location File with a current pattern driven by the tide station at Bolivar Roads, 0.5 miles north of Ft. Point (28° 20.80'N, 94° 46.10'W).

**2. River Flows**

During high runoff periods, river input is also important in driving the Galveston Bay circulation. Three main tributaries of the bay are simulated in this Location File: the Trinity River, the San Jacinto River, and Buffalo Bayou. The Trinity River is simulated as a single current pattern, while the San Jacinto River and Buffalo Bayou inputs are combined into one current pattern. Each of the river flow rates is calculated from the transport rates or stage heights that the GNOME user enters. Stage height is converted to flow rate through rating curves provided by the U.S. Geological Survey (USGS). Formulae for the conversions are detailed below. All flow calculation results are calculated in cubic feet/second (cfs) and all stage height data are assumed to be in feet.

**(a) Trinity River**
A 9th order polynomial fit to the rating curve yielded the following equation relating Trinity River flow rate, , to stage height near Liberty, Texas (station 08067000), .



The calculated flow rate is used to scale the Trinity River current pattern.

**(b) San Jacinto River and Buffalo Bayou**
A 7th order polynomial fit to the rating curve yielded the following equation relating San Jacinto River flow rate, , to stage height near Sheldon, Texas (station 08072050), .



A 7th order polynomial fit to the rating curve yielded the following equation relating Buffalo Bayou flow rate, , to stage height at Houston, Texas (station 08074000), .



The flow rates for the San Jacinto River and Buffalo Bayou are combined and then converted to a scaling coefficient.

**3. Wind Driven Currents (2 current patterns)**

Wind driven currents are simulated by a linear combination of two current patterns scaled by the wind stress. One pattern was calculated with a NW wind and the other with a NE wind. 

**4. P.H. Robinson Power Plant Circulation**

The small circulation driven by the P.H. Robinson power plant flow-through circulation at San Leon is simulated by a current pattern in the Location File. Flow data were provided by Reliant Energy, which operates the P.H. Robinson facility. Permitted flow from the plant is 75.7 m3/s. For 1998 and 1999, the maximum flow was 74.6 m3/s, with an average flow of 57.4 m3/s. The average flow rate (57.4 m3/s) was used to scale the current pattern.

**5. Offshore Circulation**

An offshore circulation pattern was derived assuming a barotropic setup. The offshore circulation pattern is scaled by the alongshore (55° True) component of the offshore velocity entered by the GNOME user.