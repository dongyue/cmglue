=============
CMGlue Readme
=============

:Author: Dong Yue
:Web site: http://cmglue.sourceforge.net/
:Source code: http://github.com/dongyue/cmglue
:Copyright: under BSD license

.. contents::
.. sectnum::


What's CMGlue?
==============

CMGlue (Configuration Management Glue) is a better git-submodule, 
to manage a workspace which may contains multiple components
that may from various version control tools such as Git and SVN (Subversion), 
or even just from a shared folder.

**Note**: currently CMGlue supports Git only.


Installation
============

Prerequisites
-------------

1. Git should be installed. Type below to verify::

    git --help
    
Besides using your package management tool (on Linux),
you may try this link to download Git and install: http://git-scm.com/download

2. Git config: Make sure you set *user.name* and *user.email* in Git.

3. Git config: Make sure you set *merge.tool* in Git. (Always *kdiff3*)

4. Git config: Make sure the value of *color.ui* is **not** *always*. 
   *auto* is OK. 

5. Git config: Make sure the value of *core.editor* is a text editor and
   **works well** with Git. 
   It could be *nano* on Linux, or *AkelPad.exe* on Windows.

6. SVN and so on should be installed, if some of your codes are under their 
   control.

7. Python version 3.0 or above should be installed. 
   Type below to verify (on Linux)::

    python3 --version

On Windows please use::

    python --version
   
Besides using your package management tool (on Linux),
you may try this link to dowload Python and install: 
http://www.python.org/ftp/python/

8. Make sure your PATH's value includes Python's path and Python's scripts'
   path. On Windows it might be::

    C:\Python31;C:\Python31\Scripts
    
On Unix you needn't set it generally.

    
Install
-------

1. Download the installation package from http://cmglue.sourceforge.net/.
   *.tar.gz* file is for Linux users, while *.zip* is for Windows users.

2. Un-zip/un-package it.

3. Go to the directory, and then (On Linux)::
    
    sudo ./setup.py install
    
On Windows it probably be::

    setup.py install

That's all. For more options and information about Python packages installation:
http://docs.python.org/py3k/install/index.html


Test & Demo
-----------

To test the installation, under any path run::

  cmg --help

To create the environment for a demo, under any path run::

  cmg_create_demo

If you are on Linux, it in fact called 
(such as) */usr/local/bin/cmg_create_demo*,
to create a demo environement under *~/cmg_demo*.

If you are on Windows, it in fact called
(such as) *C:\\Python31\\Scripts\\cmg_create_demo.bat*,
to create a demo environement under *C:\\cmg_demo*.


More information?
=================

1. Browse the help document *cmg_manual.html*. On Linux it should be copied to
   */usr/local/Doc/*, while on Windows it should be (such as) *C:\\Python31\\Doc\\*.
   Anyway, it firstly exists in the installation package.

2. Visit its website: http://cmglue.sourceforge.net/

3. Get source code: http://github.com/dongyue/cmglue

4. Email the author: me@dongyue.name

