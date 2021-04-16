.. keywords
   continuous release, Amount spilled, constant spill, emulsion, override, trajectory, map

The Continuous Release form contains multiple sections where you may enter information. If you are running the model using the Oil Fate Wizard (weathering only mode) you will not see 
the sections titled **Position** nor **Windage**. These sections are only relevant to trajectory simulations.

**General Spill Properties**

* Enter the **Name** of the spill. Use descriptive names, particularly if you will be adding more than one spill.
* Enter the **Time of Release** or select the date and time using the calendar icon next to the entry box. To enter a date and time manually, use date format yyyy/mm/dd and time format 00:00 (24-hour clock). To select a date using the calendar, click on the calendar icon next to the start time entry. Click on the left or right arrows to change the month, and click on a date square to select it. Select a time from the list to the right of the calendar, scrolling up or down as necessary.
* Enter the **Release Duration** and select units from the drop-down menu.
* Either enter the **Amount Released** (total spill amount) or **Release Rate** and select units from the drop-down menu. The other field will be dynamically calculated.


**Substance/Oil Section**

* Unless you want to leave the substance as "non-weathering", click **Select Oil**. This will open the oil database. If you want to change the substance spilled, click **Change Oil** to relaunch the database.

Note on **Emulsification Parameter**
    The emulsification algorithm assumes that emulsion begins when some percentage of the oil has evaporated. You have the option of overriding the default value and specifying when you want emulsion to begin. Click on the button next to the entry field. Choose hours from the drop-down menu and type in the number of hours that have elapsed before emulsion begins, or choose percent from the drop-down menu and type in the percent of the spill that has evaporated.

**Position Section**

You can specify the spill position one of two ways.

* Select **Place on Map** to bring up an interactive map display.
* Enter latitude and longitude values using the text boxes.

**Windage Section**

These parameters change the amount of direct wind influence on the particles.