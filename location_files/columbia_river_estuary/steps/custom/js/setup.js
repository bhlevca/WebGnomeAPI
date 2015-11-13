(function(modal){
	var inputListener = function(){
		if ($('#flow-rate').val() === 'input') {
			$('#bonneFlow').removeClass('hide');
			$('#williamFlow').removeClass('hide');
		} else {
			$('#bonneFlow').addClass('hide');
			$('#williamFlow').addClass('hide');
		}
	};
	$('#flow-rate').on('change', inputListener);
	inputListener();
}(modal));