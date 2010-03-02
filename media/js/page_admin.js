var djangocms2000Admin = function(filebrowser_url, buttons) {

    id_list = [];
    $('textarea.djangocms2000.html').each(function(i, item) {
        id_list.push(item.id);
    });
    
    
    // filebrowser callback - only used if filebrowser_url is specified
    function djangoFileBrowser(field_name, url, type, win) {
        var url = filebrowser_url + "?pop=2&type=" + type;
    
        tinyMCE.activeEditor.windowManager.open(
            {
                'file': url,
                'width': 820,
                'height': 500,
                'resizable': "yes",
                'scrollbars': "yes",
                'inline': "no",
                'close_previous': "no"
            },
            {
                'window': win,
                'input': field_name,
                'editor_id': tinyMCE.selectedInstance.editorId
            }
        );
        return false;
    };
    
    
    if (id_list.length) {
        
        tinyMCE.init({
            setup: function(ed) {
                // Force Paste-as-Plain-Text
                ed.onPaste.add( function(ed, e, o) {
                    ed.execCommand('mcePasteText', true);
                    return tinymce.dom.Event.cancel(e);
                });
            },
            "paste_auto_cleanup_on_paste" : true,
			"relative_urls" : false,
            "theme_advanced_toolbar_location": "top",
            "theme_advanced_toolbar_align": "left",
            "content_css": "",
            "language": "en",
			"theme_advanced_buttons1" : buttons,
			"external_link_list_url" : "/djangocms2000/linklist.js",
            "directionality": "ltr",
            "theme": "advanced",
            "strict_loading_mode": 1,
            "file_browser_callback": filebrowser_url ? djangoFileBrowser : null,
            "mode": "exact",
            "plugins": "heading,paste",
            "theme_advanced_buttons3": "",
            "theme_advanced_buttons2": "",
            "elements": id_list.join(',')
        });
    }
    
    
    // hack at the form for usability, if creating a page (not editing)
    if (('' + window.location).match(/\/add\/$/)) {
        $('div.inline-group').hide();
        $('input[type=submit][name=_continue]').attr('value', 'Create and continue to next step');
        $('input[type=submit][name!=_continue]').hide();
    }
    $('div.inline-group').each(function() {
        if ($(this).find('table tr').length <= 1) {
            $(this).hide();
        }
    });
    
};