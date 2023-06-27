(function (form) {
    var speed = form.find('#speed').val();
    var speed_units = form.find('#speed-units').val();
    var direction = form.find('#direction').val();
    var direction_units = form.find('#direction-units').val();
    var Offshore_Mover = webgnome.model.get('movers').findWhere({'filename': 'Offshore.cur'});
    var cat_v_at_ref = 0.247137;
    var cat_v_at_B = 0.015001;
    var errMsg;

    if (!speed || isNaN(parseFloat(speed))) {
        console.log("Please enter a numerical value for speed!");
        return "Please enter a numerical value for speed!";
    }

    if (speed_units !== 'm/s') {
        if (speed_units === 'cm/s') {
            speed /= 100;
        } else if (speed_units === 'knots') {
            speed *= 0.514444;
        }
    }

    if (speed > 1 || speed < 0) {
        errMsg = "Speed is outside the acceptable range of ";

        if (speed_units === 'm/s') {
            errMsg += "0 and 1 m/s!";
        } else if (speed_units === 'cm/s') {
            errMsg += "0 and 100 cm/s!";
        } else if (speed_units === 'knots') {
            errMsg += "0 and 1.94 knots!";
        }

        return errMsg;
    }

    if (!direction || isNaN(parseFloat(direction))) {
        return "Please enter a numerical value for direction!";
    }

    if (direction_units === 'rad') {
        direction *= (180 / Math.PI);
    }

    if (direction < 0 || direction > 360) {
        errMsg = "Direction is outside the acceptable range of ";
        
        if (direction_units === 'rad') {
            errMsg += "0 and 2 pi radians!";
        } else if (direction_units === 'deg') {
            errMsg += "0 and 360 degrees!";
        }

        return errMsg;
    }

    direction -= 55;

    direction *= (Math.PI / 180);

    var cos_rad = Math.cos(direction);
    var alongshelf = speed * cos_rad;
    var alongshelf_ref = (-1 * alongshelf) * (cat_v_at_ref / cat_v_at_B);

    Offshore_Mover.set('scale_value', alongshelf_ref);
    webgnome.model.save();
}(form));