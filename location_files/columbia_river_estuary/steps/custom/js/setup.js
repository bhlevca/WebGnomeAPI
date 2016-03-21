(function(modal){
	var inputListener = function(){
		if ($('#flow-rate', modal).val() === 'input') {
			$('.flow', modal).removeClass('hide');
		} else {
			$('.flow', modal).addClass('hide');
		}
	};
	$('#flow-rate', modal).on('change', inputListener);
	inputListener();
}(modal));