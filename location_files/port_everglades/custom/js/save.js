(function (form){
    var selector = form.selector;
    var discharge = eval($(selector + " .discharge").val());
    webgnome.model.get('movers').findWhere({'name': 'Canal.cur'}).set('on', discharge);
    webgnome.model.save();
}(form));