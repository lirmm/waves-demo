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
        // $('.has-popover').popover({'trigger': 'hover'});
        $('.js-popup-link').click(function (e) {
            console.log('Clicked on js-popup-link');
            e.preventDefault();
            $('#popup_modal').dialog({
                modal: true,
                position: {my: 'top', at: 'top+100', of: window},
                minWidth: 500,
                resizable: true,
                dialogClass: "tool_import_modal",
                title: this.title,
            }).dialog('open').load(this.href)
        });
        $('#launch_import').click(function () {
            console.log("Click called ! ");
            $('#form-modal-body').load('/launch_import/', function () {
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


