{% load url from future %}

var cms_jQuery = jQuery.noConflict(true);
cms_jQuery(function() {
    cmsAdmin(
        cms_jQuery,
        "{{ tinymce_content_css }}",
        "{{ cms_settings.TINYMCE_BUTTONS }}"
    );
});
