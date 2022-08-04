.. keywords
   spill, NESDIS
   

**File Information**

This section is automatically popluated based on the oil classification information in the uploaded shapefile. For example, NESDIS Marine Pollution Surveillance Reports typically have at most two classes: "potential oil" and "potential thicker oil". These are represented as "thin" and "thick" with specified defaults for **Thickness**. These should be reviewed and edited as appropriate. Alternatively, the total **Volume** per oil class can be specified. The **Area** of the oil class is used to transform between the two. This is calculated from the geometry of the shapes in the file and can not be edited.

**General Spill Properties**

* Enter the **Name** of the spill. Use descriptive names, particularly if you will be adding more than one spill.
* The **Time of Release** is automatically set from the file if it can be parsed. This should correspond to the time of the imagery. Alternatively, select the date and time using the calendar icon next to the entry box or enter a date and time manually. Use date format yyyy/mm/dd and time format 00:00 (24-hour clock). To select a date using the calendar, click on the calendar icon next to the start time entry. Click on the left or right arrows to change the month, and click on a date square to select it. Select a time from the list to the right of the calendar, scrolling up or down as necessary.
* The total **Amount Released** is automatically calculated from the oil class volumes.
* The **Number of Particles** defaults to 1000 but can be edited if desired (e.g. for a large volume spill).

**Substance/Oil Section**

* The default substance is "Non-weathering". In this case, particles will move under the influence of wind and currents but their properties will not change over time. To model weathering processes, you must first specify an oil. Oils can be downloaded from the ADIOS oil database using the link in the form. Oil information is stored in a JSON (text) file format. Once an oil file is loaded, summary information on the oil is displayed, along with an option to edit the Emulsification defaults for the oil.

* Note on **Emulsification Onset After**: The emulsification algorithm assumes that emulsion begins when some percentage of the oil has evaporated. You have the option of overriding the default value and specifying when you want emulsion to begin. Click on the button next to the entry field. Choose hours from the drop-down menu and type in the number of hours that have elapsed before emulsion begins, or choose percent from the drop-down menu and type in the percent of the spill that has evaporated.


**Windage Section**

These parameters change the amount of direct wind influence on the particles.