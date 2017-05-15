(function (form){
    var selector = form.selector;
    var reversal = parseFloat($(selector + " #condition").val());
    webgnome.model.get('movers').findWhere({'filename': 'WACReverse2.cur'}).set('scale_value', reversal);
    webgnome.model.save();
}(form));