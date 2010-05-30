import sys
import os
import re

from cmglib import common

def init(root, url, revision):
    """Create a component's working copy via `svn co'."""

    if not os.path.isdir(root):
        try:
            os.makedirs(root)
#        except error as err:
#            sys.stderr.write("Failed: can not to create folder " + root + ":\n" + str(err))
#            sys.exit(2)
        except:
            sys.stderr.write("Failed: can not to create folder '" + root + "':\n" + str(sys.exc_info()[0]))
            sys.exit(2)
    
    cmd = "svn co " + url + " " + root
    if revision != "":
        cmd = cmd + " -r " + revision
    (out, err, code) = common.command(cmd, root)
    if err or code != 0:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
    
    print("Success to initialize the component via 'svn co'.")


def get_status(root):
    """Show any abnormal status to deal with. Return True if anything be found out."""
    
    cmd = "svn status"
    (out, err, code) = common.command(cmd, root)
    if err or code != 0:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    if out.strip() != "":
        print("Something to deal with:")
        print(out)
        return True
    
    return False
        
def switch(root, url, revision):
    """Call `svn switch' to switch/update workspace to url -r revision"""
   
    cmd = "svn switch " + url
    if revision != "":
        cmd = cmd + " -r " + revision

    code = common.command_free(cmd, root)
    if code != 0:
        sys.stderr.write("Failed: " + cmd)
        sys.exit(2)

    print("Success to update/switch the working tree.")
        

def get_info(root, url):
    """Find out current url and revision of a working copy or remote url
    
    inputs: url is optional
    outputs: the current url and current revision
    """
    cmd = "svn info " + url
    (out, err, code) = common.command(cmd, root)
    if err or code != 0:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    current_url = current_revision = ""
    for line in out.splitlines():
        match = re.match(r"URL: (\S+)", line)
        if match != None:
            current_url = match.group(1)
        match = re.match(r"Revision: (\S+)", line)
        if match != None:
            current_revision = match.group(1)

    return (current_url, current_revision)


def add(root):    
    cmd = "svn status"
    (out, err, code) = common.command(cmd, root)
    if err or code != 0:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    new_files = []
    for line in out.splitlines():
        pattern = r"\?\s+(\S+)"
        match = re.match(pattern, line)
        if match != None:
            new_files.append(match.group(1))

    for new_file in new_files:
        cmd = "svn add " + new_file
        (out, err, code) = common.command(cmd, root)
        if err or code != 0:
            sys.stderr.write("Failed: " + cmd + "\n" + err)
            sys.exit(2)
    
def commit(root):
    """commit local modifications to remote remository"""
   
    cmd = "svn commit"
    code = common.command_free(cmd, root)
    if code != 0:
        sys.stderr.write("Failed: " + cmd)
        sys.exit(2)

def create_tag_core(root, url_from, revision_from, url_to):
    """core function of create tag"""
    
    cmd = "svn copy " + url_from + "@" + revision_from + " " + url_to
    code = common.command_free(cmd, root)
    if code != 0:
        sys.stderr.write("Failed: " + cmd)
        sys.exit(2)
        
def create_tag(root, component, config_now, url_now, revision_now, tags_url_ref, baseline):
    """create tag or record revision"""

    print("1: use revision for this component: " + revision_now)
    print("2: create a new tag for this component.")
    print("3: create a new tag with baseline name '" + baseline + "'.")
    while True:
        choice = input("? ")
        if choice == '1':
            config_now.set(component, "branch_url", url_now)
            config_now.set(component, "revision", revision_now)
            if config_now.has_option(component, "tag"):
                config_now.remove_option(component, "tag")
            return
        elif choice == '2':
            new_tag = ""
            while True:
                new_tag = input("New tag name: ")
                if new_tag.strip() != "":
                    break
            if tags_url_ref == "":
                print("Current branch's URL: " + url_now)
                while True:
                    tags_url_ref = input("Tags directory's URL: ")
                    if tags_url_ref.strip() != "":
                        break
            create_tag_core(root, url_now, revision_now, tags_url_ref + "/" + new_tag)
            config_now.set(component, "tags_url", tags_url_ref)
            config_now.set(component, "tag", new_tag)
            if config_now.has_option(component, "branch_url"):
                config_now.remove_option(component, "branch_url")
            if config_now.has_option(component, "revision"):
                config_now.remove_option(component, "revision")
            return
        elif choice == '3':
            if tags_url_ref == "":
                print("Current branch's URL: " + url_now)
                while True:
                    tags_url_ref = input("Tags directory's URL: ")
                    if tags_url_ref.strip() != "":
                        break
            create_tag_core(root, url_now, revision_now, tags_url_ref + "/" + baseline)
            config_now.set(component, "tags_url", tags_url_ref)
            config_now.set(component, "tag", baseline)
            if config_now.has_option(component, "branch_url"):
                config_now.remove_option(component, "branch_url")
            if config_now.has_option(component, "revision"):
                config_now.remove_option(component, "revision")
            return
        
        
