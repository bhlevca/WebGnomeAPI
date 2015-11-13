(function(modal){
	var inputListener = function() {
		if ($('#datatype').val() === 'height'){
			$('.height').removeClass('hide');
			$('.speed').addClass('hide');
		} else {
			$('.height').addClass('hide');
			$('.speed').removeClass('hide');
		}
	};
	$('#datatype').on('change', inputListener);
	inputListener();
}(modal));