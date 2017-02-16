var cmsAdmin = function($, tinymce_config) {

    var id_list = [];
    $('textarea.cms-html').each(function(i, item) {
        id_list.push('#' + item.id);
    });
    
    if (id_list.length) {
        tinyMCE.init($.extend({
            selector: id_list.join(','),
            plugins: "paste link code list",
            paste_as_text: true,
            relative_urls: false,
            theme: "modern",
            menubar : false,
            block_formats: "Header 3=h3;Header 4=h4;Header 5=h5;Header 6=h6;" + 
                           "Quote=blockquote;Paragraph=p",
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
