(function(modal){
  var sabineListener = function() {
     if ($('#sabine-flowrate', modal).val() === 'other') {
        $('.sabine-flow-manual', modal).removeClass('hide');
     } else {
        $('.sabine-flow-manual', modal).addClass('hide');
     }
  };

  var nechesListener = function() {
     if ($('#neches-flowrate', modal).val() === 'other') {
        $('.neches-flow-manual', modal).removeClass('hide');
     } else {
        $('.neches-flow-manual', modal).addClass('hide');
     }
  };

  $('#sabine-flowrate', modal).on('change', sabineListener);
  $('#neches-flowrate', modal).on('change', nechesListener);

  sabineListener();
  nechesListener();
}(modal));