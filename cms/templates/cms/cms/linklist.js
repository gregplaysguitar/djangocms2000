// TODO global var used by tinymce configs; should fix this
var cms_tinymce_linklist = [
    {% for page in page_list %}
    {title: "{{ page.get_absolute_url }}", value: "{{ page.get_absolute_url }}"}{% if not forloop.last %},{% endif %}
    {% endfor %}
];
