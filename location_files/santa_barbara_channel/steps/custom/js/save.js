(function(form){
   var optionsArr = $('.option', form.html());
   var movers = webgnome.model.get('movers');
   for (var i = 0; i < optionsArr.length; i++) {
      var currentOption = $(optionsArr[i]);
      if (currentOption.hasClass('upwelling')) {
         movers.findWhere({'name': 'Upwelling.cur'}).set('on', optionsArr[i].dataset.clicked);
      } else if (currentOption.hasClass('convergent')) {
         movers.findWhere({'name': 'Convergent.cur'}).set('on', optionsArr[i].dataset.clicked);
      } else if (currentOption.hasClass('relaxation')) {
         movers.findWhere({'name': 'Relaxation.cur'}).set('on', optionsArr[i].dataset.clicked);
      }
   }
   webgnome.model.save();
}(form));