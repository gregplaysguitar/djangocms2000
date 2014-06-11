var cms_jQuery = jQuery.noConflict(true);
cms_jQuery(function() {
    // tinyMCE may be confused about these if there is another version of it
    // on the page, so reset them to be sure
    tinyMCE.baseURL = "{{ cms_settings.STATIC_URL }}tinymce/js/tinymce";
    tinyMCE.suffix = '.min';
    
    cmsAdmin(
        cms_jQuery,
        {{ tinymce_config_json|safe }}
    );
});
