#!/usr/bin/python3

from distutils.core import setup

import cmglib.common

setup(name = 'CMGlue',
    version = cmglib.common.VERSION,
    description = 'Configuration Management Glue: a better git-submodule',
    author = 'Dong Yue',
    author_email = 'me@dongyue.name',
    url = '(TBD)',
    platforms = 'all popular platforms',
    license = '(TBD)',
    long_description = 'CMGlue (Configuration Management Glue) is a better git-submodule, to manage a workspace which may contains multiple components that may from various version control tools such as Git and SVN (Subversion), or even just from a shared folder.',
    packages=['cmglib'],
    scripts=['cmg', 'cmg.bat', 'cmg_create_demo', 'cmg_create_demo.bat'],
    data_files=[('Doc', ['cmg_manual.txt', 'cmg_manual.html'])]
    )
