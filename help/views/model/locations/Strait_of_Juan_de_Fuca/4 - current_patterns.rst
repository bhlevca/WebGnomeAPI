Current Patterns
=================================

The Strait of Juan de Fuca Location File contains five current patterns: a tidal pattern, a surface current reversal pattern at the western entrance to the Strait, a pattern for the local circulation in the Port Angeles area, and one pattern each for flood and ebb tide induced eddies. All current patterns were created with the NOAA Current Analysis for Trajectory Simulation (CATS) hydrodynamic application.


**Tidal Currents**

The tidal current pattern is scaled to the tidal predictions 7.6 miles SSE of Discovery Island, in the eastern Strait of Juan de Fuca (48° 18' N, 123° 10' W). The tidal currents at the Discovery Island station include mean estuarine circulation. 


**Surface Current Reversal**

The surface current reversals at the entrance to the Strait of Juan de Fuca are represented by a current pattern that is scaled in the middle of the western entrance (48° 27' N, 124° 35' W). This pattern is then scaled according to the user-selected entrance conditions. The user's velocity choices include the following::

  Reversal Condition   Velocity (m/s)
       normal		   0.0
        mild		   0.1
      moderate		   0.35
       strong		   0.5

This scaling was estimated from the data presented in Hickey et al., 1991, Holbrook et al., 1980a, and Holbrook et al., 1980b.


**Port Angeles Coastal Flow**

A particular area of concern in this Location File is Port Angeles. In addition to regularly scheduled traffic in the port, tankers may pull into the port while waiting for berths at the refineries in the Anacortes and Bellingham areas. Tidal eddies spin off the tips of both Dungeness Spit and Ediz Hook. Residual tidal currents between Port Angeles and Dungeness Spit result in a mean eastward surface current near the coast, with a convergence zone near the northern end of Dungeness Spit. (Note that Dungeness Spit is also the location of a National Wildlife Refuge).

Different studies have led to different conclusions regarding mean surface currents in Port Angeles Harbor. Ebbesmeyer et al. (1979) concluded that the mean circulation within the harbor itself could not be determined. The complexity of the region, coupled with the potential high spill-risk, have spawned many studies. Surface currents have been analyzed from drift cards, pulp mill effluents, the 1985/86 T/V Arco spill, and a hydraulic model (Ebbesmeyer et al., 1979; Ebbesmeyer et al., 1981; U. S. Coast Guard, 1986).

Surface currents in the Port Angeles eddy pattern are scaled to 0.7 m/s just northeast of Dungeness Spit (48° 10' n, 123° 11' W). The spatial pattern of the Port Angeles eddies are modeled after current patterns presented in Ebbesmeyer et al., 1979, Ebbesmeyer et al., 1981, and the 1986 Port Angeles Arco Anchorage spill (U. S. Coast Guard, 1986). The scaling is based on the experimental runs of the Location File and the time periods for oil transport in the Port Angeles Arco Anchorage spill (U. S. Coast Guard, 1986).


**Eastern Strait Eddies**

The eastern Strait of Juan de Fuca has many eddies. These eddies can significantly alter predictions of surface currents (Ebbesmeyer et al., 1991; C. Ebbesmeyer, personal communication; Mitsuhiro Kuwase, personal communication). The GNOME Location File for the Strait of Juan de Fuca simulates only the major eddies in the eastern straits: #2, #3 and #6 from Ebbesmeyer et al. (1991). Other eddies were considered either too small or their effects were created by the tidal current reversals and current shear. For example, historical data from an oil spill in the Port Angeles area indicated a consistent eastward drift in the currents along the shoreline between Port Angeles and Dungeness Spit. When this is simulated with the reversing tide, the cyclonic circulation resembling Ebbesmeyer et al. s eddy #10 is simulated. Also, the tidal current shear in Haro Strait creates additional mixing that could be interpreted as Ebbesmeyer et al. (1991) eddy #4.

Eddies were simulated in two separate patterns: one for the time period after the maximum flood currents and one for the time period after the maximum ebb currents. Ebbesmeyer et al. (1991) eddies #2 and #6 were simulated for the period after the maximum flood, and eddy # 3 and a version of eddy #6 further offshore (as produced in the University of Washington PRISM circulation model) were simulated in the period after the maximum ebb. A time series was created from the tidal current time series so that the eddy pattern started at zero amplitude at the previous appropriate tidal current maximum, increased to maximum by the next slack water period, and then decreased to zero at the opposite tidal current maximum. This was intended to simulate the eddies spinning up from the momentum of the previous tidal current maximum. The time series was then separated into flood and ebb components and each time series was scaled so that the maximum amplitude was one (1). This allowed us to simulate the currents in the patterns scaled to match the Canadian Current Atlas and have the amplitude change as the tidal exchange changed.
The table below illustrates this process. (Note that this example uses a single day of data and assumes that the local maxima are the maxima for scaling purposes). ::

   Time   Original Offset Scaled  After After
 (6/13/01)  Time    Time   Time    Max   Max
 	   Series  Series Series  Flood  Ebb
  00:19     0.0     +0.7    1.0    0.0   1.0
  03:37    -0.8      0.0    0.0    0.0   0.0
  08:54     0.0     -0.8   -1.0   -1.0   0.0
  09:06    +0.0      0.0    0.0    0.0   0.0
  10:05     0.0     +0.0    0.0    0.0   0.0
  14:46    -0.7      0.0    0.0    0.0   0.0
  18:11     0.0     -0.7   -0.875 -0.875 0.0
  21:13    +0.7      0.0    0.0    0.0   0.0

The eddy circulation patterns were tested by setting up the Strait of Juan de Fuca in GNOME to produce data for the NOAA Trajectory Analysis Planner (TAP) model. Trajectories were run with and without the eddy circulation pattern (all other physics, such as diffusion and tides, were set up as in the Location File). The addition of the eddy patterns significantly improved the simulation of known collection zones within the Strait.