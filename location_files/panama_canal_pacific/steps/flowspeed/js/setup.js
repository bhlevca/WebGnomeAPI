(function(modal){
   var flowspeedListener = function() {
      if ($('#flow-speed', modal).val() === 'other') {
        $('.flowspeed', modal).removeClass('hide');
      } else {
        $('.flowspeed', modal).addClass('hide');
      }
   };

   $('#flow-speed', modal).on('change', flowspeedListener);

   flowspeedListener();
}(modal));