/**
 * Created by marc on 23/09/16.
 */
(function ($) {
    $(document).ready(function () {
// $('.has-popover').popover({'trigger': 'hover'});
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
    });
})(jQuery || django.jQuery);
