README : twee2sam
======

This tool is intended to convert [Twee] projects (that you can export from [Twine]) into [SAM] projects. With it, it's possible to create Sega Master System adventure games using Twine.

Currently, it supports a subset of the Twine commands; so far, only links and images are supported.

You can see a working example at example/simple; run Compile.bat to make it run.


Image support
-------------

The images must be in the png format, have a resolution of 256x144, and can't have more than 16 colors. Be careful to not use an exceedingly detailed image, as SAM can't display images with more than 320 tiles. 



History
=======

2014-01-27: Generated a compiled exe version of twee2sam.py, so that people can use the tool without having Python installed.

2014-01-26: Implemented image displaying support.

2014-01-23: First working version. Links are supported.




[twee]: https://github.com/tweecode/twee "Twee story engine"
[twine]: https://github.com/tweecode/twine "A visual tool for creating interactive stories for the Web"
[SAM]: http://www.haroldo-ok.com/sam-simple-adventure-maker-sms/ "SAM - Simple Adventure Maker"
[Python]: http://www.python.org/ "Python Programming Language"
