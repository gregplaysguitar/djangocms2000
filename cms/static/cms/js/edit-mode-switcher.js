(function ($) {
	function switcher(edit) {
        $.cookie('cms-edit_mode', edit ? 1 : null, {path: '/'});
    };
    $(function() {
        $('.edit-switcher').click(function() {
            switcher($(this).hasClass('on'));
            location.reload();
            return false;
        });
    });
})(jQuery); 