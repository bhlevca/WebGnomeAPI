(function (form){
    var selector = form.selector;
    var selected = $(selector + " #month").find(":selected");
    var curUncertaintyAlong = parseFloat(selected.attr("data-along"));
    var curUncertaintyCross = parseFloat(selected.attr("data-cross"));
    var gulfCur = webgnome.model.get('movers').findWhere({'name': 'GulfMaineDAC.cur'});
    gulfCur.set('down_cur_uncertain', curUncertaintyAlong);
    gulfCur.set('left_cur_uncertain', curUncertaintyCross);
    webgnome.model.save();
}(form));