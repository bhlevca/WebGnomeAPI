.. keywords
   export, particles, format, netcdf, shapefile, kmz, binary
   
Formats
^^^^^^^

WebGNOME can export particle data in various formats for use in other applications (for example, importing into GIS). The most complete format is *NetCDF*. In addition to the locations of the particles over time, physical or chemical properties of the particle are also included. Some examples of particle properties include:

* ID: a unique particle identifier 
* Mass (kg): the amount of mass for an individual particle
* Status_codes: the "status" of the particle (e.g., floating vs. beached)
* Age (seconds): the age of a particle from the time of release
* Surface_concentration (g/m^2): an estimate of concentration based on the density and mass of surrounding particles
* Density (kg/m^3): particle density 

The *Shapefile* format is the ESRI shapefile format which is suitable for GIS applications. 
*KMZ* format can be loaded into Google Earth.
The *Binary* format is used for a deprecated NOAA/ORR application (GNOME Analyst) and support may be discontinued.