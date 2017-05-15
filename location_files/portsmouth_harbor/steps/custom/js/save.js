(function (form){
    var selector = form.selector;
    var selected = $(selector + " #month").find(":selected");
    var curUncertaintyAlong = parseFloat(selected.attr("data-along"));
    var curUncertaintyCross = parseFloat(selected.attr("data-cross"));
    var gulfCur = webgnome.model.get('movers').findWhere({'filename': 'GulfMaineDAC.cur'});
    gulfCur.set('down_cur_uncertain', curUncertaintyAlong * -1);
    gulfCur.set('left_cur_uncertain', curUncertaintyCross * -1);
    gulfCur.set('right_cur_uncertain', curUncertaintyCross);
    gulfCur.set('up_cur_uncertain', curUncertaintyAlong);
    webgnome.model.save();
}(form));