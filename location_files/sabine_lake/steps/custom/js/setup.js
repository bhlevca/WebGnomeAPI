(function(modal){
  var sabineListener = function() {
     if ($('#sabine-flowrate').val() === 'other') {
        $('.sabine-flow-manual').removeClass('hide');
     } else {
        $('.sabine-flow-manual').addClass('hide');
     }
  };

  var nechesListener = function() {
     if ($('#neches-flowrate').val() === 'other') {
        $('.neches-flow-manual').removeClass('hide');
     } else {
        $('.neches-flow-manual').addClass('hide');
     }
  };

  $('#sabine-flowrate').on('change', sabineListener);
  $('#neches-flowrate').on('change', nechesListener);

  sabineListener();
  nechesListener();
}(modal));