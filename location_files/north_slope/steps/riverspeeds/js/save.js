(function(form){

    var convertToM_S = function(speed, units) {
        if (units !== 'm/s') {
            if (units === 'cm/s') {
                speed /= 100;
            } else if (units === 'knots') {
                speed *= 0.514444;
            } else if (units === 'yd/min') {
                speed *= 0.01524;
            }
        }

        return speed;
    };

    var selector = form.selector;
    var sagMover = webgnome.model.get('movers').findWhere({'name': 'SagRiver.cur'});
    var shaMover = webgnome.model.get('movers').findWhere({'name': 'ShaviovikRiver.cur'});
    var canWestMover = webgnome.model.get('movers').findWhere({'name': 'CanningWestRiver.cur'});
    var canEastMover = webgnome.model.get('movers').findWhere({'name': 'CanningEastTamaRiver.cur'});

    var sagSpeed = convertToM_S(parseFloat($(selector + ' #sag-speed').val()), $(selector + ' #sag-speed-units'));
    var shaSpeed = convertToM_S(parseFloat($(selector + ' #sha-speed').val()), $(selector + ' #sha-speed-units'));
    var canSpeed = convertToM_S(parseFloat($(selector + ' #can-west-speed').val()), $(selector + ' #can-west-speed-units'));

}(form));