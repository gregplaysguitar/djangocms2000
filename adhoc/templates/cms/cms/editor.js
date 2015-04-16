{% load url from future %}

yepnope('{{ adhoc_settings.STATIC_URL }}css/cms.css');

// I don't know why, but tinymce fails subtly and infuriatingly if
// loaded along with the rest of the scripts. This fixes it.
yepnope.injectJs('{{ adhoc_settings.STATIC_URL }}tinymce/js/tinymce/tinymce.min.js');

yepnope({
    load: ['{{ adhoc_settings.STATIC_URL }}lib/jquery-1.10.2.min.js',
           '{{ adhoc_settings.STATIC_URL }}lib/jquery.color.js',
           '{{ adhoc_settings.STATIC_URL }}lib/jquery.cookie.js',
           '{{ adhoc_settings.STATIC_URL }}lib/jquery.form.js',
           '{% url "cms.views.linklist" %}',
           '{{ adhoc_settings.STATIC_URL }}js/cms.js',],
    complete: function() {
        var cms_jQuery = jQuery.noConflict(true),
            browser_supported = true; // TODO

        if (browser_supported) {
            // collect html bits from the server, and inject them into the page, then initialise
            var url = ('' + window.location.href).replace(/https?:\/\/[^\/]+/, '')
            cms_jQuery.get('{% url "cms.views.editor_html" %}?page=' + url, function(editor_html) {
                cms_jQuery('body').append(editor_html);
                
                // init function from cms.js
                cms(cms_jQuery,
                    {{ tinymce_config_json|safe }},
                    {{ adhoc_settings.POST_EDIT_CALLBACK|safe }});
            });
        }
        else {
            // TODO - do something here
            
            //cms_jQuery('#getarealbrowser').css({'display':'block'});
        }
    }
});
