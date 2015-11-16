(function(modal){
   var macListener = function() {
      if ($('#flow-rate', modal).val() === 'other') {
        $('.mackenzie', modal).removeClass('hide');
      } else {
        $('.mackenzie', modal).addClass('hide');
      }
   };

   $('#flow-rate', modal).on('change', macListener);

   macListener();
}(modal));