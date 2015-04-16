{% load url from future %}


var switcher_html = '<div id="cms-logged_in">' +
                    '    <a class="edit-switcher on">Edit</a> /' + 
                    '    <a href="{% url "cms.views.logout" %}?from={{ request.path_info }}">Logout</a>' +
                    '</div>'

yepnope('{{ adhoc_settings.STATIC_URL }}css/cms.css');
yepnope({
    load: ['{{ adhoc_settings.STATIC_URL }}lib/jquery-1.10.2.min.js',
           '{{ adhoc_settings.STATIC_URL }}lib/jquery.cookie.js',],
    complete: function() {
        var cms_jQuery = jQuery.noConflict(true),
            switcher = cms_jQuery(switcher_html).appendTo('body');
            
            switcher.click(function() {
                cms_jQuery.cookie('adhoc-edit_mode', 1, {path: '/'});
                location.reload();
                return false;
            });
    }
});
