(function(form) {
    var outflowBool = form.find(".outflow").val();
    webgnome.model.get('movers').findWhere({'name': 'Sewage Outfall Current'}).set('on', outflowBool);
    webgnome.model.save();
}(form));
