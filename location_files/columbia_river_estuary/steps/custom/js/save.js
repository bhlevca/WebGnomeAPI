(function (form){
	var selector = form.selector;
	var flow = $(selector + ' #flow-rate').val();
	var riverMover = webgnome.model.get('movers').findWhere({'name': 'RiverFlow.cur'});
	var scale = 0.2725 / 223.027;
	var v_scale, tongue_point;

	var convertToKCFS = function(flow, units){
		if (units === 'cfs') {
			flow /= 1000;
		} else if (units === 'm3/s') {
			flow *= 35.3146667;
			flow /= 1000;
		}
		return flow;
	};

	if (flow === 'input') {
		var bonneFlow = parseFloat($(selector + ' #bonne-flow').val());
		var willFlow = parseFloat($(selector + ' #william-flow').val());

		if (!bonneFlow || isNaN(bonneFlow)) {
			return "Please enter a number for Bonneville flow rate!";
		}

		if (!willFlow || isNaN(willFlow)) {
			return "Please enter a number for Williamette flow rate!";
		}

		var units = {};
		units['bonne'] = $(selector + ' #bonne-flow-units').val();
		units['will'] = $(selector + ' #william-flow-units').val();
		var transport, errMsg;

		bonneFlow = convertToKCFS(bonneFlow, units.bonne);
		willFlow = convertToKCFS(willFlow, units.will);

		if (bonneFlow < 0 || bonneFlow > 450) {
			errMsg = "Bonneville flow rate is outside the acceptable range of ";
			if (units.bonne === 'cfs') {
				errMsg += "0 and 450,000 cfs!";
			} else if (units.bonne === 'kcfs') {
				errMsg += "0 and 450 kcfs!";
			} else if (units.bonne === 'm3/s') {
				errMsg += "0 and 12,742 m^3/s!";
			}

			return errMsg;
		}

		if (willFlow < 0 || willFlow > 300) {
			errMsg = "Williamette flow rate is outside the acceptable range of ";
			if (units.will === 'cfs') {
				errMsg += "0 and 300,000 cfs!";
			} else if (units.will === 'kcfs') {
				errMsg += "0 and 300 kcfs!";
			} else if (units.will === 'm3/s') {
				errMsg += "0 and 8,495 m^3/s!";
			}

			return errMsg;
		}

		if ((bonneFlow <= 200) && (willFlow <= 90)) {
			transport = (4.139 + (1.003 * bonneFlow)) + (1.632 * willFlow);
		} else {
			transport = (103 + (1.084 * bonneFlow)) + (1.757 * willFlow);
		}

		tongue_point = scale * transport;
		v_scale = tongue_point - 0.200;
	} else {
		var flowNum = parseFloat(flow);
		tongue_point = scale * flowNum;
		v_scale = tongue_point - 0.200;
	}

	riverMover.set('scale_value', v_scale);
	webgnome.model.save();
}(form));