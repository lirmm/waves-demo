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
                console.log(data);
                $('#connect_result .modal-content').html(data['connection_result']);
                console.log($('#connect_result .modal-content'));
                $('#connect_result').dialog({
                    modal: true,
                    position: {my: 'top', at: 'top+100', of: window},
                    minWidth: 300,
                    resizable: false,
                    dialogClass: "tool_import_modal",
                    title: "Connection Test"
                }).dialog('open');
            })
        });
    })
})(jQuery || django.jQuery);