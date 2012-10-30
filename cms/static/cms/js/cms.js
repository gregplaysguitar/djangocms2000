    var cms = function ($, highlight_color, buttons, tinymce_content_css, linklist_url, post_edit_callback) {
	
	
	var throbberString = "<span class='throbber'>Saving...</span>",
		currently_editing = false,
		tinymce_init_object = {
			setup: function() {
			    // hack to stop tinymce's silly alert (see paste plugin source code)
			    var cookie = tinymce.util.Cookie;
			    if (!cookie.get("tinymcePasteText")) {
    			    cookie.set("tinymcePasteText", "1");
    			}
			},
			setupcontent_callback: function(id) {
			    // set plain-text paste to be on by default
			    tinyMCE.get(id).execCommand('mcePasteText', true);
			},
            paste_auto_cleanup_on_paste: true,
			language: "en",
			directionality: "ltr",
			theme: "advanced",
			strict_loading_mode: 1,
			mode: "exact",
			height: "400px",
			width: "760px",
			content_css: tinymce_content_css,
			external_link_list_url: linklist_url,
			theme_advanced_toolbar_location: "top",
			theme_advanced_toolbar_align: "left",
			theme_advanced_buttons1: buttons,
			theme_advanced_buttons2: "",
			theme_advanced_buttons3: "",
            theme_advanced_statusbar_location: "bottom",
            theme_advanced_resizing: true,
			plugins: "paste,inlinepopups",
			relative_urls: false
		};
	
	
	function edit(block) {
		var save_url = $(block).attr('save_url');
		
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
		    var img = $(block).find('img');
		    // TODO ajaxify this
			$('#cms-imageform form').attr('action', save_url);
			if (img.length && !img.hasClass('placeholder')) {
				$('#cms-imageform h2').html('Change image');
				$('#cms-imageform div.current img').attr('src', img.attr('src'));
				$('#cms-imageform div.current').css({'visibility': 'visible'});
				$('#cms-imageform input[name$="description"]').val(img.attr('alt'));
			}
			else {
				$('#cms-imageform h2').html('Add image');
				$('#cms-imageform div.current').css({'visibility': 'hidden'});
			}
			
			showForm('image');
		}
		else {
		    var inner = $(block).find(".cms-inner");
		    
		    function update_block(page_content) {
                var updated_body = $('<div>' + page_content + '</div>'),
                    // save_url is unique to the block, so use it to find the updated block 
                    updated_block = updated_body.find('.cms-block[save_url="' + save_url + '"]'),
                    updated_content = $.trim(updated_block.find('.cms-inner').html());
                
                inner.html(updated_content || "Click to add text");
                if (!updated_content) {
                    $(block).addClass("placeholder");
                }                        
		    };
		    
            if ($(block).attr('format') === 'html') {
                $('#cms-htmlform #id_html-content').val(raw_content).html(raw_content);
                tinyMCE.get("id_html-content").setContent(raw_content);
                $('#cms-htmlform #id_format').val($(block).attr('format'));
                
                
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
	
	
	$(function() {
	
		$('#id_html-content').tinymce(tinymce_init_object);

		$('.cms-form input.cancel').click(function() {
			hideForm();
		});

		$('.cms-image').each(function () {
		    // if there's no image and we're cropping, size the placeholder the same as
		    // the image so as not to break layouts.
		    if (!$(this).find('img').length && $(this).attr('constraint')) {
				var bits = $(this).attr('constraint').split('x');
                $(this).css({
                    width: bits[0] ? bits[0] + 'px' : 'auto',
                    height: bits[1] ? bits[1] + 'px' : 'auto',
                    lineHeight: bits[2] + 'px',
                    display: 'inline-block'
                });
			}
		});
		$('.cms-block, .cms-image').each(function() {
			$(this).append('<span class="editMarker"></span>');
		}).mouseover(function() {
			if (!currently_editing) {
				$(this).addClass('hovered').find('span.editMarker').css({'display': 'block'});
			}
		}).mouseout(function() {
			$(this).removeClass('hovered').find('span.editMarker').css({'display': 'none'});
		}).click(function(e){
		    if (!e.originalTarget || e.originalTarget.tagName.toLowerCase() != 'a') {
    			edit(this);
	    		return false;
		    }
		}).find('span.editMarker').click(function(){
			edit(this.parentNode);
			return false;
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
	    
		
	});
	
	function highlightBlock(block) {
		$(block).css({
		    backgroundColor: highlight_color		    
		});
		setTimeout(function() {
            $(block).css({
                '-moz-transition': 'all 500ms',
                '-webkit-transition': 'all 500ms',
                transition: 'all 500ms',
                backgroundColor: ''
            });
            setTimeout(function() {
                $(block).css({
                    '-moz-transition': 'none',
                    '-webkit-transition': 'none',
                    transition: 'none'
                });
            }, 500);
        }, 1);
	};

	function showForm(which) {
	     $('#cms-' + which + 'overlay').stop().css({opacity: 0, display: 'block'}).animate({opacity: 1}, 300)[0].visible = true;
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


}; //init done inline so settings can be passed in - see templates/editor.html


