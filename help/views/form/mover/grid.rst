.. keywords
   currents, movers, gridded, roms, fvcom, hyrodynamic model
   
The **Name** by default is set from the uploaded file name. It can be edited for clarity.

**Start Date** and **End Date** are also set from the file and indicate the time span of the model values in the file. They are displayed for reference. The time zone is the same as that used in the input file. There is no support for converting to a different time zone within the application at present.

The **Active Range** option can be used to limit the time interval in which the Mover is applied to the particles. The default is **Infinite** in which case the model will apply this Mover at all times and errors will occur if the model run time is outside the interval of available data. A second option is to choose **Set to Start/End Times**. In this case, the Mover will be applied only while within the data range of the input file and will be inactive at other times. 

The **Scale Value** applies a multipicative scale to all the velocity values used by the current mover. Note, the underlying data is unchanged and hence the vector displays in the Map View will not reflect this scaling. Scaling is uniform across the grid.

The **Extrapolate the Data** option allows the current mover to operate outside the time span of the underlying data. For example, at times before the **Start Time** the initial velocity values will be used, At times after the **End Time**, the final velocity value will be used.