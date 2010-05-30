import os
import sys

from cmglib import common
from cmglib import git
from cmglib import svn
from cmglib import file

def download_usage():
    print("""
Download/sync/update from remote repositories/places to local.

Usage: cmg download [-h|--help] [<tag>|<remote-tracking branch>|<local branch>]

    (no paramater)      download current stream
    -h, --help          help
    <tag>               tag name that indicate the baseline
    <remote-tracking branch>
                        remote-tracking branch name (such as origin/master)
                        that indicate the remote-local branch pair for stream
    <local branch>      local branch name (such as master) that indicate
                        the remote-local branch pair for stream
""")

def download(args):
    """Download/sync/update from remote repositories/places to local repositories / working trees."""

    point = ""
    if len(args) == 0:
        pass
    elif len(args) > 1:
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        download_usage()
        sys.exit(2)
    elif args[0] in ('-h', "--help"):
        download_usage()
        sys.exit()
    elif args[0][0] == '-':
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        download_usage()
        sys.exit(2)
    else:
        point = args[0]

    root = common.get_root()
    git.get_cmg_cfg(root)
    print("---- " + root)
    
    if common.cfgs['online']:
        git.fetch(root)
    else:
        print("Warning: CMG is running under offline mode. No interaction with remote.")
    
    local = remote = tag = ""
    if point == "":
        (local, remote) = git.get_current_br_pair(root)
        if local == "":
            sys.stderr.write("Failed: it's not on a local branch "\
                + "that follow a remote-tracking branch")
            sys.exit(2)
    else:
        if git.is_local_br(root, point):
            local = point
            remote = git.get_remote_br_via_local(root, local)
            if remote == "":
                sys.stderr.write("Failed: can not find local branch "\
                    + local + "'s remote-tracking branch\n")
                sys.exit(2)
        elif git.is_local_br_to_create(root, point):
            local = git.create_default_local_br(root, point)
            remote = "origin/" + local
        elif git.is_remote_br(root, point):
            remote = point
            local = git.get_local_br_via_remote(root, remote)
            if local == "":
                local = git.create_default_local_br(root, point)
        elif git.is_tag(root, point):
            tag = point
        else:
            sys.stderr.write("Failed: '" + point + "' is not a local branch, or "\
                + "remote-tracking branch, or tag.")
            sys.exit(2)

    if tag == "":
        git.cleanup_working_tree(root)
        git.checkout(root, local, "branch")
        if common.cfgs['gitrebase']:
            git.rebase(root, remote)
        else:
            git.merge(root, remote)
    else:
        git.cleanup_working_tree(root)
        git.checkout(root, tag, "tag")

    config = None
    if tag == "":
        config = common.get_stream_cfg(root, local, remote)
    else:
        tag_annotation = git.get_tag_annotation(root, tag)
        config = common.get_baseline_cfg(root, tag, tag_annotation)
        
    for component in config.sections():
        if not config.has_option(component, 'type'):
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("No 'type' option in '" + component + "' section.")
            sys.exit(2)
        
        type = config.get(component, 'type')
        if type.lower() == 'git':
            git.download(root, config, component)
        elif type.lower() == 'svn' or type.lower() == 'subversion':
            svn.download(root, config, component)
        elif type.lower() == 'fl' or type.lower() == 'file':
            file.download(root, config, component, True)
        elif type.lower() == 'dir' or type.lower() == 'directory':
            file.download(root, config, component, False)
        else:
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("type '" + type + "' is not supported.")
            sys.exit(2)

            
def status_usage():
    print("""
Show status/diff information of container and each component

Usage: cmg status [-h|--help] [<tag>|<remote-tracking branch>|<local branch>]

    (no paramater)      show status of current stream
    -h, --help          help
    <tag>               see if current workspace match the baseline
    <remote-tracking branch>
                        remote-tracking branch name (such as origin/master)
                        that indicate the remote-local branch pair for stream
    <local branch>      local branch name (such as master) that indicate
                        the remote-local branch pair for stream
""")

