.. keywords
   map, bna, coastline, paramterized, shoreline
   
The **Name** of the map is automatically specified from the uploaded file name. This can be edited to a more meaningful name if desired.

The **Refloat Half-life** parameter, along with the other environmental data, allows refloating of oil after it
has impacted the shoreline. Refloat half-life is one hour by default; if the value is higher, the oil will
stick to the shoreline longer (as for a marsh), whereas for very small values, the oil refloats immediately (as
for a rocky shoreline). 

When a map is loaded, a raster land/water mask is created. This mask is used to check whether particle positions are on land or in the water. The default **Land Mask Raster Size** is 16 MB which should be sufficent for most regional applications. However, this size can be increased if more resolution is necessary in domains with narrow channels or complicated shoreline geometry. Increasing this size significantly may negatively impact model performance.


