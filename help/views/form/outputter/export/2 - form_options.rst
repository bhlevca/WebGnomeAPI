.. keywords
   export, particles, format, netcdf, shapefile, kmz, binary

Export Options
^^^^^^^^^^^^^^

Export options are identical, regardless of the format.

An **Output Start Time** can be specified, by default this is the model start time. The **Output Time Step (hours)** determines how often to write output -- for example, for a longer duration simulation, you might only want daily model output.

The checkbox **Output Positions at Single Time** will disable the time step option and only the time specfied will be output. 

The options to **Output Initial/Final Positions** will ensure the output at the very beginning and end of the simulation are inlcuded in the event the time step and model start time specified don't line up exactly with those times.