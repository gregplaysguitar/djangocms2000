$(function() {

id_list = [];
$('textarea.djangocms2000.html').each(function(i, item) {
    id_list.push(item.id);
});


if (id_list.length) {
    
    tinyMCE.init({
        setup: function(ed) {
            // Force Paste-as-Plain-Text
            ed.onPaste.add( function(ed, e, o) {
                ed.execCommand('mcePasteText', true);
                return tinymce.dom.Event.cancel(e);
            });
        },
        "paste_auto_cleanup_on_paste" : true,
        "relative_urls": "",
        "theme_advanced_toolbar_location": "top",
        "theme_advanced_toolbar_align": "left",
        //"spellchecker_rpc_url": "/tinymce/spellchecker/",
        "content_css": "",
        "language": "en",
        //"spellchecker_languages": "Arabic=ar,Bengali=bn,Bulgarian=bg,Catalan=ca,Czech=cs,Welsh=cy,Danish=da,German=de,Greek=el,+English=en,Spanish / Argentinean Spanish=es,Estonian=et,Basque=eu,Persian=fa,Finnish=fi,French=fr,Irish=ga,Galician=gl,Hungarian=hu,Hebrew=he,Hindi=hi,Croatian=hr,Icelandic=is,Italian=it,Japanese=ja,Georgian=ka,Korean=ko,Khmer=km,Kannada=kn,Latvian=lv,Lithuanian=lt,Macedonian=mk,Dutch=nl,Norwegian=no,Polish=pl,Portuguese / Brazilian Portuguese=pt,Romanian=ro,Russian=ru,Slovak=sk,Slovenian=sl,Serbian=sr,Swedish=sv,Tamil=ta,Telugu=te,Thai=th,Turkish=tr,Ukrainian=uk,Simplified Chinese / Traditional Chinese=zh",
        "theme_advanced_buttons1": "h3,h4,|,bold,italic,|,undo,redo,|,link,image,|,bullist,numlist,|,code,pastetext",
        "directionality": "ltr",
        //"height": "200px",
        //"width": "620px",
        "theme": "advanced",
        "strict_loading_mode": 1,
        "mode": "exact",
        "plugins": "heading,paste",
        "theme_advanced_buttons3": "",
        "theme_advanced_buttons2": "",
        "elements": id_list.join(',')
        //file_browser_callback: "CustomFileBrowser"
    });
}



});