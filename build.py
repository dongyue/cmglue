#!/usr/bin/python3

import os
import shutil
import subprocess

import cmglib.common

def main():
    """package and deploy."""
    
    cmglib.common.cfgs['verbose'] = True

    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    if os.name == 'nt':
        cmglib.common.command_free("rst2html.py cmg_manual.txt cmg_manual.html", ".")
        cmglib.common.command_free("setup.py sdist --formats=zip", ".")
        #cmglib.common.command("python setup.py bdist --format=msi", ".")
        cmglib.common.command_free("unzip CMGlue-" + cmglib.common.VERSION + ".zip", "dist")
        cmglib.common.command_free("setup.py install", os.path.join("dist", "CMGlue-" + cmglib.common.VERSION))
    elif os.name == 'posix':
        cmglib.common.command_free("rst2html cmg_manual.txt cmg_manual.html", ".")
        cmglib.common.command_free("./setup.py sdist --formats=gztar", ".")
        cmglib.common.command_free("tar -zxvf CMGlue-" + cmglib.common.VERSION + ".tar.gz", "dist")
        cmglib.common.command_free("sudo ./setup.py install", os.path.join("dist", "CMGlue-" + cmglib.common.VERSION))
    else:
        print("Unknown OS. Failed to build.")
        exit(2)

if __name__ == '__main__': main()
