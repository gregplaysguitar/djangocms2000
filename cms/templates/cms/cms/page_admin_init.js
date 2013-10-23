{% load url from future %}

jQuery(function() {
    cmsAdmin(
        jQuery,
        "{{ cms_settings.FILEBROWSER_URL_ADMIN }}",
        "{% url 'cms.views.linklist' %}",
        "{{ cms_settings.TINYMCE_CONTENT_CSS }}",
        "{{ cms_settings.TINYMCE_BUTTONS }}",
        {% if request.user.is_superuser %}1{% else %}0{%endif %}
    );
});
