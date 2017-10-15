var cmsAdmin = function($, tinymce_config) {

    var id_list = [];
    $('textarea.cms-html').each(function(i, item) {
        id_list.push('#' + item.id);
    });
    
    if (id_list.length) {
        tinyMCE.init($.extend({
            selector: id_list.join(','),
            plugins: "paste link code lists",
            paste_as_text: true,
            relative_urls: false,
            theme: "modern",
            menubar : false,
            block_formats: "Large Title=h3;Medium Title=h4;Small Title=h5;Bold Title=h6;Quote=blockquote;Paragraph=p",
            toolbar: "formatselect bold italic | undo redo | link | " +
                     "blockquote bullist numlist | pastetext code",
            height: 400,
            width: 760,
            link_list: cms_tinymce_linklist // created by cms.views.linklist
        }, tinymce_config));
    }


    // hack at the form for usability, if creating a page (not editing)
    if (('' + window.location).match(/\/add\/$/)) {
        $('div.inline-group').hide();
        $('input[type=submit][name=_continue]').attr('value', 'Create and continue to next step');
        $('input[type=submit][name!=_continue]').remove();
    }
};
