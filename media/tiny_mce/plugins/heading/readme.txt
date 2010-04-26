Plugin: Heading
~~~~~~~~~~~~~~~
  Here is a Heading plugin for TinyMCE by WSL.RU
  This plugin adds H1-H6 buttons to TinyMCE. 
  This plugin was developed by Andrey G and modified by ggoodd.


Version History
~~~~~~~~~~~~~~~
  1.3
  * rewrited for TinyMCE 3.x
  - removed keyboard shortcuts (use Ctrl+1-6) 
  
  1.2 by ggoodd
  + added keyboard shortcuts 
  + added heading_clear_tag option
  - removed language pack, advansed theme variables used instead

  1.1 by ggoodd
  + added buttons switching
  - removed NoHeading button 

  1.0 by Andrey G
  * initial version 


Installation
~~~~~~~~~~~~
  - Copy the heading directory to the plugins directory of TinyMCE.
  - Add plugin to TinyMCE plugin option list.
  - Add heading buttons to button list.
  - Set heading_clear_tag option if you need. Default value is undefined. 
    This option holds formating tag which is added on heading removal.


Initialization Example
~~~~~~~~~~~~~~~~~~~~~~
tinyMCE.init({

    theme : "advanced",
    mode : "exact",
    
    plugins : "heading",
    heading_clear_tag : "p",
    theme_advanced_buttons1_add_before : "h1,h2,h3,h4,h5,h6,separator",

});
