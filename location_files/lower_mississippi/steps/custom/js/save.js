(function(form){
    var selector = form.selector;
    var datatype = $(selector + ' #datatype').val();
    var missRiverMover = webgnome.model.get('movers').findWhere({'name': 'MissRiver.cur'});
    var stageHeight = $(selector + ' #stageheight').val();
    var speed = parseFloat($(selector + ' #currentspeed').val());
    var speedms;

	if (datatype === 'height'){
        var heightUnits = $(selector + ' #stageheight-units').val();

        if (!stageHeight) {
            return "Please enter a value for stage height!";
        }

        if (heightUnits === 'm') {
            stageHeight *= 3.28084;
        }

        if (stageHeight < 0 || stageHeight > 18) {
            return "Stage height is outside the acceptable range!";
        }

        speedms = (0.0011 * Math.pow(stageHeight, 2) + 0.15 * stageHeight + 0.3868) * 0.5144;

        if (stageHeight <= 8) {
            speedms *= 1.5;
        }
    } else {

        if (isNaN(speed)) {
            return "Please enter a valid input for speed!";
        }

        if ($(selector + ' #currentspeed-units').val() !== 'm/s') {
            if ($(selector + ' #currentspeed-units').val() === 'knots') {
                speed *= 0.5144;
            } else {
                speed *= 0.01;
            }
        }

        if (speed < 0.25722 || speed > 1.80056) {
            return "Speed is outside the acceptable range!";
        }

        speedms = speed;
	}

    missRiverMover.set('scale_value', speedms);
    webgnome.model.save();
}(form));