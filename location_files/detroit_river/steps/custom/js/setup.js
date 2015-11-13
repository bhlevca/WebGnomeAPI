(function(modal){
    var renderInputs = function(){
        if ($('#data-type').val() === 'height') {
            $('.height').removeClass('hide');
            $('.speed').addClass('hide');
        } else {
            $('.speed').removeClass('hide');
            $('.height').addClass('hide');
        }
    };
    $('#data-type').on('change', renderInputs);
    renderInputs();
}(modal));