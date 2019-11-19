.. keywords
   currents, movers, gridded, roms, fvcom, hyrodynamic model
   
The **Name** by default is set from the uploaded file name. 

**Start Time** and **End Time** are also set from the file and indicate the time span of the model values in the file. They are read-only values shown here for reference only.

The **Scale Value** applies a multipicative scale to all the velocity values used by the current mover. Note, the underlying data is unchanged and hence the vector displays in the Map View will not reflect this scaling. Scaling is uniform across the grid.

The **Extrapolate the Data** option allows the current mover to operate outside the time span of the underlying data. For example, at times before the **Start Time** the initial velocity values will be used, At times after the **End Time**, the final velocity value will be used.