River Flow Estimation
======================================

**(a) Formulas Used**

The Columbia River Estuary Location File uses the total river transport at Astoria to scale the river flow.
To allow you to enter your own river flow values, the Columbia River Location File includes a modification 
of Jay's (1984) formula for calculating Columbia River flow at Astoria. The user enters values for river flow 
of the Columbia River at the Bonneville Dam and the Willamette River at Portland. Jay's (1984) formula for volume 
transport at Astoria can be written::

    If Bonneville Dam flow < 200 kcfs AND Willamette River flow < 90 kcfs, then   
        Astoria flow (t) = 4.139 kcfs + 1.003 (Bonneville Dam flow (t-6) kcfs) + 1.632 (Willamette River at Portland (t-6) kcfs)  

    If Bonneville Dam flow > 200 kcfs OR Willamette River flow > 90 kcfs, then   
        Astoria flow (t) = 103 kcfs + 1.084 (Bonneville Dam flow (t-6) kcfs) + 1.757 (Willamette River at Portland (t-6) kcfs)  

Since this function is undefined if both the Bonneville Dam and Willamette Rivers are at the decision flows (200 kcfs and 90 kcfs, respectively), 
the Columbia River Estuary Location File uses the lower-flow formula at the decision points. The use of this formula at the decision points results 
in a lower river flow and the oil moving down the river more slowly (more conservative estimate). 

**(b) Limitations on the Formulas**

Jay's formula does not explicitly take into account the differing seasonal inputs from the eastern and coastal portions of the Columbia River watershed.
The Cascade Range effectively divides the watershed into the smaller coastal portion (8%) and the much larger eastern portion (92%).
The smaller coastal sub-basin contributes 24% of the total Columbia River flow, due to orographically-generated rains on the western 
Cascade slopes and the mild wet winters, during which water is not stored for summer release. The Willamette, Lewis, and Cowlitz Rivers 
of the coastal areas have their peak flows during the winter months, while the eastern portion of the watershed contributes highest flows during 
the snow melting season (April to July). The overall Columbia River transport is highest during the spring snow melting season and lowest 
during autumn (Simenstad et al., 1990).

**(c) Time-Correcting River Flow Data**

If you choose to enter river flow values for the Columbia River at Bonneville Dam and the Willamette River at Portland, enter the observed river 
flows at these two locations six (6) hours earlier than your model start time. This is the approximate length of time the transport signal takes to 
travel to the estuary.

**(d) Scaling Current Patterns from User Entered Data**

The Columbia River Estuary Location File scales all current patterns relative to the currents at Tongue Point, Oregon.
To calculate the scale for the river current pattern, :code:`V_scale` (m/s), from the Location File's estimate of the river 
transport at Astoria, :code:`VolumeTransport` (m\ :sup:`3`\ /s) calculated in section (a), the following 
formula is used::

    V_scale = VolumeTransport / CrossSectionalArea - V_tidal,

where :code:`V_tidal` is the mean flow in the tidal record at Tongue Point (approximately 0.2 m/s), and 
:code:`CrossSectionalArea` (m3) is the river's cross sectional area at Tongue Point.