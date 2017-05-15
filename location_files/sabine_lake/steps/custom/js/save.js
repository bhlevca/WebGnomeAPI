(function(form){
    var selector = form.selector;
    var sabineRiver = webgnome.model.get('movers').findWhere({'filename': 'SabineRiver.cur'});
    var nechesRiver = webgnome.model.get('movers').findWhere({'filename': 'NechesRiver.cur'});
    var sab_flow, nec_flow, sab_scale, nec_scale, sab_units, nec_units, errMsg;

    if ($(selector + ' #sabine-flowrate').val() !== 'other') {
        sab_flow = parseFloat($(selector + ' #sabine-flowrate').val());
    } else {
        sab_flow = parseFloat($(selector + ' #sabine-flowrate-manual').val());
        sab_units = $(selector + ' #sabine-flowrate-units').val();

        if (isNaN(sab_flow)) {
            return "Please enter a number for Sabine flow rate!";
        }

        if (sab_units !== 'cfs') {
            sab_flow *= 1000;
        }

        if (sab_flow > 20000 || sab_flow < 10) {
            errMsg = "The entered Sabine flow rate is outside the acceptable range of ";

            if (sab_units === 'cfs') {
                errMsg += "10,000 and 20,000,000 cfs!";
            } else if (sab_units === 'kcfs') {
                errMsg += "10 and 20,000 kcfs!";
            }

            return errMsg;
        }
    }

    if ($(selector + ' #neches-flowrate').val() !== 'other') {
        nec_flow = parseFloat($(selector + ' #neches-flowrate').val());
    } else {
        nec_flow = parseFloat($(selector + ' #neches-flowrate-manual').val());
        nec_units = $(selector + ' #neches-flowrate-units').val();

        if (isNaN(nec_flow)) {
            return "Please enter a number for Neches flow rate!";
        }

        if (nec_units !== 'cfs') {
            nec_flow *= 1000;
        }

        if (nec_flow > 3800 || nec_flow < 1) {
            errMsg = "The entered Neches flow rate is outside the acceptable range of ";
            
            if (nec_units === 'cfs') {
                errMsg += "1,000 and 3,800,000 cfs!";
            } else if (nec_units === 'kcfs') {
                errMsg += "1 and 3,800 kcfs!";
            }

            return errMsg;
        }
    }

    sab_scale = sab_flow * (1.182 / 95935);
    nec_scale = nec_flow * (0.69 / 198.53);

    sabineRiver.set('scale_value', sab_scale);
    nechesRiver.set('scale_value', nec_scale);
}(form));