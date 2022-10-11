(function(form) {
    function headRiver() {
        var headFlow = form.find('#head-flow').val();
        var headMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeHead.cur'});
        var HEAD_SCALE = 1.0 / 3480;

        if (headFlow === 'other') {
           var headVal = parseFloat(form.find('#head-flow-manual').val());
           var headUnits = form.find('#head-flow-manual-units').val();

           if (!headVal || isNaN(headVal)) {
              return "Please enter a number for lake flow rate!";
           }

           if (headUnits === 'km3/s') {
                headVal *= 1000;
           }

           if (headVal < 10 || headVal > 10000) {
              var str = 'Lake flow rate is outside the acceptable range of ';
              if (headUnits === 'km3/s') {
                str += '0.05 and 0.10 km3/s!';
              } else {
                str += '50 and 100 m3/s!';
              }
              return str;
           }

           headFlow = headVal;
        } else {
           headFlow = parseFloat(headFlow);
        }

        var headScaled = headFlow * HEAD_SCALE;

        headMover.set('scale_value', headScaled);
    }

    function tailRiver() {
        var tailFlow = form.find('#tail-flow').val();
        var tailMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeTail.cur'});
        var TAIL_SCALE = 1.0 / 6430;

        if (tailFlow === 'other') {
           var tailVal = parseFloat(form.find('#tail-flow-manual').val());
           var tailUnits = form.find('#tail-flow-manual-units').val();

           if (!tailVal || isNaN(tailVal)) {
              return "Please enter a number for canal flow rate!";
           }

           if (tailUnits === 'km3/s') {
                tailVal *= 1000;
           }

           if (tailVal < 10 || tailVal > 10000) {
              var str = 'Canal flow rate is outside the acceptable range of ';
              if (tailUnits === 'km3/s') {
                str += '0.02 and .008 km3/s!';
              } else {
                str += '20 and 80 m3/s!';
              }
              return str;
           }

           tailFlow = tailVal;
        } else {
           tailFlow = parseFloat(tailFlow);
        }

        var tailScaled = tailFlow * TAIL_SCALE;

        tailMover.set('scale_value', tailScaled);
    }

    var headMessage = headRiver();

    if (headMessage) {
      return headMessage;
    }
    
    var tailMessage = tailRiver();

    if (tailMessage) {
      return tailMessage;
    }

    webgnome.model.save();
}(form));
