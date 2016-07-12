/**
 * Created by marc on 07/07/16.
 * WAVES form javascript library used in base templates
 */

$(document).ready(function () {
    $(".has_dependent").change(function(elem){
        /*
          * for each inputs with related_inputs, hide all except the one corresponding
          * to input value
         */
        var dependents = $("[dependent-on='" + $(this).attr("name") + "']")
        var has_dep = $(this);
        dependents.each(function() {
            if ($(this).attr('dependent-4-value') == has_dep.val())
                $('#div_id_' + $(this).attr('name')).removeClass('hid_dep_parameter');
            else
                $('#div_id_' + $(this).attr('name')).addClass('hid_dep_parameter');
        });
    });
});


