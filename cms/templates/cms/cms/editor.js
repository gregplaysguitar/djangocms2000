{% load url from future %}

yepnope('{{ cms_settings.STATIC_URL }}css/cms.css');

// I don't know why, but tinymce fails subtly and infuriatingly if
// loaded along with the rest of the scripts. This fixes it.
yepnope.injectJs('{{ cms_settings.STATIC_URL }}tiny_mce/tiny_mce.js');

yepnope({
    load: ['{{ cms_settings.STATIC_URL }}lib/jquery-1.7.2.js',
           '{{ cms_settings.STATIC_URL }}lib/jquery.color.js',
           '{{ cms_settings.STATIC_URL }}lib/jquery.cookie.js',
           '{{ cms_settings.STATIC_URL }}lib/jquery.form.js',
           '{{ cms_settings.STATIC_URL }}js/cms.js',],
    complete: function() {
        var cms_jQuery = jQuery.noConflict(true),
            browser_supported = !cms_jQuery.browser.msie; // TODO

        if (browser_supported) {
            // collect html bits from the server, and inject them into the page, then initialise
            var url = ('' + window.location.href).replace(/https?:\/\/[^\/]+/, '')
            cms_jQuery.get('{% url "cms.views.editor_html" %}?page=' + url, function(editor_html) {
                cms_jQuery('body').append(editor_html);
                
                // init function from cms.js
                cms(cms_jQuery,
                    "{{ cms_settings.HIGHLIGHT_COLOR }}",
                    "{{ cms_settings.TINYMCE_BUTTONS }}",
                    "{{ tinymce_content_css }}",
                    "{% url 'cms.views.linklist' %}",
                    {{ cms_settings.POST_EDIT_CALLBACK|safe }});
            });
        }
        else {
            // TODO - do something here
            
            //cms_jQuery('#getarealbrowser').css({'display':'block'});
        }
    }
});
