(function(form){
    var convertHeight = function(height, units) {
        if (units !== 'm') {
            height *= 0.3048;
        }
        return height;
    };

    var selector = form.selector;
    var datatype = $(selector + ' #data-type').val();
    var erieMover = webgnome.model.get('movers').findWhere({'name': 'Erie.cur'});
    var scale_value;

    if (datatype === 'height') {
        var windmillHeight = $(selector + ' #windmill').val();
        var windmillHeightUnits = $(selector + ' #windmill-units').val();
        var gibraltarHeight = $(selector + ' #gibraltar').val();
        var gibraltarHeightUnits = $(selector + ' #gibraltar-units').val();

        if (!windmillHeight) {
            return "Please enter a value for Windmill stage height!";
        }

        if (!gibraltarHeight) {
            return "Please enter a value for Gibralter stage height!";
        }

        windmillHeight = convertHeight(windmillHeight, windmillHeightUnits);
        gibraltarHeight = convertHeight(gibraltarHeight, gibraltarHeightUnits);

        if (windmillHeight < 170 || windmillHeight > 180) {
            return "Windmill stage height is outside an acceptable range!";
        }

        if (gibraltarHeight < 170 || gibraltarHeight > 180) {
            return "Gibralter stage height is outside an acceptable range!";
        }

        scale_value = windmillHeight - gibraltarHeight;
    } else {
        scale_value = parseFloat($(selector + ' #surfacespeed').val());
    }

    erieMover.set('scale_value', scale_value);
    webgnome.model.save();
}(form));