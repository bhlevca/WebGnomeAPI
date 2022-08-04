(function(form) {
    var datatype = form.find('#data-type').val();

    var convertHeight = function(height, units) {
        if (units !== 'm') {
            height *= 0.3048;
        }
        return height;
    };

    var erieMover = webgnome.model.get('movers').findWhere({'filename': 'Erie.cur'});
    var scale_value;

    if (datatype === 'height') {
        var windmillHeight = form.find('#windmill').val();
        var windmillHeightUnits = form.find('#windmill-units').val();
        var gibraltarHeight = form.find('#gibraltar').val();
        var gibraltarHeightUnits = form.find('#gibraltar-units').val();

        if (!windmillHeight) {
            return "Please enter a value for Windmill stage height!";
        }

        if (!gibraltarHeight) {
            return "Please enter a value for Gibralter stage height!";
        }

        windmillHeight = convertHeight(windmillHeight, windmillHeightUnits);
        gibraltarHeight = convertHeight(gibraltarHeight, gibraltarHeightUnits);

        var str;
        if (windmillHeight < 170 || windmillHeight > 180) {
            str = "Windmill stage height needs to be within ";
            if (windmillHeightUnits === 'm') {
                str += "170 and 180 meters!";
            } else {
                str += "558 and 591 feet!";
            }
            return str;
        }

        if (gibraltarHeight < 170 || gibraltarHeight > 180) {
            str = "Gibraltar stage height needs to be within ";
            if (gibraltarHeightUnits === 'm') {
                str += "170 and 180 meters!";
            } else {
                str += "558 and 591 feet!";
            }
            return str;
        }

        scale_value = windmillHeight - gibraltarHeight;
    } else {
        scale_value = parseFloat(form.find('#surfacespeed').val());
    }

    erieMover.set('scale_value', scale_value);
    webgnome.model.save();
}(form));