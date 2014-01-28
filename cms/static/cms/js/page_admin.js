var cmsAdmin = function($, tinymce_content_css, buttons) {

    var id_list = [];
    $('textarea.cms-html').each(function(i, item) {
        id_list.push(item.id);
    });

    if (id_list.length) {

        tinyMCE.init({
        	elements: id_list.join(','),
        	plugins: "paste link code",
			paste_as_text: true,
			relative_urls: false,
			theme: "modern",
	        menubar : false,
			block_formats: "Header 3=h3;Header 4=h4;Header 5=h5;Header 6=h6;Quote=blockquote;Paragraph=p",
			toolbar: buttons,
			content_css: tinymce_content_css,
			height: 400,
			width: 760,
			link_list: cms_tinymce_linklist, // created by cms.views.linklist
        
        
        
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
