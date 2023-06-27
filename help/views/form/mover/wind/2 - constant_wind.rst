.. keywords
   constant, wind, direction, speed, bullseye, bull\'s-eye, bulls-eye, target, rayleigh distribution, point

Constant Wind
^^^^^^^^^^^^^
A **Constant Wind** will be the same for the entire model run regardless of the **Date & Time** entered. 
However, its a good idea for this to match up with the model start time in case you want to add some 
time variability later.

**Wind Direction** and **Speed** can be entered either by typing a value or by clicking in the wind bull\'s-eye. 

**Wind Direction** can be entered as degrees (between 0 and 360 degrees) or by the cardinal directions 
N, NE, NNE, NW, NNW, E, S, SE, SSE, SW, SSW, W. Cardinal directions will automatically be translated 
into degrees. Enter a value for **Speed** and then select units from the drop-down menu.

To select **Wind Direction and Speed using the bull\'s-eye**, click and drag inside the bull\'s-eye to change 
the length of the arrow to represent speed and the direction of the arrow to indicate the direction of 
the wind.

The **Speed Uncertainty (Oil Weathering)** option adds some variability to the magnitude of the winds that
affects oil weathering ONLY (uncertainty is handled differently in the oil transport and is activated 
from the Model Settings panel). |location_link|

Change the **Speed Uncertainty** slider by dragging the bar to the left for certain and to the right for 
uncertain to change the range of wind speed that will be used. Range is calculated using a Rayleigh 
distribution.

.. |location_link| raw:: html

   <a href="/doc/uncertainty.html" target="_blank">Learn more about uncertainty in the WebGNOME Users manual.</a>
