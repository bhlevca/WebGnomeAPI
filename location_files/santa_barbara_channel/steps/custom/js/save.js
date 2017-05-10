(function(form){
   var optionsArr = $('.option', form.html());
   var movers = webgnome.model.get('movers');
   for (var i = 0; i < optionsArr.length; i++) {
      var currentOption = $(optionsArr[i]);
      if (currentOption.hasClass('upwelling')) {
         movers.findWhere({'filename': 'Upwelling.cur'}).set('on', optionsArr[i].dataset.clicked);
      } else if (currentOption.hasClass('convergent')) {
         movers.findWhere({'filename': 'Convergent.cur'}).set('on', optionsArr[i].dataset.clicked);
      } else if (currentOption.hasClass('relaxation')) {
         movers.findWhere({'filename': 'Relaxation.cur'}).set('on', optionsArr[i].dataset.clicked);
      }
   }
   webgnome.model.save();
}(form));