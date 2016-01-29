(function(form){
	var selector = form.selector;
	var macFlow = $(selector + ' #flow-rate').val();
	var EAST_SCALE = 0.266 / 108500;
	var MIDDLE_SCALE = 0.371 / 376250;
	var NAP_SCALE = 0.363 / 408750;

	if (macFlow === 'other') {
		macFlow = parseFloat($(selector + ' #flow-rate-manual').val());

		if (!macFlow || isNaN(macFlow)) {
			return "Please enter a number for Mackenzie flow!";
		}

		if (macFlow < 2500 || macFlow > 35000) {
			return "Mackenzie flow rate is not within the acceptable range of 2500 and 35000 m^3/s!";
		}
	} else {
		macFlow = parseFloat(macFlow);
	}

	var macEastMover = webgnome.model.get('movers').findWhere({'name': 'MackenzieRiver_EastChannel.cur'});
	var macMidMover = webgnome.model.get('movers').findWhere({'name': 'MackenzieRiver_MiddleChannel.cur'});
	var napMover = webgnome.model.get('movers').findWhere({'name': 'MackenzieRiver_NapoiakChannel.cur'});

	var eastScaled = EAST_SCALE * macFlow;
	var midScaled = MIDDLE_SCALE * macFlow;
	var napScaled = NAP_SCALE * macFlow;

	macEastMover.set('scale_value', eastScaled);
	macMidMover.set('scale_value', midScaled);
	napMover.set('scale_value', napScaled);

	webgnome.model.save();
}(form));