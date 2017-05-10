(function(form){
    var convertHeight = function(height, units) {
        if (units !== 'm') {
            height *= 0.3048;
        }
        return height;
    };

    var selector = form.selector;
    var datatype = $(selector + ' #data-type').val();
    var erieMover = webgnome.model.get('movers').findWhere({'filename': 'Erie.cur'});
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
        scale_value = parseFloat($(selector + ' #surfacespeed').val());
    }

    erieMover.set('scale_value', scale_value);
    webgnome.model.save();
}(form));