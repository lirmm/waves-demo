/**
 * Created by marc on 25/11/15.
 * Functions library for atgc service platform back-office
 */

(function ($) {
    $(document).ready(function () {
        $('.btn-file :file').on('fileselect', function (event, numFiles, label) {

            var input = $(this).parents('.input-group').find(':text'),
                log = numFiles > 1 ? numFiles + ' files selected' : label;

            if (input.length) {
                input.val(log);
            } else {
                if (log) alert(log);
            }

        });

        $('#launch_import').click(function () {
            $('#form-modal-body').load('/launch_import/', function () {
                console.log('IamUsed');
                $('#form-modal').modal('toggle');
            });
        });
        $(document).on('change', '.btn-file :file', function () {
            var input = $(this),
                numFiles = input.get(0).files ? input.get(0).files.length : 1,
                label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
            input.trigger('fileselect', [numFiles, label]);
        });
    })
})(jQuery || django.jQuery);