#
# below are commands called from commands.py for each component.
#


def download(root, config, component):
    """Download/sync/update a component from SVN repository to working copy.
    
    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)
    
    url = revision = ""
    if config.has_option(component, "branch_url"):
        url = config.get(component, "branch_url")
        if config.has_option(component, "revision"):
            revision = config.get(component, "revision")
    elif config.has_option(component, "tags_url") and config.has_option(component, "tag"):
        url = config.get(component, "tags_url") + '/' + config.get(component, "tag")
    
    if url == "":
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("Neither 'branch_url' option nor 'tags_url' & 'tag' options exists in '" + component + "' section.")
        sys.exit(2)

    if not os.path.isdir(os.path.join(root, ".svn")):
        init(root, url, revision)
        return

    b_dirty = get_status(root)
    
    if b_dirty:
        if config.has_option(component, "tag"):
            tag = config.get(component, "tag")
            print("Warning: this SVN component is expected to be on tag '" + tag + \
                "', but the working copy contain modification(s).")
            print("1: handled clean up manually, pls continue\n2: quit")
            while True:
                choice = input("? ")
                if choice == '2':
                    sys.exit(2)
                elif choice == '1':
                    break
        
        if config.has_option(component, "revision"):
            revision = config.get(component, "revision")
            print("Warning: this SVN component is expected to be on revision '" + revision + \
                "' exactly, but the working copy contain modification(s).")
            print("1: handled clean up manually, pls continue\n2: quit")
            while True:
                choice = input("? ")
                if choice == '2':
                    sys.exit(2)
                elif choice == '1':
                    break
    
    switch(root, url, revision)
    
def status(root, config, component):
    """Show status of a component.
    
    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    url = revision = ""
    if config.has_option(component, "branch_url"):
        url = config.get(component, "branch_url")
        if config.has_option(component, "revision"):
            revision = config.get(component, "revision")
    elif config.has_option(component, "tags_url") and config.has_option(component, "tag"):
        url = config.get(component, "tags_url") + '/' + config.get(component, "tag")
    
    if url == "":
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("Neither 'branch_url' option nor 'tags_url' & 'tag'" + \
            " options exists in '" + component + "' section.")
        sys.exit(2)

    if not os.path.isdir(os.path.join(root, ".svn")):
        sys.stderr.write("Failed: This component does not exist yet.")
        sys.exit(2)
        
    (current_url, current_revision) = get_info(root, "")
    
    if (os.name == 'nt' and current_url.lower() != url.lower()) or \
       (os.name != 'nt' and current_url != url):
        print("Warning: It's expected to follow '" + url + "', but now it's on '" \
            + current_url + "'.")
    elif revision != "":
        if revision != current_revision:
            print("Warning: It's expected to be on revision '" + revision \
                + "', but now it's on '" + current_revision + "'.")
    else:
        (nouse, tip_revision) = get_info(root, url)
        if current_revision != tip_revision:
            print("Warning: It's expected to be on tip revision " + tip_revision + \
                " of branch '" + url + "', but now it's on revision " + current_revision + ".")

    b_dirty = get_status(root)
    
    if not b_dirty:
        return

    if config.has_option(component, "tag"):
        tag = config.get(component, "tag")
        print("Warning: this SVN component is expected to be on tag '" + tag + \
            "', but the working copy contain modification(s).")
    
    if config.has_option(component, "revision"):
        revision = config.get(component, "revision")
        print("Warning: this SVN component is expected to be on revision " + revision + \
            " exactly, but the working copy contain modification(s).")


