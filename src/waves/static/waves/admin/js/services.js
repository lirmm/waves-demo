/**
 * Created by marc on 25/11/15.
 * Functions library for atgc service platform back-office
 */

(function ($) {
    $(document).ready(function () {

        $("#id_run_on").focus(function () {
            prev_val = $(this).val();
            console.log('Prev val' + prev_val);
        }).change(function () {
            console.log('Changed triggered');
            if (prev_val) {
                if (confirm('Changing this value might cancel running jobs.\n\nAre you sure ?')) {
                    $("#id_service_run_params-TOTAL_FORMS").val(0);
                    $("#id_service_run_params-INITIAL_FORMS").val(0);
                    $("input[type='submit'][name='_continue']").trigger('click');
                } else {
                    $(this).val(prev_val);
                }
            } else {
                console.log('changed ?');
                $("input[type='submit'][name='_continue']").trigger('click');
            }
        });

        $('#open_import_form').click(function () {
            console.log('Launch an import')
            $('#form-modal-body').load('/open_import_form/', function () {
                $('#form-modal').modal('toggle');
            });
        });

        $('input[id^="id_service_outputs"][id$="from_input"]').each(function () {
            console.log(this.id);
        });
    })
})(jQuery || django.jQuery);


