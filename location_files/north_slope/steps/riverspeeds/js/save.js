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

    var validationMsgGenerator = function(str, units) {
        switch (units) {
            case 'm/s':
                str += '0.05 and 2.5 m/s!';
                break;
            case 'cm/s':
                str += '5 and 250 cm/s!';
                break;
            case 'knots':
                str += '0.0972 and 4.86 knots!';
                break;
            case 'yd/min':
                str += '3.29 and 164 yd/min!';
                break;
        }

        return str;
    };

    var selector = form.selector;
    var sagMover = webgnome.model.get('movers').findWhere({'filename': 'SagRiver.cur'});
    var shaMover = webgnome.model.get('movers').findWhere({'filename': 'ShaviovikRiver.cur'});
    var canWestMover = webgnome.model.get('movers').findWhere({'filename': 'CanningWestRiver.cur'});
    var canEastMover = webgnome.model.get('movers').findWhere({'filename': 'CanningEastTamaRiver.cur'});

    var sagVal = parseFloat($(selector + ' #sag-speed').val());
    var shaVal = parseFloat($(selector + ' #sha-speed').val());
    var canWestVal = parseFloat($(selector + ' #can-west-speed').val());
    var canEastVal = parseFloat($(selector + ' #can-tam-speed').val());

    var sagUnits = $(selector + ' #sag-speed-units').val();
    var shaUnits = $(selector + ' #sha-speed-units').val();
    var canWestUnits = $(selector + ' #can-west-speed-units').val();
    var canEastUnits = $(selector + ' #can-tam-speed-units').val();

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
        return "Please enter a number for Canning and Tamayariak flow rate!";
    }

    var sagSpeed = convertToM_S(sagVal, sagUnits);
    var shaSpeed = convertToM_S(shaVal, shaUnits);
    var canWestSpeed = convertToM_S(canWestVal, canWestUnits);
    var canEastSpeed = convertToM_S(canEastVal, canEastUnits);

    if (sagSpeed < 0.05 || sagSpeed > 2.5) {
        return validationMsgGenerator('Sag flow rate is not within the acceptable range of ', sagUnits);
    }

    if (shaSpeed < 0.05 || shaSpeed > 2.5) {
        return validationMsgGenerator('Shaviovik flow rate is not within the acceptable range of ', shaUnits);
    }

    if (canWestSpeed < 0.05 || canWestSpeed > 2.5) {
        return validationMsgGenerator('Canning West flow rate is not within the acceptable range of ', canWestUnits);
    }

    if (canEastSpeed < 0.05 || canEastSpeed > 2.5) {
        return validationMsgGenerator('Canning and Tamayariak flow rate is not within the acceptable range of ', canEastUnits);
    }

    sagMover.set('scale_value', sagSpeed);
    shaMover.set('scale_value', shaSpeed);
    canWestMover.set('scale_value', canWestSpeed);
    canEastMover.set('scale_value', canEastSpeed);

    webgnome.model.save();
}(form));