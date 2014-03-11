README : twee2sam
======

This tool is intended to convert [Twee] projects (that you can export from [Twine]) into [SAM] projects. With it, it's possible to create Sega Master System adventure games using Twine.

Currently, it supports a subset of the Twine commands; so far, only links and images are supported.

You can see a working example at example/simple; run Compile.bat to make it run.


Compiled version
----------------

You can get a compiled version from https://dl.dropboxusercontent.com/u/1235428/sms/twee2sam-2014-02-01a.rar

Of from the [SMSPower thread](http://www.smspower.org/forums/viewtopic.php?t=14568)


Image support
-------------

The images must be in the png format, have a resolution of 256x144, and can't have more than 16 colors. Be careful to not use an exceedingly detailed image, as SAM can't display images with more than 320 tiles. 

Commands
========

[img[imagename.png]]
--------------------

Displays an image

&lt;&lt;pause&gt;&gt;
---------

Forces a page break or, if there's no text, just waits for the user to press any button.

&lt;&lt;set *variable* to *expression*&gt;&gt;
---------

Sets the value of a variable to the value of the expression.

&lt;&lt;if *expression*&gt;&gt;...&lt;&lt;endif&gt;&gt;
---------

Conditionally executes the code between &lt;&lt;if &gt;&gt; and &lt;&lt;endif&gt;&gt; if the *expression* evaluates to *true*.

Note: &lt;&lt;else&gt;&gt; is not implemented yet.

&lt;&lt;music *"filename.epsgmod"*&gt;&gt;
---------

Plays a music in *.epsgmod* format, as exported by [Mod2PSG2]

Expressions
-----------

Currently, twee2sam has only limited expression support:

- **true** evaluates to true;
- **false** evaluates to false;
- ***variable name*** evaluates to the current value of the variable;
- **not** ***variable_name*** or ***!variable_name*** evaluates to the logical negation of the current value of the variable; that is, if 'variable' is true, '!variable' is false, and vice versa.

So, essentially, the tool is currently supporting either single boolean constants or single variables, with or without negation. Future versions will support more complex expressions.


History
=======

2014-02-19: Updated SAM to use PS Gaiden compression.

2014-02-17: Corrected word wrapping bug.

2014-02-01: Implemented the &lt;&lt;set&gt;&gt; and &lt;&lt;if&gt;&gt; commands.

2014-01-30: Implemented text buffer overflow checking and also implemented the &lt;&lt;pause&gt;&gt; command.

2014-01-27: Generated a compiled exe version of twee2sam.py, so that people can use the tool without having Python installed.

2014-01-26: Implemented image displaying support.

2014-01-23: First working version. Links are supported.




[twee]: https://github.com/tweecode/twee "Twee story engine"
[twine]: https://github.com/tweecode/twine "A visual tool for creating interactive stories for the Web"
[SAM]: http://www.haroldo-ok.com/sam-simple-adventure-maker-sms/ "SAM - Simple Adventure Maker"
[Python]: http://www.python.org/ "Python Programming Language"
[Mod2PSG2]: http://www.smspower.org/Music/Mod2PSG2 "A tracker for the Sega Master System's sound chip"
