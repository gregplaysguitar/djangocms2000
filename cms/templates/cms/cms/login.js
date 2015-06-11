yepnope('{{ cms_settings.STATIC_URL }}css/cms.css');

yepnope({
  load: ['{{ cms_settings.STATIC_URL }}lib/jquery-1.10.2.min.js',
         '{{ cms_settings.STATIC_URL }}lib/jquery.cookie.js',],
  complete: function() {
    var cms_jQuery = jQuery.noConflict(true),
        url = window.location.pathname;
    
    cms_jQuery.get('{% url "cms_login" %}', function(html) {
      cms_jQuery('body').append(html);
      var menu = cms_jQuery('#cms-menu');
      menu.hide().fadeIn()
      menu.find('input[name="next"]').val(window.location.pathname);
      cms_jQuery.cookie('cms-edit_mode', 1, {path: '/'});
    });
  }
});
