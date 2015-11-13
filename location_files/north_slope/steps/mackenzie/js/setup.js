(function(modal){
   var macListener = function() {
      if ($('#flow-rate').val() === 'other') {
        $('.mackenzie').removeClass('hide');
      } else {
        $('.mackenzie').addClass('hide');
      }
   };

   $('#flow-rate').on('change', macListener);

   macListener();
}(modal));