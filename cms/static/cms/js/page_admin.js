var cmsAdmin = function($, linklist_url, tinymce_content_css, buttons) {

    id_list = [];
    $('textarea.cms-html').each(function(i, item) {
        id_list.push(item.id);
    });

    if (id_list.length) {

        tinyMCE.init({
            mode: 'exact',
            elements: id_list.join(','),
			paste_text_sticky_default: true,
            paste_text_sticky: true,
            paste_text_linebreaktype: 'combined',
            paste_auto_cleanup_on_paste: true,
			relative_urls: false,
            theme_advanced_toolbar_location: "top",
            theme_advanced_toolbar_align: "left",
            content_css: tinymce_content_css,
            language: "en",
			external_link_list_url: linklist_url,
            directionality: "ltr",
            theme: "advanced",
            strict_loading_mode: 1,
            plugins: "paste,inlinepopups",
            heading_clear_tag: "p",
			theme_advanced_buttons1: buttons,
            theme_advanced_buttons2: "",
            theme_advanced_buttons3: "",
            theme_advanced_statusbar_location: "bottom",
            theme_advanced_resizing: true
        });
    }


    // hack at the form for usability, if creating a page (not editing)
    if (('' + window.location).match(/\/add\/$/)) {
        $('div.inline-group').hide();
        $('input[type=submit][name=_continue]').attr('value', 'Create and continue to next step');
        $('input[type=submit][name!=_continue]').remove();
    }
    else {
        $('div.inline-group').each(function() {
            if ($(this).find('table tr').length <= 1) {
                $(this).hide();
            }
        });
    }

};
