(function(modal){
   var kuparukListener = function() {
      if ($('#kuparuk-flow', modal).val() === 'other') {
        $('.kuparuk', modal).removeClass('hide');
      } else {
        $('.kuparuk', modal).addClass('hide');
      }
   };

   $('#kuparuk-flow', modal).on('change', kuparukListener);

   kuparukListener();
}(modal));