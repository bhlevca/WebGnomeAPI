(function(modal){
   var heightListener = function() {
      if ($('#riverflow', modal).val() === 'other') {
         $('.height', modal).removeClass('hide');
      } else {
         $('.height', modal).addClass('hide');
      }
   };

   $('#riverflow', modal).on('change', heightListener);
   heightListener();
}(modal));