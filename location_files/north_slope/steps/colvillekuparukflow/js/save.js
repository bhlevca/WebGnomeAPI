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
           var kuparukUnits = $(selector + ' #kuparuk-flow-manual-units').val();

           if (!kuparukVal || isNaN(kuparukVal)) {
              return "Please enter a number for Kuparuk flow rate!";
           }

           if (kuparukUnits === 'kcfs') {
                kuparukVal *= 1000;
           }

           if (kuparukVal < 10 || kuparukVal > 10000) {
              var str = 'Kuparuk flow rate is outside the acceptable range of ';
              if (kuparukUnits === 'kcfs') {
                str += '0.01 and 10 kcfs!';
              } else {
                str += '10 and 10000!';
              }
              return str;
           }

           kuparukFlow = kuparukVal;
        } else {
           kuparukFlow = parseFloat(kuparukFlow);
        }

        var kuparukScaled = kuparukFlow * KUPARUK_SCALE;

        kuparukMover.set('scale_value', kuparukScaled);
    }

    colvilleRiver();
    var kuparukMessage = kuparukRiver();

    if (kuparukMessage) {
      return kuparukMessage;
    }

    webgnome.model.save();
}(form));