def status(args):
    """Show status/diff information of container and each component"""

    point = ""
    if len(args) == 0:
        pass
    elif len(args) > 1:
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        status_usage()
        sys.exit(2)
    elif args[0] in ('-h', "--help"):
        status_usage()
        sys.exit()
    elif args[0][0] == '-':
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        status_usage()
        sys.exit(2)
    else:
        point = args[0]
        
    root = common.get_root()
    git.get_cmg_cfg(root)
    print("---- " + root)
    
    if common.cfgs['online']:
        git.fetch(root)
    else:
        print("Warning: CMG is running under offline mode. No interaction with remote.")
    
    local = remote = tag = ""
    if point == "":
        (local, remote) = git.get_current_br_pair(root)
        if local == "":
            print("Warning: it's expected to be on a local branch "\
                + "that follow a remote-tracking branch, but currently not.")
    else:
        if git.is_local_br(root, point):
            local = point
            remote = git.get_remote_br_via_local(root, local)
            if remote == "":
                print("Warning: can not find local branch "\
                    + local + "'s remote-tracking branch.\n")
        elif git.is_local_br_to_create(root, point):
            local = git.create_default_local_br(root, point)
            remote = "origin/" + local
        elif git.is_remote_br(root, point):
            remote = point
            local = git.get_local_br_via_remote(root, remote)
            if local == "":
                local = git.create_default_local_br(root, point)
        elif git.is_tag(root, point):
            tag = point
        else:
            print("Warning: '" + point + "' is not a local branch, or "\
                + "remote-tracking branch, or tag.")

    if local != "" and remote != "" and point != "": #to check if current branch is the given branch
        (local_now, remote_now) = git.get_current_br_pair(root)
        if local_now == "":
            print("Warning: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's not on a local branch " \
                + "that follow a remote-tracking branch.")
        elif local_now != local:
            print("Warning: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's on local branch '" + local_now\
                + "' that follow remote-tracking branch '" + remote_now + "'.")
        
    elif tag != "": # to check if HEAD is on the given tag
        if not git.is_on_tag(root, tag):
            print("Warning: it's expected to be on tag '" + tag\
                + "', but currently it's not.")

    if local != "" and remote != "": #to check if remote-tracking branch has multiple local branch
        git.remind_multi_local(root, remote)
        
    git.get_status(root)
            
    config = None
    if tag == "":
        config = common.get_stream_cfg(root, local, remote)
    else:
        tag_annotation = git.get_tag_annotation(root, tag)
        config = common.get_baseline_cfg(root, tag, tag_annotation)
        
    for component in config.sections():
        if not config.has_option(component, 'type'):
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("No 'type' option in '" + component + "' section.")
            sys.exit(2)
        
        type = config.get(component, 'type')
        if type.lower() == 'git':
            git.status(root, config, component)
        elif type.lower() == 'svn' or type.lower() == 'subversion':
            svn.status(root, config, component)
        elif type.lower() == 'fl' or type.lower() == 'file':
            file.status(root, config, component)
        elif type.lower() == 'dir' or type.lower() == 'directory':
            file.status(root, config, component)
        else:
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("type '" + type + "' is not supported.")
            sys.exit(2)
            
def upload_usage():
    print("""
Upload/deliver local modifications to remote repositories.

Usage: cmg upload [-h|--help] [<tag>|<remote-tracking branch>|<local branch>]

    (no paramater)      upload current stream
    -h, --help          help
    <tag>               tag name that indicate the baseline to upload
    <remote-tracking branch>
                        must be the current remote-tracking branch name 
                        (such as origin/master)
    <local branch>      must be the current local branch name (such as master)
""")

def upload(args):
    """Upload/deliver local modifications to remote repositories."""

    point = ""
    if len(args) == 0:
        pass
    elif len(args) > 1:
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        upload_usage()
        sys.exit(2)
    elif args[0] in ('-h', "--help"):
        upload_usage()
        sys.exit()
    elif args[0][0] == '-':
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        upload_usage()
        sys.exit(2)
    else:
        point = args[0]

    root = common.get_root()
    git.get_cmg_cfg(root)
    print("---- " + root)
    
    if common.cfgs['online']:
        git.fetch(root)
    else:
        sys.stderr.write("Failed: CMG is running under offline mode. No way to upload.")
        upload_usage()
        sys.exit(2)

    local = remote = tag = ""
    if point == "":
        (local, remote) = git.get_current_br_pair(root)
        if local == "":
            sys.stderr.write("Failed: it's not on a local branch "\
                + "that follow a remote-tracking branch")
            sys.exit(2)
    else:
        if git.is_local_br(root, point):
            local = point
            remote = git.get_remote_br_via_local(root, local)
            if remote == "":
                sys.stderr.write("Failed: can not find local branch "\
                    + local + "'s remote-tracking branch\n")
                sys.exit(2)
        elif git.is_local_br_to_create(root, point):
            local = git.create_default_local_br(root, point)
            remote = "origin/" + local
        elif git.is_remote_br(root, point):
            remote = point
            local = git.get_local_br_via_remote(root, remote)
            if local == "":
                local = git.create_default_local_br(root, point)
        elif git.is_tag(root, point):
            tag = point
        else:
            sys.stderr.write("Failed: '" + point + "' is not a local branch, or "\
                + "remote-tracking branch, or tag.")
            sys.exit(2)

    if local != "" and point != "": #to check if current branch is the given branch
        (local_now, remote_now) = git.get_current_br_pair(root)
        if local_now == "":
            sys.strerr.write("Failed: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's not on a local branch " +\
                "that follow a remote-tracking branch.")
            sys.exit(2)
        elif local_now != local:
            sys.strerr.write("Failed: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's on local branch '" + local_now +\
                "' that follow remote-tracking branch '" + remote_now + "'.")
            sys.exit(2)
            
    
    git.cleanup_working_tree(root)
    
    config = None
    if tag == "":
        config = common.get_stream_cfg(root, local, remote)
    else:
        tag_annotation = git.get_tag_annotation(root, tag)
        config = common.get_baseline_cfg(root, tag, tag_annotation)
        
    for component in config.sections():
        if not config.has_option(component, 'type'):
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("No 'type' option in '" + component + "' section.")
            sys.exit(2)
        
        type = config.get(component, 'type')
        if type.lower() == 'git':
            git.upload(root, config, component)
        elif type.lower() == 'svn' or type.lower() == 'subversion':
            svn.upload(root, config, component)
        elif type.lower() == 'fl' or type.lower() == 'file':
            file.upload(root, config, component)
        elif type.lower() == 'dir' or type.lower() == 'directory':
            file.upload(root, config, component)
        else:
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("type '" + type + "' is not supported.")
            sys.exit(2)

    print("---- (back to) " + root)
    if tag == "":
        if common.cfgs['gitrebase']:
            git.rebase(root, remote)
        else:
            git.merge(root, remote)
        git.push(root, remote)
    else:
        git.push_tag(root, tag)


