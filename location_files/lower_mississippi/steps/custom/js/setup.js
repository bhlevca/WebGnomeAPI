(function(modal){
	var inputListener = function() {
		if ($('#datatype', modal).val() === 'height'){
			$('.height', modal).removeClass('hide');
			$('.speed', modal).addClass('hide');
		} else {
			$('.height', modal).addClass('hide');
			$('.speed', modal).removeClass('hide');
		}
	};
	$('#datatype', modal).on('change', inputListener);
	inputListener();
}(modal));