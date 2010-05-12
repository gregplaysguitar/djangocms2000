(function($) {
    
    $(function() {
    
        $('a:contains("Djangocms2000")').each(function() {
            $(this).html($(this).html().replace('Djangocms2000', 'Static Content'));
        });
    
    });    
    
})(jQuery);