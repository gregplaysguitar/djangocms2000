$(function() {
    djangocms2000Admin("{{ djangocms2000_settings.FILEBROWSER_URL_ADMIN }}", "{{ djangocms2000_settings.TINYMCE_BUTTONS }}", {% if request.user.is_superuser %}1{% else %}0{%endif %});
})