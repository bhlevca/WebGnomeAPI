(function(modal){
	var inputListener = function(){
		if ($('#flow-rate', modal).val() === 'input') {
			$('#bonneFlow', modal).removeClass('hide');
			$('#williamFlow', modal).removeClass('hide');
		} else {
			$('#bonneFlow', modal).addClass('hide');
			$('#williamFlow', modal).addClass('hide');
		}
	};
	$('#flow-rate', modal).on('change', inputListener);
	inputListener();
}(modal));