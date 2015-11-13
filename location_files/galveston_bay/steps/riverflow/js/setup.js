(function(modal){
	var triChange = function() {
		if ($('#trinity-flow').val() === 'other') {
			$('.trinity').removeClass('hide');
		} else {
			$('.trinity').addClass('hide');
		}
	};

	var sanChange = function() {
		if ($('#sanjacinto-flow').val() === 'other') {
			$('.sanjacinto').removeClass('hide');
		} else {
			$('.sanjacinto').addClass('hide');
		}
	};

	var buffaloChange = function() {
		if ($('#buffalobayou-flow').val() === 'other') {
			$('.buffalobayou').removeClass('hide');
		} else {
			$('.buffalobayou').addClass('hide');
		}
	};

	$('#trinity-flow').on('change', triChange);
	$('#sanjacinto-flow').on('change', sanChange);
	$('#buffalobayou-flow').on('change', buffaloChange);

	triChange();
	sanChange();
	buffaloChange();
}(modal));