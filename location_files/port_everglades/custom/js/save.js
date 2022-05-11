(function(form) {
    var discharge = eval(form.find(".discharge").val());
    webgnome.model.get('movers').findWhere({'filename': 'Canal.cur'}).set('on', discharge);
    webgnome.model.save();
}(form));
