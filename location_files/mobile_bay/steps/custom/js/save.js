(function(form){
    var selector = form.selector;
    var mobileRiver = webgnome.model.get('movers').findWhere({'name': 'MobileRiver.cur'});
    var scale = 7.6 / 1157;
    var scale_value, transport;

    if ($(selector + ' #riverflow').val() !== 'other') {
        var flow = parseFloat($(selector + ' #riverflow').val());
        scale_value = scale * flow;
    } else {
        var stage_height = parseFloat($(selector + ' #stageheight').val());
        var stage_height_units = $(selector + ' #stageheight-units').val();
        var errMsg;

        if (!stage_height || isNaN(stage_height)) {
            return "Please enter a number for stage height!";
        }

        if (stage_height_units === 'm') {
            stage_height *= 3.28084;
        }

        if (stage_height < 3 || stage_height > 20) {
            errMsg = "Stage height is not within the acceptable range of ";

            if (stage_height_units === 'm') {
                errMsg += "0.92 and 6 meters!";
            } else if (stage_height_units === 'ft') {
                errMsg += "3 and 20 feet!";
            }

            return errMsg;
        }

        var a7 = (1.30783535/10) * Math.pow(stage_height, 7);
        var a6 = (-9.30220602) * Math.pow(stage_height, 6);
        var a5 = (2.77541373 * 100) * Math.pow(stage_height, 5);
        var a4 = (-4.48728702 * 1000) * Math.pow(stage_height, 4);
        var a3 = (4.21967977 * 10000) * Math.pow(stage_height, 3);
        var a2 = (-2.28915462 * 100000) * Math.pow(stage_height, 2);
        var a1 = (6.87589384 * 100000) * stage_height;
        var a0 = (-8.24448766 * 100000);

        var terms = [a7, a6, a5, a4, a3, a2, a1, a0];
        var sum = 0;

        terms.forEach(function(val, i, arr){
            sum += val;
        });
        transport = sum / 1000;
        scale_value = scale * transport;
    }

    mobileRiver.set('scale_value', scale_value);
    webgnome.model.save();
}(form));