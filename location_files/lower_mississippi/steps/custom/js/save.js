(function(form){
    var selector = form.selector;
    var datatype = $(selector + ' #datatype').val();
    var missRiverMover = webgnome.model.get('movers').findWhere({'filename': 'MissRiver.cur'});
    var stageHeight = $(selector + ' #stageheight').val();
    var speed = parseFloat($(selector + ' #currentspeed').val());
    var speedms, errMsg;

	if (datatype === 'height'){
        var heightUnits = $(selector + ' #stageheight-units').val();

        if (!stageHeight) {
            return "Please enter a value for stage height!";
        }

        if (heightUnits === 'm') {
            stageHeight *= 3.28084;
        }

        if (stageHeight < 0 || stageHeight > 18) {
            errMsg = "Stage height is outside the acceptable range of ";

            if (heightUnits === 'm') {
                errMsg += "0 and 5.4 meters!";
            } else if (heightUnits === 'ft') {
                errMsg += "0 and 18 feet!";
            }

            return errMsg;
        }

        speedms = (0.0011 * Math.pow(stageHeight, 2) + 0.15 * stageHeight + 0.3868) * 0.5144;

        if (stageHeight <= 8) {
            speedms *= 1.5;
        }
    } else {

        var speedUnits = $(selector + ' #currentspeed-units').val();

        if (isNaN(speed)) {
            return "Please enter a valid input for speed!";
        }

        if (speedUnits !== 'm/s') {
            if (speedUnits === 'knots') {
                speed *= 0.5144;
            } else {
                speed *= 0.01;
            }
        }

        if (speed < 0.25722 || speed > 1.80056) {
            errMsg = "Speed is outside the acceptable range of ";

            if (speedUnits === 'm/s') {
                errMsg += "0.26 and 1.8 m/s!";
            } else if (speedUnits === 'knots') {
                errMsg += "0.5 and 3.5 knots!";
            } else if (speedUnits === 'cm/s') {
                errMsg += "26 and 180 cm/s!";
            }

            return errMsg;
        }

        speedms = speed;
	}

    missRiverMover.set('scale_value', speedms);
    webgnome.model.save();
}(form));