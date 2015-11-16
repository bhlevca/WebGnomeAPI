(function(modal){
	var thumbnailHighlight = function(e) {
       $('.thumbnail', modal).removeClass('selected');
       $($(e.target).parent('.thumbnail'), modal).addClass('selected');
	};

	$('.thumbnail', modal).on('click', thumbnailHighlight);
}(modal));