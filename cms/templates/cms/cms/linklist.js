var tinyMCELinkList = [
    {% for page in page_list %}
    ["{{ page }}", "{{ page.get_absolute_url }}"]{% if not forloop.last %},{% endif %}
    {% endfor %}
];
