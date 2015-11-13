(function(modal){
   var heightListener = function() {
      if ($('#riverflow').val() === 'height') {
         $('.height').removeClass('hide');
      } else {
         $('.height').addClass('hide');
      }
   };

   $('#riverflow').on('change', heightListener);
   heightListener();
}(modal));