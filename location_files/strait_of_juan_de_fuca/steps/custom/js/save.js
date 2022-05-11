(function(form) {
    var reversal = parseFloat(form.find("#condition").val());
    webgnome.model.get('movers').findWhere({'filename': 'WACReverse2.cur'}).set('scale_value', reversal);
    webgnome.model.save();
}(form));
