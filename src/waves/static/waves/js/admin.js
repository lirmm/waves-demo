/**
 * Created by marc on 23/09/16.
 */
(function ($) {
    $(document).ready(function () {
        $('.js-popup-link').click(function (e) {
            e.preventDefault();
            console.log('Js-pop-up-modal called');
            $('#popup_modal').dialog({
                modal: true,
                position: {my: 'top', at: 'top+100', of: window},
                minWidth: 500,
                resizable: true,
                dialogClass: "tool_import_modal",
                title: this.title,
            }).dialog('open').load(this.href)
        });
        var $loading = $('#loading').hide();
        $(document)
            .ajaxStart(function () {
                $loading.show();
            })
            .ajaxStop(function () {
                $loading.hide();
            });
    });
})(jQuery || django.jQuery);
