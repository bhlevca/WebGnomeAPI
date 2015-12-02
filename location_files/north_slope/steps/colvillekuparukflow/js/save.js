(function(form){
	var selector = form.selector;
    
    function colvilleRiver() {
        var colvilleFlow = $(selector + ' #colville-flow').val();
        var colvilleMover = webgnome.model.get('movers').findWhere({'name': 'ColvilleRiver.cur'});
    }

    function kuparukRiver() {

    }

    colvilleRiver();
    kuparukRiver();
    webgnome.model.save();
}(form));