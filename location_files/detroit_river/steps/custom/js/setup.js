(function(modal){
    var renderInputs = function(){
        if ($('#data-type', modal).val() === 'height') {
            $('.height', modal).removeClass('hide');
            $('.speed', modal).addClass('hide');
        } else {
            $('.speed', modal).removeClass('hide');
            $('.height', modal).addClass('hide');
        }
    };
    $('#data-type', modal).on('change', renderInputs);
    renderInputs();
}(modal));