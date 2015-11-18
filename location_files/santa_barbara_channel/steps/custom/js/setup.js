(function(modal, modaljq){
	$('.option', modal).attr('data-clicked', false);
	var thumbnailHighlight = function(e) {
       $(e.target, modal).closest('.option').attr('data-clicked', true);
	};

	$('.option', modal).on('click', thumbnailHighlight);
}(modal, modaljq));