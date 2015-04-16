var cms = function ($, tinymce_config, post_edit_callback) {
	var throbberString = "<span class='throbber'>Saving...</span>",
		currently_editing = false,
		tinymce_init_object = $.extend({
			plugins: "paste link code",
			paste_as_text: true,
			relative_urls: false,
			theme: "modern",
	        menubar : false,
			block_formats: "Header 3=h3;Header 4=h4;Header 5=h5;Header 6=h6;Quote=blockquote;Paragraph=p",
			toolbar: "formatselect bold italic | undo redo | link | " +
			         "blockquote bullist numlist | pastetext code",
			height: 400,
			width: 760,
			link_list: cms_tinymce_linklist // created by cms.views.linklist
		}, tinymce_config);
	
	$('.edit-switcher').click(function() {
	    $.cookie('adhoc-edit_mode', null, {path: '/'});
	    location.reload();
	    return false;
	});
	
	function edit(block) {
		var save_url = $(block).data('save_url');
		
		if (currently_editing) {
			return false;
		}
		
		if ($(block).hasClass('placeholder')) {
			var raw_content = '';
		}
		else {
			var raw_content = $.trim($(block).find('input[name="content"]').val());
		}
		
		if ($(block).hasClass('cms-image')) {
		  var form = $('#cms-imageform'),
		      image_url = $(block).data('image_url'),
		      description = $(block).data('description');
		      
		  form.find('form').attr('action', save_url);
		
		  if (image_url) {
		    form.find('h2').html('Change image');
		    form.find('div.current img').attr('src', image_url);
		    form.find('div.current').css('visibility', 'visible');
		    form.find('input[name$="description"]').val(description);
		  }
		  else {
		    form.find('h2').html('Add image');
		    form.find('div.current').css('visibility', 'hidden');
		  }
		  
		  showForm('image');
		}
		else {
		    var inner = $(block).find(".cms-inner");
		    
		    function update_block(page_content) {
                var updated_body = $('<div>' + page_content + '</div>'),
                    // save_url is unique to the block, so use it to find the updated block 
                    updated_block = updated_body.find('.cms-block').filter(function() {
                        return $(this).data('save_url') === save_url;
                    }),
                    updated_content = $.trim(updated_block.find('.cms-inner').html());
                
                inner.html(updated_content || "Click to add text");
                if (!updated_content) {
                    $(block).addClass("placeholder");
                }                        
		    };
		    
            if ($(block).data('format') === 'html') {
                $('#cms-htmlform #id_html-content').val(raw_content).html(raw_content);
                tinyMCE.get("id_html-content").setContent(raw_content);
                $('#cms-htmlform #id_format').val($(block).data('format'));
                
                
                $('#cms-htmlform form').ajaxForm({
                    url: save_url,
                    success: function(data) {
                        update_block(data.page_content);
                        $(block).find('input[name="content"]').val(data.content);
                        highlightBlock(block);
                        currently_editing = false;
                        if (typeof post_edit_callback === 'function') {
                            post_edit_callback(block);
                        }
                    },
                    beforeSubmit: function() {
                        $(block).removeClass("placeholder");
                        inner.html(throbberString);
                        hideForm('html', false);
                    },
                    dataType: 'json'
                });
                showForm('html');
            }
            else {
                var reset_callbacks = [];
                
                $(block).parents('a').each(function(e) {
                    var me = $(this),
                        cancel = function() {
                            return false;
                        };
                    me.bind('click', cancel);
                    reset_callbacks.push(function() {
                        setTimeout(function() {
                            me.unbind('click', cancel);
                        }, 100);
                    });
                });
                            
                var editFormContainer = $('#cms-textform').clone();
                raw_content_escaped = raw_content.replace('>', '&gt;').replace('<', '&lt;');
                editFormContainer.find('textarea[name$="content"]').val(raw_content).html(raw_content_escaped);
    
                editFormContainer.show().find('textarea').css({'height': $(block).height()});
                
                $(block).parent().append(editFormContainer);
                $(block).css({'display': 'none'});
    
                editFormContainer.find('textarea').focus().select();
                
                function hideTextForm() {
                    $(block).css({'display': 'block'});
                    editFormContainer.remove();
                    currently_editing = false;
                    $(reset_callbacks).each(function(i, fn) { fn(); });
                };
                editFormContainer.find('input.cancel').click(hideTextForm);
                
                
                editFormContainer.find('form').ajaxForm({
                    url: save_url,
                    success: function(data) {
                        update_block(data.page_content);
                        highlightBlock(block);
                        currently_editing = false;
                        $(block).find('input[name="content"]').val(data.content);
                        $(reset_callbacks).each(function(i, fn) { fn(); });
                        if (typeof post_edit_callback === 'function') {
                            post_edit_callback(block);
                        }
                    },
                    beforeSubmit: function() {
                        $(block).removeClass("placeholder");
                        inner.html(throbberString);
                        hideTextForm();
                    },
                    dataType: 'json'
                });
                
                /* manually submit the form if we're killing the click event above due to
                   the parent being an <a> tag */
                if ($(block).parents('a').length) {
                    editFormContainer.find('form input[type=submit]').click(function() {
                        $(this).parents('form').eq(0).submit();
                    });
                }
            }
        }
		
		currently_editing = true;
	};
	
	tinyMCE.init($.extend(tinymce_init_object, {
    	mode: 'exact',
    	elements: 'id_html-content'
	}));

	$('.cms-form input.cancel').click(function() {
		hideForm();
	});

	$('.cms-image').each(function () {
	    // img could be any element, not necessarily <img>
	    var el = $(this).find('.cms-inner').children();
	
	    // if there's no image and we're cropping, size the placeholder the same as
	    // the image so as not to break layouts.
	    if (!el.length && $(this).attr('constraint')) {
	        var bits = $(this).attr('constraint').split('x');
	        $(this).css({
	            width: bits[0] ? bits[0] + 'px' : 'auto',
	            height: bits[1] ? bits[1] + 'px' : 'auto',
	            lineHeight: bits[2] + 'px',
	            display: 'inline-block'
	        });
	    }
	    
	    // match the display css prop for the same reason
	    $(this).css('display', el.css('display') || 'inline-block');
	});
	
	$('.cms-block, .cms-image').each(function() {
        var me = $(this);
	    me.hover(function() {
    	    me.addClass('hovered');
	    }, function() {
    	    me.removeClass('hovered');
	    });
	    me.click(function(e) {
            if (!e.originalTarget || e.originalTarget.tagName.toLowerCase() != 'a') {
                edit(me[0]);
                return false;
            }
	    });
	});
	
	$('#cms-menu .page-options').click(function() {
    	showForm('page');
    	return false;
	});	
	$('#cms-menu .new-page').click(function() {
    	showForm('newpage');
	    return false;
	});
	
	$('#cms-pageform form, #cms-newpageform form').ajaxForm({
        'success': function(data, status, form) {
            var wrap = $(form).find('.wrap').eq(0);
            wrap.find('.error').remove();
            wrap.find('p').removeClass('haserrors');
            wrap.find('.message').remove();
            
            if (data.success) {
                wrap.append($('<div>').addClass('message').html(data.message || 'Page saved'));
                setTimeout(function() {
                    window.location = data.url;
                }, 300);
            }
            else {
                var input;
                for (key in data.errors) {
                    input = wrap.find('*[id$=' + key + ']');
                    input.parent().addClass('haserrors').prepend($('<span>' + data.errors[key] + '</span>').addClass('error'));
                }
            }
        },
        'beforeSubmit': function(data, status, form) {
            var wrap = $(form).find('.wrap').eq(0);
            wrap.find('.message').remove();
            wrap.append($('<div>').addClass('message').html('Page saved'));
        },
        'dataType': 'json'
    });
    
    $('#cms-imageform form').submit(function() {
        $(this).find('.wrap').append($('<div>').addClass('message').html('Saving...'));
    });
	
	function highlightBlock(block) {
		$(block).addClass('cms-highlight');
		
		setTimeout(function() {
            $(block).addClass('cms-highlight-animate');
            $(block).removeClass('cms-highlight');
        }, 200);
        setTimeout(function() {
            $(block).removeClass('cms-highlight-animate');
		}, 700);
	};

	function showForm(which) {
		var overlay = $('#cms-' + which + 'overlay'),
			form = overlay.children('.cms-form');
		overlay.stop().css({
			opacity: 0,
			display: 'block'
		}).animate({opacity: 1}, 300)[0].visible = true;
		var margin = (overlay.height() - form.outerHeight()) / 2;
		form.css({
			marginTop: Math.max(20, margin) + 'px'
		});
	};
	function hideForm(which, animate) {
	    if (which) {
		    var overlay = $('#cms-' + which + 'overlay');
		}
		else {
		    var overlay = $('.cms-overlay');
		}
		
		overlay.stop().each(function() {
		    this.visible = false;
		});
		if (animate === false) {
			overlay.css({display: 'none'});
		}
		else {
			overlay.animate({opacity: 0}, 'fast', function() {
				overlay.css({display: 'none'});
			});
		}
		currently_editing = false;

	};


}; // init done inline so settings can be passed in - see templates/adhoc/cms/editor.js