def upload(root, config, component):
    """Upload/deliver a component's local modification in working copy to its (remote) repository.

    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """
    
    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    if not os.path.isdir(os.path.join(root, ".svn")):
        sys.stderr.write("Failed: This component does not exist yet.")
        sys.exit(2)
    
    b_dirty = get_status(root)
    
    if not b_dirty:
        return
    
    if config.has_option(component, "tag"):
        tag = config.get(component, "tag")
        print("Warning: this SVN component is expected to be on tag '" + tag + \
            "', so that local modifications will not be uploaded.")
        print("1: handled clean up manually, pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit(2)
            elif choice == '1':
                return

    if config.has_option(component, "revision"):
        revision = config.get(component, "revision")
        print("Warning: this SVN component is expected to be on given revision " + \
            revision + ", so that local modificaitons will not be uploaded.")
        print("1: handled clean up manually, pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit(2)
            elif choice == '1':
                return

    if not config.has_option(component, "branch_url"):
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("Neither 'branch_url' option nor 'tags_url' & 'tag'" + \
            " options exists in '" + component + "' section.")
        sys.exit(2)
    
    url = config.get(component, "branch_url")
    
    (current_url, current_revision) = get_info(root, "")
    
    if (os.name == 'nt' and current_url.lower() != url.lower()) or \
       (os.name != 'nt' and current_url != url):
        sys.stderr.write("Failed: It's expected to follow '" + url + "', but now it's on '" \
            + current_url + "'.")
        sys.exit(2)
            
    (nouse, tip_revision) = get_info(root, url)
    if current_revision != tip_revision:
        print("Tip revision of branch '" + url + "' is " + tip_revision \
            + ", but now it's on revision " + current_revision + ".")
        switch(root, url, "")

    if common.cfgs['addnewfile']:
        add(root)

    commit(root)

    
def freeze(root, config_now, config_ref, component, baseline):
    """Find out tag (create tag if neccessary) or revision for a component."""

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)
    
    if not os.path.isdir(os.path.join(root, ".svn")):
        sys.stderr.write("Failed: This component does not exist yet.")
        sys.exit(2)

    b_dirty = get_status(root)
    
    if b_dirty:
        print("Warning: this SVN component's working copy contain modification(s).")
        print("1: handled clean up manually, pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit(2)
            elif choice == '1':
                break

    if not os.path.isdir(os.path.join(root, ".svn")):
        sys.stderr.write("Failed: This component does not exist yet.")
        sys.exit(2)

    (url_now, revision_now) = get_info(root, "")
                
    if config_ref.has_option(component, "branch_url") and config_ref.has_option(component, "revision"):
        url_ref = config_ref.get(component, "branch_url")
        revision_ref = config_ref.get(component, "revision")
        if url_ref != url_now:
            print("The branch URL changes from '" + url_ref + "' to '" + url_now + "'.")
        if revision_ref != revision_now:
            print("The revision changes from '" + revision_ref + "' to '" + revision_now + "'.")
        else:
            print("Still on previous revision '" + revision_ref + "'.")

        config_now.set(component, "branch_url", url_now)
        config_now.set(component, "revision", revision_now)
        if config_now.has_option(component, "tag"):
            config_now.remove_option(component, "tag")

    elif config_ref.has_option(component, "tags_url") and config_ref.has_option(component, "tag"):
        tags_url_ref = config_ref.get(component, "tags_url")
        tag_ref = config_ref.get(component, "tag")
        if url_now == tags_url_ref + '/' + tag_ref:
            print("Still on tag " + tag_ref + ".")
            config_now.set(component, "tags_url", tags_url_ref)
            config_now.set(component, "tag", tag_ref)
            if config_now.has_option(component, "branch_url"):
                config_now.remove_option(component, "branch_url")
            if config_now.has_option(component, "revision"):
                config_now.remove_option(component, "revision")
        elif url_now.find(tags_url_ref) == 0:
            tag_now = url_now[len(tags_url_ref)+1:]
            print("Tag changes from " + tag_ref + " to " + tag_now)
            config_now.set(component, "tags_url", tags_url_ref)
            config_now.set(component, "tag", tag_now)
            if config_now.has_option(component, "branch_url"):
                config_now.remove_option(component, "branch_url")
            if config_now.has_option(component, "revision"):
                config_now.remove_option(component, "revision")
        else:
            create_tag(root, component, config_now, url_now, revision_now, tags_url_ref, baseline)

    elif config_ref.has_option(component, "tags_url"):
        tags_url_ref = config_ref.get(component, "tags_url")
        create_tag(root, component, config_now, url_now, revision_now, tags_url_ref, baseline)
    else:
        create_tag(root, component, config_now, url_now, revision_now, "", baseline)
