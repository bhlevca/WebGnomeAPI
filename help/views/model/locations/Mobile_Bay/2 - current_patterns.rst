Current Patterns
===================================

The Mobile Bay Location File contains four current patterns. The tidal current pattern is scaled to the tidal predictions at the entrance to Mobile Bay off Mobile Point.

Two wind-driven circulation patterns, one from north winds and another from east winds, are used to simulate wind-driven flow. These two patterns are combined linearly to produce a current pattern appropriate for the user-defined wind field. Current velocity is scaled linearly with wind stress calculated from the user's wind field. Wind-driven currents are important at low- to moderate-river flow rates; at high-river flow rates, surface current patterns become dominated by the freshwater input, and winds play a lesser role. Wind-driven current patterns are thus also scaled by river flow rates as outlined below.

The fourth current pattern represents Mobile River flow. The current pattern is referenced to the river entrance near Little Sand Island and scaled according to the flow rate information given by the user.

All current patterns were created with the NOAA Current Analysis for Trajectory Simulation (CATS) hydrodynamic application.

**River Flow Estimation**

There are four fresh water entrances to Mobile Bay. Relative flow rates for each entrance are estimated from the cross-sectional areas of each entrance and the relative velocities at each entrance.

Ftotal = FLSI + FT + FA + FB

where	
	
* Ftotal = total flow rate
* FLSI = flow rate of Mobile River at Little Sand Island
* FT = flow rate of Tensaw-Raft River entrance
* FA = flow rate of Apalachee River entrance
* FB = flow rate of Blakeley River entrance

The relative flow rate at each entrance is calculated by dividing the entrance flow rate (e.g. FLSI) by the total flow rate (Ftotal).

The currents are then scaled to the largest of these entrances near Little Sand Island. The currents are calculated by multiplying the relative flow rate of the "Mobile River at Little Sand Island" entrance by the absolute flow rate (entered by the user), then dividing by the cross-sectional area of the river entrance there:

CLSI = FLSI / Ftotal * Fabsolute) / CrossSectionalAreaLSI

The user can either select a flow rate (high, medium or low), or enter a stage height at the Barry Steam Plant. Mobile River Flow rate, *transport*, is calculated from the Barry Steam Plant stage height, *h*, using a 7th order polynomial fit to the rating curve provided by Mr. Steve Lloyd of the U.S. Army Corps of Engineers:

*transport* = 0.130783535h\ :sup:`7` − 9.30220603h\ :sup:`6` + 277.541373h\ :sup:`5` − 4487.28702h\ :sup:`4` +42196.7977h\ :sup:`3` − 228915.462h\ :sup:`2` + 687589.384h − 824448.766

**Scaling Wind-Driven Currents**

During periods of high river runoff into Mobile Bay, there are few to no correlations between surface currents and wind stress (Noble et al. 1997). Wind-driven surface currents are thus scaled to river flow such that they are larger at low river flow and decrease to zero at high river flow. The scaling factor is modeled after results presented in Noble et al. (1997), fading out wind-driven currents as river flow approaches 4000 m3/s (141 cfs):

| WindScaleFactor = 1
| RiverTransport < 106 cfs (3000 m3/s)
| WindScaleFactor = (141 - RiverTransport) / 35
| 106 cfs < RiverTransport < 141 cfs
| WindScaleFactor = 0.0
| RiverTransport > 141 cfs (4000 m3/s)
|

Wind-driven current velocities are multiplied by the WindScaleFactor to scale them with 
fresh water input.