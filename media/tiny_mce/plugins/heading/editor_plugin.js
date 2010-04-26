/**
 *
 * @author WSL.RU
 * @copyright Copyright (c) 2006-2009. All rights reserved.
 *
 */

(function() {

	tinymce.create('tinymce.plugins.heading', {
		init : function(ed, url) {
		// adding buttons
			for (var i =1; i<=6;i++) { 
				ed.addButton('h'+i, { title : ed.getLang('advanced.h'+i,'h'+i)+' (Ctrl+'+i+')', image : url+'/img/h'+i+'.gif', cmd: 'mceHeading'+i }); 
			}

			ed.addCommand('mceHeading1', function() { 
				var ct=	ed.getParam("heading_clear_tag",false)?"<"+ed.getParam("heading_clear_tag","")+">":"";
				if (ed.selection.getNode().nodeName.toLowerCase() != 'h1') ct = '<h1>';
				ed.execCommand('FormatBlock', false, ct) 
			});
			ed.addCommand('mceHeading2', function() { 
				var ct=	ed.getParam("heading_clear_tag",false)?"<"+ed.getParam("heading_clear_tag","")+">":"";
				if (ed.selection.getNode().nodeName.toLowerCase() != 'h2') ct = '<h2>';
				ed.execCommand('FormatBlock', false, ct) 
			});
			ed.addCommand('mceHeading3', function() { 
				var ct=	ed.getParam("heading_clear_tag",false)?"<"+ed.getParam("heading_clear_tag","")+">":"";
				if (ed.selection.getNode().nodeName.toLowerCase() != 'h3') ct = '<h3>';
				ed.execCommand('FormatBlock', false, ct) 
			});
			ed.addCommand('mceHeading4', function() { 
				var ct=	ed.getParam("heading_clear_tag",false)?"<"+ed.getParam("heading_clear_tag","")+">":"";
				if (ed.selection.getNode().nodeName.toLowerCase() != 'h4') ct = '<h4>';
				ed.execCommand('FormatBlock', false, ct) 
			});
			ed.addCommand('mceHeading5', function() { 
				var ct=	ed.getParam("heading_clear_tag",false)?"<"+ed.getParam("heading_clear_tag","")+">":"";
				if (ed.selection.getNode().nodeName.toLowerCase() != 'h5') ct = '<h5>';
				ed.execCommand('FormatBlock', false, ct) 
			});
			ed.addCommand('mceHeading6', function() { 
				var ct=	ed.getParam("heading_clear_tag",false)?"<"+ed.getParam("heading_clear_tag","")+">":"";
				if (ed.selection.getNode().nodeName.toLowerCase() != 'h6') ct = '<h6>';
				ed.execCommand('FormatBlock', false, ct) 
			});

			ed.onNodeChange.add( function(ed, cm, n) {cm.setActive('h1', n.nodeName.toLowerCase() == 'h1');});
			ed.onNodeChange.add( function(ed, cm, n) {cm.setActive('h2', n.nodeName.toLowerCase() == 'h2');});
			ed.onNodeChange.add( function(ed, cm, n) {cm.setActive('h3', n.nodeName.toLowerCase() == 'h3');});
			ed.onNodeChange.add( function(ed, cm, n) {cm.setActive('h4', n.nodeName.toLowerCase() == 'h4');});
			ed.onNodeChange.add( function(ed, cm, n) {cm.setActive('h5', n.nodeName.toLowerCase() == 'h5');});
			ed.onNodeChange.add( function(ed, cm, n) {cm.setActive('h6', n.nodeName.toLowerCase() == 'h6');});
			
		},

		getInfo : function() {
			return {
				longname :  'Heading plugin',
				author :    'WSL.RU / Andrey G, ggoodd',
				authorurl : 'http://wsl.ru',
				infourl :   'mailto:ggoodd@gmail.com',
				version :   '1.3'
			};
		}
	});

	
	tinymce.PluginManager.add('heading', tinymce.plugins.heading);

})();

