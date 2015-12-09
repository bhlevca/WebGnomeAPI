(function (form){
    var CUBIC_METER_PER_SECOND = 0.028316847;
    var selector = form.selector;

    function trinityRiver() {
        var TRIN_U_TO_Q_RATIO = 0.6698 / 15373;
        var Trin_River_Mover = webgnome.model.get('movers').findWhere({'name': 'TrinityRiver.cur'});
        var t_transport, t_transport_scaled;

        var trinFlow = $(selector + ' #trinity-flow').val();

        if (trinFlow === "other") {
            var trinStageHeight = $(selector + " #trinity-stageheight").val();
            var trinStageHeightUnits = $(selector + " #trinity-stageheight-units").val();

            if (!trinStageHeight || isNaN(parseFloat(trinStageHeight))) {
                return "Please enter a number for Trinity stage height!";
            }

            if (trinStageHeightUnits === 'm') {
                trinStageHeight = trinStageHeight * 3.28084;
            }

            if (trinStageHeight < 0 || trinStageHeight > 31) {
                return "Trinity stage height is outside the acceptable range!";
            }

            if (trinStageHeight > 15) {
                var a9 = -0.0003237200497277822 * Math.pow(trinStageHeight, 9);
                var a8 = 0.05730374402263 * Math.pow(trinStageHeight, 8);
                var a7 = -4.39356026997217 * Math.pow(trinStageHeight, 7);
                var a6 = 190.3947923307952 * Math.pow(trinStageHeight, 6);
                var a5 = -5091.414135633288 * Math.pow(trinStageHeight, 5);
                var a4 = 85706.93130551324 * Math.pow(trinStageHeight, 4);
                var a3 = -878585.6324310122 * Math.pow(trinStageHeight, 3);
                var a2 = 4860075.540379636 * Math.pow(trinStageHeight, 2);
                var a1 = -9059453.584957751 * trinStageHeight;
                var a0 = -17464153.86161943;

                var terms = [a9, a8, a7, a6, a5, a4, a3, a2, a1, a0];
                t_transport = 0;
                terms.forEach(function(value){
                    t_transport += value;
                });
            } else {
                t_transport = 0;
            }

        } else {
            t_transport = CUBIC_METER_PER_SECOND * parseFloat(trinFlow) * 1000;
        }

        t_transport_scaled = t_transport * TRIN_U_TO_Q_RATIO;
        Trin_River_Mover.set('scale_value', t_transport_scaled);
    }

    function sanJacBuffRiver() {
        var SAN_BUFF_TO_Q_RATIO = 0.7048 / (5.12238 * 1000);
        var San_Buff_River_Mover = webgnome.model.get('movers').findWhere({'name': 'BuffBayouSanJacinto.cur'});

        var sanJacFlow = $(selector + ' #sanjacinto-flow').val();
        var buffFlow = $(selector + ' #buffalobayou-flow').val();
        var sj_transport, b_transport;
        var a7, a6, a5, a4, a3, a2, a1, a0;
        var terms;

        if (sanJacFlow === 'other') {
            var sanJacStageHeight = $(selector + ' #sanjacinto-stageheight').val();
            var sanJacStageHeightUnits = $(selector + ' #sanjacinto-stageheight-units').val();

            if (!sanJacStageHeight || isNaN(parseFloat(sanJacStageHeight))) {
                return "Please enter a number for San Jacinto stage height!";
            }

            if (sanJacStageHeightUnits === 'm') {
                sanJacStageHeight = sanJacStageHeight * 3.28084;
            }

            if (sanJacStageHeight < 0 || sanJacStageHeight > 28) {
                return "San Jacinto stage height is outside the acceptable range!";
            }

            a7 = -0.0008962534216177780 * Math.pow(sanJacStageHeight, 7);
            a6 = 0.08090710430776 * Math.pow(sanJacStageHeight, 6);
            a5 = -2.87704742826949 * Math.pow(sanJacStageHeight, 5);
            a4 = 52.01494119132756 * Math.pow(sanJacStageHeight, 4);
            a3 = -497.7695044340068 * Math.pow(sanJacStageHeight, 3);
            a2 = 2598.874761983057 * Math.pow(sanJacStageHeight, 2);
            a1 = -2873.610938411168 * sanJacStageHeight;
            a0 = 2078.345299841351;

            terms = [a7, a6, a5, a4, a3, a2, a1, a0];

            sj_transport = 0;
            terms.forEach(function(value){
                sj_transport += value;
            });
            sj_transport /= 1000;
        } else {
            sj_transport = CUBIC_METER_PER_SECOND * parseFloat(sanJacFlow) * 1000;
        }

        if (buffFlow === 'other') {
            var buffStageHeight = $(selector + ' #buffalobayou-stageheight').val();
            var buffStageHeightUnits = $(selector + ' #buffalobayou-stageheight-units').val();

            if (!buffStageHeight || isNaN(parseFloat(buffStageHeight))) {
                return "Please enter a number for Buffalo stage height!";
            }

            if (buffStageHeightUnits === 'm') {
                buffStageHeight = buffStageHeight * 3.28084;
            }

            if (buffStageHeight < 3 || buffStageHeight > 38) {
                return "Buffalo stage height is outside the acceptable range!";
            }

            a7 = -0.0008962534216177780 * Math.pow(buffStageHeight, 7);
            a6 = 0.08090710430776 * Math.pow(buffStageHeight, 6);
            a5 = -2.87704742826949 * Math.pow(buffStageHeight, 5);
            a4 = 52.01494119132756 * Math.pow(buffStageHeight, 4);
            a3 = -497.7695044340068 * Math.pow(buffStageHeight, 3);
            a2 = 2598.874761983057 * Math.pow(buffStageHeight, 2);
            a1 = -2873.610938411168 * buffStageHeight;
            a0 = 2078.345299841351;

            terms = [a7, a6, a5, a4, a3, a2, a1, a0];

            b_transport = 0;
            terms.forEach(function(value){
                b_transport += value;
            });
            b_transport /= 1000;
        } else {
            b_transport = CUBIC_METER_PER_SECOND * parseFloat(buffFlow) * 1000;
        }

        var b_sj_transport = b_transport + sj_transport;
        var b_sj_transport_scaled = b_sj_transport * SAN_BUFF_TO_Q_RATIO;

        San_Buff_River_Mover.set('scale_value', b_sj_transport_scaled);
    }

    trinityRiver();
    sanJacBuffRiver();
    webgnome.model.save();
}(form));