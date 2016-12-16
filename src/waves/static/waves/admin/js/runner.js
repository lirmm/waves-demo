/**
 * Created by marc on 22/09/16.
 */
(function ($) {
    $(document).ready(function () {
        var prev_val = ''
        $("#id_clazz").focus(function () {
            prev_val = $(this).val();
            console.log('Prev val' + prev_val);
        }).change(function () {
            console.log('Changed triggered');
            if (prev_val) {
                if (confirm('Changing this value will disable related service and might cancel running jobs.\n\nAre you sure ?')) {
                    $("input[type='submit'][name='_continue']").trigger('click');
                } else {
                    $(this).val(prev_val);
                }
            } else {
                console.log('changed ?');
                if ($("#id_name").val() == "") {
                    $("#id_name").val($(this).val().substring($(this).val().lastIndexOf('.') + 1));
                }
                $("input[type='submit'][name='_continue']").trigger('click');
            }
        });
        $('#test_connect').click(function (e) {
            e.preventDefault();
            console.log('test_connect clicked ' + $(this).attr('href'));
            $.getJSON($(this).attr('href'), function (data) {
                $('#modal_alert .modal-content .modal-header > h4').html('Connection test');
                $('#modal_alert .modal-content .modal-body').html(data['connection_result']);
                $('#modal_alert').modal('toggle');
            })
        });
        $('#open_import_form').click(function (e) {
            console.log('Launch an import ' + $(this).attr('href'));
            e.preventDefault();
            $('#popup_modal_content').load($(this).attr('href'), function () {
                console.log('loaded')
                $('#popup_modal').modal('toggle');
            });
        });
        $('#popup_modal').on('toggle', function () {
            console.log('show raised');
            $(this).find('.modal-body').css({
                'max-height': '100%'
            });
        });
    })
})(jQuery || django.jQuery);