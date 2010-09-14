var djangocms2000 = function ($, highlight_start_color, highlight_end_color, tinymce_init_object, filebrowser_url, buttons, tinymce_content_css, linklist_url, is_superuser) {
	
	var throbberString = "<span class='throbber'>Saving...</span>",
		currently_editing = false;
	
	
	if (!tinymce_init_object) {
	    tinymce_init_object = {
			setup: is_superuser ? function(){} : function(ed) {
       
				// Force Paste-as-Plain-Text
				ed.onPaste.add( function(ed, e, o) {
					ed.execCommand('mcePasteText', true);
					return tinymce.dom.Event.cancel(e);
				});
			   
			},
            paste_auto_cleanup_on_paste: true,
			//"elements: "id_raw_content",
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
			plugins: "paste",
			relative_urls: false
		};
	}

	
	// filebrowser callback - only used if filebrowser_url is specified
	function djangoFileBrowser(field_name, url, type, win) {
        var url = filebrowser_url + "?pop=2&type=" + type;
    
        tinyMCE.activeEditor.windowManager.open(
            {
                'file': url,
                'width': 820,
                'height': 500,
                'resizable': "yes",
                'scrollbars': "yes",
                'inline': "no",
                'close_previous': "no"
            },
            {
                'window': win,
                'input': field_name,
                'editor_id': tinyMCE.selectedInstance.editorId
            }
        );
        return false;
    };
	
	tinymce_init_object['file_browser_callback'] = djangoFileBrowser;
	
	
	/*
	$('body').css({
		'padding-top': '30px'
	});
	*/
	
	//$("#djangocms2000-menu").prependTo('body');
	//var topMenu = $("#djangocms2000-menu").clone();
	//$('body').remove("#djangocms2000-menu");
	//$('body').prepend(topMenu);
	
	function edit(block) {
		//console.log(block, currently_editing, $(block).attr('type'));
		
		if (currently_editing) {
			return false;
		}
		
		
		if ($(block).hasClass('placeholder')) {
			var raw_content = '';
		}
		else {
			var raw_content = $.trim($(block).find('input').val());
		}
		
		if ($(block).attr('blocktype') === 'image') {
			$('#djangocms2000-imageform #id_image_id').val($(block).attr('image_id'));
			$('#djangocms2000-imageform #id_redirect_to').val(window.location);
			
			if ($(block).find('img').length) {
				$('#djangocms2000-imageform h2').html('Change image');
				$('#djangocms2000-imageform div.current img').attr('src', $(block).find('img').eq(0).attr('src'));
				$('#djangocms2000-imageform div.current').css({'display': 'block'});
			}
			else {
				$('#djangocms2000-imageform h2').html('Add image');
				$('#djangocms2000-imageform div.current').css({'display': 'none'});
			}
			
			showForm('image');
		}
		else if ($(block).attr('format') === 'html') {
			$('#djangocms2000-htmlform #id_html-raw_content').val(raw_content).html(raw_content);
			tinyMCE.get("id_html-raw_content").setContent(raw_content);
			$('#djangocms2000-htmlform #id_html-block_id').val($(block).attr('block_id'));
			$('#djangocms2000-htmlform #id_html-format').val($(block).attr('format'));
            
            
			$('#djangocms2000-htmlform form').ajaxForm({
				'success': function(data) {
					var raw_content = $.trim(data.raw_content),
						compiled_content = $.trim(data.compiled_content);
					$(block).find('input').val(raw_content);
					$(block).find("span.inner").html(compiled_content || "Click to add text");
					
					if (!compiled_content) {
						$(block).addClass("placeholder");
					}
					highlightBlock(block);
					currently_editing = false;
					
				},
				'beforeSubmit': function() {
					$(block).removeClass("placeholder");
					$(block).find("span.inner").html(throbberString);
					hideForm('html', false);
				},
				'dataType': 'json'
			});
			showForm('html');
		}
		else {
		    raw_content_escaped = raw_content.replace('<', '&lt;').replace('<', '&lt;');
			$('#djangocms2000-textform #id_raw_content').val(raw_content).html(raw_content_escaped);
			$('#djangocms2000-textform #id_block_id').val($(block).attr('block_id'));
			$('#djangocms2000-textform #id_format').val($(block).attr('format'));
			
			var editFormContainer = $('#djangocms2000-textform').clone();
			editFormContainer.find('textarea').css({'height': $(block).height()});
			editFormContainer.css({'display': 'block'});
			
			$(block).parent().append(editFormContainer);
			$(block).css({'display': 'none'});
			
			
			
			editFormContainer.find('textarea').focus().select();
			
			function hideTextForm() {
				$(block).css({'display': 'block'});
				editFormContainer.remove();
				currently_editing = false;
			};
			editFormContainer.find('input.cancel').click(hideTextForm);
			

			editFormContainer.find('form').ajaxForm({
				'success': function(data) {
					$(block).find("span.inner").html($.trim(data.compiled_content) || "Click to add text");
					if (!$.trim(data.compiled_content)) {
						$(block).addClass("placeholder");
					}
					highlightBlock(block);
					currently_editing = false;
					$(block).find('input').val($.trim(data.raw_content));
				},
				'beforeSubmit': function() {
					$(block).removeClass("placeholder");
					$(block).find("span.inner").html(throbberString);
					hideTextForm();
				},
				'dataType': 'json'
			});			
		}

		
		
		currently_editing = true;
	};
	
	
	$(function() {
	
		$('#id_html-raw_content').tinymce(tinymce_init_object);

		$('.djangocms2000-form input.cancel').click(function() {
			hideForm();
		});	
	
		
		$('.djangocms2000-block, .djangocms2000-image').each(function() {
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
		
		$('#djangocms2000-menu .page-options').click(function() {
    		showForm('page');
	    });	
		$('#djangocms2000-menu .new-page').click(function() {
    		showForm('newpage');
	    });
	    
	    $('#djangocms2000-pageform form, #djangocms2000-newpageform form').ajaxForm({
            'success': function(data, status, form) {
                var wrap = $(form).find('.wrap').eq(0);
                wrap.find('.error').remove();
                wrap.find('p').removeClass('haserrors');
                
                if (data.success) {
                    wrap.append($('<div>').addClass('message').html('Page saved'));
                    setTimeout(function() {
                        window.location = data.uri;
                    }, 1000);
                }
                else {
                    var input;
                    for (key in data.errors) {
                        input = wrap.find('*[id$=' + key + ']');
                        input.parent().addClass('haserrors').prepend($('<span>' + data.errors[key] + '</span>').addClass('error'));
                    }
                }
            },
            'dataType': 'json'
        });	
	    
		
	});
	
	function highlightBlock(block) {
		$(block).css({backgroundColor: (highlight_start_color || "#ff0")}).animate({backgroundColor: (highlight_end_color || "#fff")}, 500, function() {
			$(block).css({backgroundColor: ("")});	
		});
	};

	function showForm(which) {
	     $('#djangocms2000-' + which + 'overlay').stop().css({opacity: 0, display: 'block'}).animate({opacity: 1}, 300)[0].visible = true;
	};
	function hideForm(which, animate) {
	    if (which) {
		    var overlay = $('#djangocms2000-' + which + 'overlay');
		}
		else {
		    var overlay = $('.djangocms2000-overlay');
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


