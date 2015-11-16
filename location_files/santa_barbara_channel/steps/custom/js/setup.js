(function(modal, modaljq){
	var thumbnailHighlight = function(e) {
       $(e.target, modal).closest('.option').addClass('selected');
       $(modal).trigger('save');
	};

	$('.option', modal).on('click', thumbnailHighlight);
}(modal, modaljq));