def freeze_usage():
    print("""
Create baseline.

Usage: cmg freeze -h|--help|<tag> [<old_tag>]

    -h, --help          help
    <tag>               tag name that indicate the baseline to create
    <old_tag>           existing tag to be the base to edit
""")

def freeze(args):
    """Create baseline."""

    tag = old_tag = ""
    if len(args) == 0 or len(args) > 2:
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        freeze_usage()
        sys.exit(2)
    elif args[0] in ('-h', "--help"):
        freeze_usage()
        sys.exit()
    elif args[0][0] == '-':
        sys.stderr.write("Failed: wrong format of command line paramaters.")
        freeze_usage()
        sys.exit(2)
    else:
        tag = args[0]
    if len(args) == 2:
        old_tag = args[1]

    root = common.get_root()
    git.get_cmg_cfg(root)
    print("---- " + root)

    if common.cfgs['online']:
        git.fetch(root)
    else:
        print("Warning: CMG is running under offline mode. No interaction with remote.")

    git.cleanup_working_tree(root)
    
    if git.is_tag(root, tag):
        sys.stderr.write("Failed: '" + tag + "' is an existing tag.")
        sys.exit(2)

    (local_now, remote_now) = git.get_current_br_pair(root)
    config_now = common.get_stream_cfg(root, local_now, remote_now)
    
    config_ref = config_now
    if old_tag:
        if not git.is_tag(root, old_tag):
            sys.stderr.write("Failed: '" + old_tag + "' is not an existing tag.")
            sys.exit(2)
        tag_annotation = git.get_tag_annotation(root, old_tag)
        config_ref = common.get_baseline_cfg(root, old_tag, tag_annotation)
        
    for component in config_now.sections():
        if not config_now.has_option(component, 'type'):
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("No 'type' option in '" + component + "' section.")
            sys.exit(2)
        
        type = config_now.get(component, 'type')
        if type.lower() == 'git':
            git.freeze(root, config_now, config_ref, component, tag)
        elif type.lower() == 'svn' or type.lower() == 'subversion':
            svn.freeze(root, config_now, config_ref, component, tag)
        elif type.lower() == 'fl' or type.lower() == 'file':
            file.freeze(root, config_now, config_ref, component, tag)
        elif type.lower() == 'dir' or type.lower() == 'directory':
            file.freeze(root, config_now, config_ref, component, tag)
        else:
            sys.stderr.write("Failed: bad format of stream/baseline config: ")
            sys.stderr.write("type '" + type + "' is not supported.")
            sys.exit(2)

    print("---- (back to) " + root)

    bl_cfg_fl_name = os.path.join(root, ".git", common.BASELINEFILE)
    try:
        bl_cfg_fl = open(bl_cfg_fl_name, 'w') 
#    except error as err:
#        sys.stderr.write("Failed: can not open file " + bl_cfg_fl_name + ":\n" + str(err))
#        sys.exit(2)
    except:
        sys.stderr.write("Failed: can not open file " + bl_cfg_fl_name + ":\n" + str(sys.exc_info()[0]))
        sys.exit(2)
        
    try:
        config_now.write(bl_cfg_fl)
#    except error as err:
#        sys.stderr.write("Failed: can not write baseline config to file " + bl_cfg_fl_name + ":\n" + str(err))
#        sys.exit(2)
    except:
        sys.stderr.write("Failed: can not write baseline config to file " + bl_cfg_fl_name + ":\n" + str(sys.exc_info()[0]))
        sys.exit(2)

    bl_cfg_fl.close()
    
    print("Now the baseline content was written to file '" + bl_cfg_fl_name + "'. Pls review/revise it.")
    print("1: reviewed. pls continue\n2: quit")
    while True:
        choice = input("? ")
        if choice == '2':
            sys.exit()
        elif choice == '1':
            break

    git.create_tag(root, tag, bl_cfg_fl_name)
