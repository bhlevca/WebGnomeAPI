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

    var sagVal = parseFloat($(selector + ' #sag-speed').val());
    var shaVal = parseFloat($(selector + ' #sha-speed').val());
    var canWestVal = parseFloat($(selector + ' #can-west-speed').val());
    var canEastVal = parseFloat($(selector + ' #can-east-speed').val());

    if (!sagVal || isNaN(sagVal)) {
        return "Please enter a number for Sag flow rate!";
    }

    if (!shaVal || isNaN(shaVal)) {
        return "Please enter a number for Shaviovik flow rate!";
    }

    if (!canWestVal || isNaN(canWestVal)) {
        return "Please enter a number for Canning West flow rate!";
    }

    if (!canEastVal || isNaN(canEastVal)) {
        return "Please enter a number for Canning East flow rate!";
    }

    var sagSpeed = convertToM_S(sagVal, $(selector + ' #sag-speed-units'));
    var shaSpeed = convertToM_S(shaVal, $(selector + ' #sha-speed-units'));
    var canWestSpeed = convertToM_S(canWestVal, $(selector + ' #can-west-speed-units'));
    var canEastSpeed = convertToM_S(canEastVal, $(selector + ' #can-tam-speed-units'));

    if (sagSpeed < 0.05 || sagSpeed > 2.5) {
        return "Sag flow rate is not within the acceptable range!";
    }

    if (shaSpeed < 0.05 || shaSpeed > 2.5) {
        return "Shaviovik flow rate is not within the acceptable range!";
    }

    if (canWestSpeed < 0.05 || canWestSpeed > 2.5) {
        return "Canning West flow rate is not within the acceptable range!";
    }

    if (canEastSpeed < 0.05 || canEastSpeed > 2.5) {
        return "Canning East flow rate is not within the acceptable range!";
    }

    sagMover.set('scale_value', sagSpeed);
    shaMover.set('scale_value', shaSpeed);
    canWestMover.set('scale_value', canWestSpeed);
    canEastMover.set('scale_value', canEastSpeed);

    webgnome.model.save();
}(form));