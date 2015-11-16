(function(modal){
	var triChange = function() {
		if ($('#trinity-flow', modal).val() === 'other') {
			$('.trinity', modal).removeClass('hide');
		} else {
			$('.trinity', modal).addClass('hide');
		}
	};

	var sanChange = function() {
		if ($('#sanjacinto-flow', modal).val() === 'other') {
			$('.sanjacinto', modal).removeClass('hide');
		} else {
			$('.sanjacinto', modal).addClass('hide');
		}
	};

	var buffaloChange = function() {
		if ($('#buffalobayou-flow', modal).val() === 'other') {
			$('.buffalobayou', modal).removeClass('hide');
		} else {
			$('.buffalobayou', modal).addClass('hide');
		}
	};

	$('#trinity-flow', modal).on('change', triChange);
	$('#sanjacinto-flow', modal).on('change', sanChange);
	$('#buffalobayou-flow', modal).on('change', buffaloChange);

	triChange();
	sanChange();
	buffaloChange();
}(modal));