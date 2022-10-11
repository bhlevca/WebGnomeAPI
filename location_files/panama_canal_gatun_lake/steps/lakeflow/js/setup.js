(function(modal){
   var headListener = function() {
      if ($('#head-flow', modal).val() === 'other') {
        $('.head', modal).removeClass('hide');
      } else {
        $('.head', modal).addClass('hide');
      }
   };

   $('#head-flow', modal).on('change', headListener);

   headListener();

   var tailListener = function() {
      if ($('#tail-flow', modal).val() === 'other') {
        $('.tail', modal).removeClass('hide');
      } else {
        $('.tail', modal).addClass('hide');
      }
   };

   $('#tail-flow', modal).on('change', tailListener);

   tailListener();
}(modal));