(function (form){
    var selector = form.selector;
    var speed = $(selector + ' #speed').val();
    var speed_units = $(selector + ' #speed-units').val();
    var direction = $(selector + ' #direction').val();
    var direction_units = $(selector + ' #direction-units').val();
    var Offshore_Mover = webgnome.model.get('movers').findWhere({'name': 'Offshore.cur'});
    var cat_v_at_ref = 0.247137;
    var cat_v_at_B = 0.015001;

    if (!speed || isNaN(parseFloat(speed))) {
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
        return "Speed is outside the acceptable range!";
    }

    if (!direction || isNaN(parseFloat(direction))) {
        return "Please enter a numerical value for direction!";
    }

    if (direction_units === 'rad') {
        direction *= (180 / Math.PI);
    }

    if (direction < 0 || direction > 360) {
        return "Direction is outside the acceptable range!";
    }

    direction -= 55;

    direction *= (Math.PI / 180);

    var cos_rad = Math.cos(direction);
    var alongshelf = speed * cos_rad;
    var alongshelf_ref = (-1 * alongshelf) * (cat_v_at_ref / cat_v_at_B);

    Offshore_Mover.set('scale_value', alongshelf_ref);
    webgnome.model.save();
}(form));