(function(form){
    //var flowVal = parseFloat(form.find('#flow-speed').val());
    var flowVal = form.find('#flow-speed').val();

    //var flowUnits = form.find('#flow-speed-units').val();
    var flowUnits = 'm/s';

	if (flowVal === 'other') {
		flowVal = parseFloat(form.find('#flow-speed-manual').val());

		if (!flowVal || isNaN(flowVal)) {
			return "Please enter a number for coastal flow rate!";
		}

		flowUnits = form.find('#flow-speed-units').val();
	} else {
		flowVal = parseFloat(flowVal);
	}

    var convertToM_S = function(speed, units) {
        if (units !== 'm/s') {
            if (units === 'cm/s') {
                speed /= 100;
            } else if (units === 'knots') {
                speed *= 0.514444;
            }
        }

        return speed;
    };

    var validationMsgGenerator = function(str, units) {
        switch (units) {
            case 'm/s':
                str += '-1.0 and 1.0 m/s!';
                break;
            case 'cm/s':
                str += '-100 and 100 cm/s!';
                break;
            case 'knots':
                str += '-1.9438 and 1.9438 knots!';
                break;
        }

        return str;
    };

    var coastalMover = webgnome.model.get('movers').findWhere({'filename': 'pDACtriangvel.cur'});

    var flowSpeed = convertToM_S(flowVal, flowUnits);

    if (flowSpeed < -1.0 || flowSpeed > 1.0) {
        return validationMsgGenerator('Coastal flow rate is not within the acceptable range of ', flowUnits);
    }


    coastalMover.set('scale_value', flowSpeed);

    webgnome.model.save();
}(form));