(function(form) {
    function headRiver() {
        var headFlow = form.find('#head-flow').val();
        //var headMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeHead.cur'});
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
        return headScaled;

        //headMover.set('scale_value', headScaled);
    }

    function tailRiver() {
        var tailFlow = form.find('#tail-flow').val();
        //var tailMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeTail.cur'});
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
        return tailScaled;

        //tailMover.set('scale_value', tailScaled);
    }

    function inletsRiver() {
        var inletsFlow = form.find('#inlets-flow').val();
        //var inletsMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeInlets.cur'});
        var INLETS_SCALE = 1.0 / 42400;

        if (inletsFlow === 'other') {
           var inletsVal = parseFloat(form.find('#inlets-flow-manual').val());
           var inletsUnits = form.find('#inlets-flow-manual-units').val();

           if (!inletsVal || isNaN(inletsVal)) {
              return "Please enter a number for canal flow rate!";
           }

           if (inletsUnits === 'km3/s') {
                inletsVal *= 1000;
           }

           if (inletsVal < 10 || inletsVal > 10000) {
              var str = 'Inlets flow rate is outside the acceptable range of ';
              if (inletsUnits === 'km3/s') {
                str += '0.02 and .008 km3/s!';
              } else {
                str += '20 and 80 m3/s!';
              }
              return str;
           }

           inletsFlow = inletsVal;
        } else {
           inletsFlow = parseFloat(inletsFlow);
        }

        var inletsScaled = inletsFlow * INLETS_SCALE;
        return inletsScaled;

        //inletsMover.set('scale_value', inletsScaled);
    }

    var headMessage = headRiver();

    if (headMessage && typeof headMessage==='string') {
      return headMessage;
    } else {
        var headMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeHead.cur'});
        headMover.set('scale_value', headMessage);
    }

    var tailMessage = tailRiver();

    if (tailMessage && typeof tailMessage==='string') {
      return tailMessage;
    } else {
        var tailMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeTail.cur'});
        tailMover.set('scale_value', tailMessage);
    }

    var inletsMessage = inletsRiver();

    if (inletsMessage && typeof inletsMessage==='string') {
      return inletsMessage;
    } else {
        var inletsMover = webgnome.model.get('movers').findWhere({'filename': 'GatunLakeInlets.cur'});
        inletsMover.set('scale_value', inletsMessage);
    }

    webgnome.model.save();
}(form));
