(function(form){
    var selector = form.selector;
    
    function colvilleRiver() {
        var colvilleFlow = $(selector + ' #colville-flow').val();
        var colvilleMover = webgnome.model.get('movers').findWhere({'name': 'ColvilleRiver.cur'});
        var COLLVILLE_SCALE = 0.183 / 1500;
        var colvilleScaled = colvilleFlow * COLLVILLE_SCALE;

        colvilleMover.set('scale_value', colvilleScaled);
    }

    function kuparukRiver() {
        var kuparukFlow = $(selector + ' #kuparuk-flow').val();
        var kuparukMover = webgnome.model.get('movers').findWhere({'name': 'KuparukRiver.cur'});
        var KUPARUK_SCALE = 0.1814 / 957;

        if (kuparukFlow === 'other') {
           var kuparukVal = parseFloat($(selector + ' #kuparuk-flow-manual').val());

           if (!kuparukVal || isNaN(kuparukVal)) {
              return "Please enter a number for Kuparuk flow rate!";
           }

           if ($(selector + ' #kuparuk-flow-manual-units').val() === 'kcfs') {
                kuparukVal *= 1000;
           }

           if (kuparukVal < 10 || kuparukVal > 10000) {
              return "Kuparuk flow rate is outside the acceptable range!";
           }

           kuparukFlow = kuparukVal;
        } else {
           kuparukFlow = parseFloat(kuparukFlow);
        }

        var kuparukScaled = kuparukFlow * KUPARUK_SCALE;

        kuparukMover.set('scale_value', kuparukScaled);
    }

    colvilleRiver();
    kuparukRiver();

    webgnome.model.save();
}(form));