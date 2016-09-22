/**
 * Created by marc on 22/09/16.
 */
(function ($) {
    $(document).ready(function () {
        $("#id_clazz").click(function () {
            prev_val = $(this).val();
        }).change(function () {
            if ($("#id_available").is(':checked')) {
                if (!confirm('Changing this value on available Runner will disable related service and might cancel running jobs !\n\nAre you sure ?')) {
                    $(this).val(prev_val);
                }
            }
        });
    })
})(jQuery || django.jQuery);