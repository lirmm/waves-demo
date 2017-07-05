/**
 * Created by marc on 23/09/16.
 */
var RelatedInlinePopup = function () {
    inline_source = undefined
};

(function ($) {
    RelatedInlinePopup.prototype = {
        popupInline: function (href) {
            //console.log(href.href, typeof href);
            if (href.indexOf('?') === -1) {
                href += '?_popup=1';
            } else {
                href += '&_popup=1';
            }
            var $document = $(window.top.document);
            var $container = $document.find('.related-popup-container');
            var $loading = $container.find('.loading-indicator');
            var $body = $document.find('body');
            var $popup = $('<div>')
                .addClass('related-popup');
            //.data('input', $input);
            var $iframe = $('<iframe>')
                .attr('src', href)
                .on('load', function () {
                    $popup.add($document.find('.related-popup-back')).fadeIn(200, 'swing', function () {
                        $loading.hide();
                    });
                });

            $popup.append($iframe);
            $loading.show();
            $document.find('.related-popup').add($document.find('.related-popup-back')).fadeOut(200, 'swing');
            $container.fadeIn(200, 'swing', function () {
                $container.append($popup);
            });
            $body.addClass('non-scrollable');
        },
        closePopup: function (response) {
            console.log('in closepopup');
            // var previousWindow = this.windowStorage.previous();
            var self = this;

            (function ($) {
                var $document = $(window.parent.document);
                var $popups = $document.find('.related-popup');
                var $container = $document.find('.related-popup-container');
                var $popup = $popups.last();

                if (response != undefined) {
                    self.processPopupResponse($popup, response);
                } else {
                    console.log('no response');
                }

                // self.windowStorage.pop();

                if ($popups.length == 1) {
                    $container.fadeOut(200, 'swing', function () {
                        $document.find('.related-popup-back').hide();
                        $document.find('body').removeClass('non-scrollable');
                        $popup.remove();
                    });
                } else if ($popups.length > 1) {
                    $popup.remove();
                    $popups.eq($popups.length - 2).show();
                }
            })($);
        },
        processPopupResponse: function ($popup, response) {
            console.log('need to process response ' + response + " document " + $popup);
            window.parent.location.reload();
        },
        findPopupResponse: function () {
            var self = this;

            $('#django-waves-admin-inline-popup-response-constants').each(function () {
                var $constants = $(this);
                var response = $constants.data('popup-response');
                console.log('Found !');
                self.closePopup(response);
            });
        },
    };


    $(document).ready(function () {

        $('.js-popup-link').click(function (e) {
            e.preventDefault();
            console.log('Js-pop-up-modal called');
            if ($(this).attr('modal-title') != null) {
                $('#popup_modal_content .modal-header').html("<h4>" + $(this).attr('modal-title') +"</h4>");
            }
            $('#popup_modal_content .modal-body').load($(this).attr('href'), function () {
                $('#popup_modal').modal('toggle');
            });
        });
        var $loading = $('#loading').hide();
        $(document)
            .ajaxStart(function () {
                $loading.show();
            })
            .ajaxStop(function () {
                $loading.hide();
            });

        $('fieldset.collapse.open').removeClass('collapsed');
        var rel1 = new RelatedInlinePopup();
        rel1.findPopupResponse();
        $('fieldset.show-change-link-popup a.inlinechangelink').click(function (e) {
            var rel = new RelatedInlinePopup();
            e.preventDefault();
            rel.popupInline(e.target.href)
        });
        $('#add_submission_link').click(function (e) {
            e.preventDefault();
            console.log("submission link " + $(this) + ' / ' + e.target);
            var rel = new RelatedInlinePopup();
            rel.popupInline(e.target.href);
        });
    });

})(django.jQuery || jQuery);

