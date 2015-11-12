(function (form){
    var selector = form.selector;
    var outflowBool = $(selector + " .outflow").val();
    webgnome.model.get('movers').findWhere({'name': 'MassBaySewage.cur'}).set('on', outflowBool);
    webgnome.model.save();
}(form));