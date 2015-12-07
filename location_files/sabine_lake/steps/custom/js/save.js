(function(form){
    var selector = form.selector;
    var sabineRiver = webgnome.model.get('movers').findWhere({'name': 'SabineRiver.cur'});
    var nechesRiver = webgnome.model.get('movers').findWhere({'name': 'NechesRiver.cur'});
    var sab_flow, nec_flow, sab_scale, nec_scale;

    if ($(selector + ' #sabine-flowrate').val() !== 'other') {
        sab_flow = parseFloat($(selector + ' #sabine-flowrate').val());
    } else {
        sab_flow = parseFloat($(selector + ' #sabine-flowrate-manual').val());

        if ($(selector + ' #sabine-flowrate-units').val() !== 'cfs') {
            sab_flow *= 1000;
        }
    }

    if ($(selector + ' #neches-flowrate').val() !== 'other') {
        nec_flow = parseFloat($(selector + ' #neches-flowrate').val());
    } else {
        nec_flow = parseFloat($(selector + ' #neches-flowrate-manual').val());

        if ($(selector + ' #neches-flowrate-units').val() !== 'cfs') {
            nec_flow *= 1000;
        }
    }

    sab_scale = sab_flow * (1.182 / 95935);
    nec_scale = nec_flow * (0.69 / 198.53);

    sabineRiver.set('scale_value', sab_scale);
    nechesRiver.set('scale_value', nec_scale);
}(form));