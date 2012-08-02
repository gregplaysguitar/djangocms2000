var tinyMCELinkList = [
    {% for page in page_list %}
    ["{% firstof page.page_title page.get_absolute_url %}", "{{ page.get_absolute_url }}"]{% if not forloop.last %},{% endif %}
    {% endfor %}
];