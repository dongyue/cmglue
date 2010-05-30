import sys
import os
import shutil


from cmglib import common

def read_egg(root):
    """read egg-info file and return the source url. return "" if nothing found."""

    try:
        f = open(root + ".egg-info", 'r')
    except:
        return ""
    
    for line in f:
        if line != "":
            return line.strip()

    f.close()
    
    return ""

def write_egg(root, url):
    """write source url to egg-info file."""

    try:
        f = open(root + ".egg-info", 'w')
    except:
        sys.stderr.write("Failed: can not open file '" + root + ".egg-info' to write.")
        sys.exit(2)
        
    f.write(url + "\n")
    f.close()
    

def copy_file(root, url):
    """copy a file from url to local."""

    try:
        shutil.copy2(url, root)
    except:
        sys.stderr.write("Failed: can not copy file from  '" + url + "' to '" + root + "'.")
        sys.exit(2)
    
def copy_tree(root, url):
    """copy a directory from url to local."""


    try:
        shutil.copytree(url, root)
    except:
        sys.stderr.write("Failed: can not copy tree from  '" + url + "' to '" + root + "'.")
        sys.exit(2)

def remove(root):
    """remove everything under given path(root)."""

    if not os.path.exists(root):
        return
    if os.path.isfile(root):
        try:
            os.remove()
        except:
            sys.stderr.write("Failed: can not remove file  '" + root + "'.")
            sys.exit(2)
    if os.path.isdir(root):
        try:
            os.remove()
        except:
            sys.stderr.write("Failed: can not remove tree  '" + root + "'.")
            sys.exit(2)
    else:
        sys.stderr.write("Failed: Can not remove '" + root + "' as it is neither file nor dir.")
        sys.exit(2)
    
#
# below are commands called from commands.py for each component.
#


def download(root, config, component, b_file):
    """Download/sync/update a component from shared folder to working copy.
    
    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component. 'b_file' indicates it's a file or dir.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)
    
    if not config.has_option(component, "url"):
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'url' option exists in '" + component + "' section.")
        sys.exit(2)
    
    url = config.get(component, "url")
    current_url = read_egg(root)
    if current_url == url and os.path.exists(root):
        print("Still on '" + url + "'.")
        return
    
    remove(root)

    if b_file:
        copy_file(root, url)
    else:
        copy_tree(root, url)
    
    write_egg(root, url)
    
    print("Success to copy from '" + url + "' to '" + root + "'.")

    
def status(root, config, component):
    """Show status of a component.
    
    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)
    
    if not config.has_option(component, "url"):
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'url' option exists in '" + component + "' section.")
        sys.exit(2)
    
    url = config.get(component, "url")
    current_url = read_egg(root)
    
    if not os.path.exists(root):
        print("Warning: this component doesn't exists in workspace.")
    elif current_url == "":
        print("Warning: can not get the source information from file '" + root + ".egg-info'.")
    elif current_url != url:
        print("Warning: this component should from '" + url + "', but now '" + current_url + "'.")


def upload(root, config, component):
    """No upload as it is just a file/dir not under version control."""
    
    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)
    
    print("No upload as it is just a file/dir not under version control. Pls do it manually if necessary.")


def freeze(root, config_now, config_ref, component, baseline):
    """Record the source url of the component."""

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    url_now = read_egg(root)
    
    if not os.path.exists(root):
        sys.stderr.write("Failed: this component doesn't exists in workspace.")
        sys.exit(2)
    elif url_now == "":
        sys.stderr.write("Failed: can not get the source information from file '" + root + ".egg-info'.")
        sys.exit(2)
    
    if config_ref.has_option(component, "url"):
        url_ref = config.get(component, "url")
        if url_ref != url_now:
            print("The URL changes from '" + url_ref + "' to '" + url_now + "'.")
        else:
            print("Still on URL '" + url_ref + "'.")
    
    config_now.set(component, "url", url_now)
