{% load url from future %}


var switcher_html = '<div id="cms-menu">' +
                    '    <a class="edit-switcher on">Edit</a> /' + 
                    '    <a href="{% url "cms.views.logout" %}?from=' +
                    window.location.pathname + '">Logout</a>' +
                    '</div>'

yepnope('{{ cms_settings.STATIC_URL }}css/cms.css');
yepnope({
    load: ['{{ cms_settings.STATIC_URL }}lib/jquery-1.10.2.min.js',
           '{{ cms_settings.STATIC_URL }}lib/jquery.cookie.js',],
    complete: function() {
        var cms_jQuery = jQuery.noConflict(true),
            switcher = cms_jQuery(switcher_html).appendTo('body');
            
            switcher.find('.edit-switcher').on('click', function() {
                cms_jQuery.cookie('cms-edit_mode', 1, {path: '/'});
                location.reload();
                return false;
            });
    }
});
