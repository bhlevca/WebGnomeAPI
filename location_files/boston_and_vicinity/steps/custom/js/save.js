(function (form){
    var selector = form.selector;
    var outflowBool = $(selector + " .outflow").val();
    webgnome.model.get('movers').findWhere({'name': 'Sewage Outfall Current'}).set('on', outflowBool);
    webgnome.model.save();
}(form));