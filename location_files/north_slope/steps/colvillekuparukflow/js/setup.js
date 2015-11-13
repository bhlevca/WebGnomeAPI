(function(modal){
   var kuparukListener = function() {
      if ($('#kuparuk-flow').val() === 'other') {
        $('.kuparuk').removeClass('hide');
      } else {
        $('.kuparuk').addClass('hide');
      }
   };

   $('#kuparuk-flow').on('change', kuparukListener);

   kuparukListener();
}(modal));