(function ($) {
	function switcher(edit) {
        $.cookie('djangocms2000-edit_mode', edit ? 1 : null, {path: '/'});
    };
    $(function() {
        $('.edit-switcher').click(function() {
            switcher($(this).hasClass('on'));
            location.reload();
            return false;
        });
    });
})(jQuery); 