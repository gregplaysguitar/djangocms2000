var cms_jQuery = jQuery.noConflict(true);
cms_jQuery(function() {
    cmsAdmin(
        cms_jQuery,
        {{ tinymce_config_json|safe }}
    );
});
