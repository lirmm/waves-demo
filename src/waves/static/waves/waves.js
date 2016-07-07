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
            e.preventDefault();
            $('#popup_modal').dialog({
                modal: true,
                position: {my: 'top', at: 'top+100', of: window},
                minWidth: 400,
                resizable: true,
                title: this.title,
            }).dialog('open').load(this.href)
        });
        $('#launch_import').click(function () {
            console.log("Click called ! ");
            $('#form-modal-body').load('/launch_import/', function () {
                $('#form-modal').modal('toggle');
                formAjaxSubmit('#form-modal-body form', '#form-modal');
            });
        });
        $(document).on('change', '.btn-file :file', function () {
            var input = $(this),
                numFiles = input.get(0).files ? input.get(0).files.length : 1,
                label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
            input.trigger('fileselect', [numFiles, label]);
        });
        var formAjaxSubmit = function (form, modal) {
            $(form).submit(function (e) {
                window.console.log("Submit called for this form");
                e.preventDefault();
                $.ajax({
                    type: $(this).attr('method'),
                    url: $(this).attr('action'),
                    data: $(this).serialize(),
                    success: function (xhr, ajaxOptions, thrownError) {
                        if ($(xhr).find('.has-error').length > 0) {
                            window.console.log('has-error ');// + $(xhr).find('.has-error').length);
                            $(modal).find('.modal-body').html(xhr);
                            formAjaxSubmit(form, modal);
                        } else {
                            window.console.log('simply toggle ');
                            $(modal).modal('toggle');
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                    }
                });
            });
        }
    })
})(grp.jQuery);
