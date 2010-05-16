import sys
import os
import re

from cmglib import common

def is_local_br(root, local):
    """Check if it is an existing local branch."""
    
    if local[:8] == "remotes/":
        return False
    
    if local[:7] == "origin/":
        return False

    cmd = "git branch"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    for line in out.splitlines():
        match = re.match(r"\*?\s+" + local + r"$", line)
        if match != None:
            return True
    
    return False

def is_local_br_to_create(root, local):
    """Check if it is local branch that does not exist but has a corresponding remote-tracking branch."""
    
    if local[:8] == "remotes/":
        return False
    
    if local[:7] == "origin/":
        return False

    cmd = "git branch -r"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    for line in out.splitlines():
        match = re.match(r"\s+" + "origin/" + local + r"$", line)
        if match != None:
            return True

    return False

def is_remote_br(root, remote):
    """Check if it is an existing remote-tracking branch."""
    
    if remote[:8] == "remotes/":
        remote = remote[8:]
    
    if remote[:7] != "origin/":
        return False

    cmd = "git branch -r"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    for line in out.splitlines():
        match = re.match(r"\s+" + remote + r"$", line)
        if match != None:
            return True

    return False

def is_tag(root, tag):
    """Check if it is an existing tag."""

    cmd = "git tag -l " + tag
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
    
    if out.strip() == tag:
        return True
    
    return False

def is_on_tag(root, tag):
    """Check if it is currently on a tag."""

    cmd = "git tag -l " + tag + " --contains HEAD"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    if out.strip() == tag:
        return True
    
    return False

def get_cmg_cfg(root):
    """To get CMG configurations from Git config file(s).
    
    `root' is the container's root. It means the CMG configs should be stored in
    the container's git cfg file, and / or user-specific git config file,
    and / or system-wide git config file.

    An example of config format in git config file:

        [cmg]
            verbose = false
            gitrebase = true
            online = false
    All these configurations have default values in common.py.
    """
    
    for key in list(common.cfgs.keys()):
        cmd = "git config cmg." + key
        (out, err, code) = common.command(cmd, root)
        if err:
            sys.stderr.write("Failed: " + cmd + "\n" + err)
            sys.exit(2)
        if out.strip().lower() == "true":
            common.cfgs[key] = True
        if out.strip().lower() == "false":
            common.cfgs[key] = False

def get_current_br_pair(root):
    """Find out local-remote branch pair of current checked out branch."""

    cmd = "git branch -v -v"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    for line in out.splitlines():
        match = re.match(r"\*\s+(\S+)\s+\S+\s+\[(\S+?)(\]|:)\s+", line)
        if match != None:
            return (match.group(1), match.group(2))
    
    return ("", "")
       
def get_remote_br_via_local(root, local):
    """Get remote-tracking branch using local branch name as a hint."""

    cmd = "git branch -v -v"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    for line in out.splitlines():
        match = re.match(r"\*?\s+" + local + r"\s+\S+\s+\[(\S+?)(\]|:)\s+", line)
        if match != None:
            return match.group(1)
    
    return ""
            
def get_local_br_via_remote(root, remote):
    """Get (select if several) an local branch using remote-tracking branch name as a hint."""
    
    if remote[:8] == "remotes/":
        remote = remote[8:]
    
    if remote[:7] != "origin/":
        return False
    
    cmd = "git branch -v -v"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    locals = []
    for line in out.splitlines():
        pattern = r"(\*?)\s+(\S+)\s+\S+\s+\[" + remote + r"(\]|:)\s+"
        match = re.match(pattern, line)
        if match != None:
            if match.group(1) == "*": #the current branch, the favorite
                return match.group(2)
            locals.append(match.group(2))

    if len(locals) == 0:
        return ""
    elif len(locals) == 1:
        return locals[0]
    else:
        print("Found multiple branch pairs you may mean:")
        i = 1
        for local in locals:
            print(str(i) + " local branch: " + local + " remote-tracking branch: " + remote)
            i = i + 1
        print(str(i) + " quit")
        while True:
            choice = input("? ")
            if choice == str(len(locals) + 1):
                exit()
            for j in len(locals):
                if str(j) == choice:
                    return locals[j-1]

def get_tag_annotation(root, tag):
    """Get content of tag annotation, which indicate the baseline configuation.""" 

    cmd = "git tag -n10000 -l " + tag
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
    return re.sub(r"\S+\s+", "", out, 1)
        
    
def get_status(root):
    """Show any abnormal status to deal with"""
    
    cmd = "git status"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    # "nothing to commit (working directory clean)"
    match1 = re.search(r"nothing to commit \(working directory clean\)", out)
    # "nothing to commit (create/copy files and use "git add" to track)"
    match2 = re.search(r"nothing to commit \(create/copy files", out)
    # "# Your branch is ahead of 'origin/st1' by 3 commits."
    match3 = re.search(r"is ahead of", out)
    # "# Your branch is behind 'origin/st1' by 1 commit, and can be fast-forwarded."
    match4 = re.search(r"is behind", out)
    # "# Your branch and 'origin/st1' have diverged."   
    match5 = re.search(r"have diverged", out)

    if (match1 != None or match2 != None) and \
        (match3 == None and match4 == None and match5 == None):
        return

    print("Something to deal with:")
    print(out)

def get_remote(root):
    """Get parameters of `origin' in Git config"""

    url = pushurl = ""
    
    cmd = "git config remote.origin.url"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
    url = out.strip()
        
    cmd = "git config remote.origin.pushurl"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)    
    pushurl = out.strip()
    
    if pushurl == "":
        pushurl = url
    
    return (url, pushurl)

def create_new_tag(root, tag):
    cmd = "git tag " + tag
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    print("Created new tag '" + tag + "'.")

    
def get_current_tag(root, baseline):
    """Get (create if have to) a tag for HEAD.
    
    `baseline' is the tag name of container.
    """
    
    cmd = "git tag -l --contains HEAD"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    tags = []
    for line in out.splitlines():
        tags.append(line.strip())
        
    print("1: create a new tag for this component.")
    print("2: create a new tag with baseline name '" + baseline + "'.")

    i = 3
    if len(tags) != 0:
        for tag in tags:
            print(str(i) + ": select existing tag '" + tag + "'.")
            i = i + 1

    while True:
        choice = input("? ")
        if choice == '1':
            new_tag = ""
            while True:
                new_tag = input("New tag name: ")
                if new_tag.strip() != "":
                    break
            create_new_tag(root, new_tag)
            return new_tag
        elif choice == '2':
            create_new_tag(root, baseline)
            return baseline
        for j in len(tags):
            if str(j+2) == choice:
                print("Selected existing tag '" + tags[j-1] + "'.")
                return tags[j-1]

        
def remind_multi_local(root, remote):
    """Check if the remote-tracking branch has multiple local branches. Remind if so."""
    
    if remote[:8] == "remotes/":
        remote = remote[8:]
    
    if remote[:7] != "origin/":
        assert False, "It's not an remote-tracking branch."
    
    cmd = "git branch -v -v"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    lines = []
    for line in out.splitlines():
        pattern = r"(\*?)\s+(\S+)\s+\S+\s+\[" + remote + r"(\]|:)\s+"
        match = re.match(pattern, line)
        if match != None:
            lines.append(line)

    if len(lines) > 1:
        print("Reminder: remote-tracking branch '" + remote + "' has multiple local branches:")
        i = 1
        for line in lines:
            print(str(i) + ": " + line)
            i = i + 1
    
    
def init(root, url):
    """Create a component's local repository via `git clone'."""

    if not os.path.isdir(root):
        try:
            os.makedirs(root)
#        except error as err:
#            sys.stderr.write("Failed: can not to create folder " + root + ":\n" + str(err))
#            sys.exit(2)
        except:
            sys.stderr.write("Failed: can not to create folder " + root + ":\n" + str(sys.exc_info()[0]))
            sys.exit(2)
    
    cmd = "git clone " + url + " " + root
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
    
    print("Success to initialize the component via clone.")

def set_remote(root, url, pushurl):
    """Set parameters of `origin' in Git config"""

    cmd = "git config remote.origin.url " + url
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    fetch = "+refs/heads/*:refs/remotes/origin/*"
    cmd = "git config remote.origin.fetch " + fetch
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    cmd = "git config remote.origin.pushurl " + pushurl
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
        
def fetch(root):
    """Call `git fetch origin'."""

    cmd = "git fetch origin"
    (out, err, code) = common.command(cmd, root)
    if err and err[:4] != 'From':
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    #print("Success to fetch from origin.")

def create_default_local_br(root, branch):
    """Create local branch which has the same (base) name of remote-tracking branch"""
    
    local = branch
    if branch[:8] == "remotes/":
        local = branch[15:]
    elif branch[:7] == "origin/":
        local = branch[7:]

    cmd = "git branch " + local + ' origin/' + local
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    print("Success to create local branch " + local \
        + " to follow remote-tracking branch origin/" + local)
    
    return local

def cleanup_working_tree(root):
    """Check and then clean up the working tree of the container / a component."""

    cmd = "git status"
    (out, err, code) = common.command(cmd, root)
    if err:
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)

    match = re.search(r"nothing to commit \(working directory clean\)", out)
    if match != None:
        return
    
    print("You should cleanup working tree "\
        + "(via git reset/add/commit etc.) "\
        + "before git checkout/merge/rebase/push:\n" + out\
        + "(Hint: you may want to add them to .gitignore?)")

    match = re.search(r"# Not currently on any branch.", out)
    if match == None:
        print("1: add and commit all\n2: clean and reset all\n" \
            + "3: handled clean up manually, pls continue\n4: quit")
        while True:
            choice = input("? ")
            if choice == '4':
                sys.exit(2)
            elif choice == '3':
                break
            elif choice == '2':
                cmd = "git clean -f ."
                (out, err, code) = common.command(cmd, root)
                if err:
                    sys.stderr.write("Failed: " + cmd + "\n" + err)
                    continue
                cmd = "git reset --hard HEAD"
                (out, err, code) = common.command(cmd, root)
                if err:
                    sys.stderr.write("Failed: " + cmd + "\n" + err)
                    continue
                break
            elif choice == '1':
                cmd = "git add ."
                (out, err, code) = common.command(cmd, root)
                if err:
                    sys.stderr.write("Failed: " + cmd + "\n" + err)
                    continue
                cmd = "git commit"
                common.command_free(cmd, root)
                break
    else:
        print("1: clean and reset all\n2: handled clean up manually, "\
            + "pls continue\n3: quit")
        while True:
            choice = input("? ")
            if choice == '3':
                sys.exit(2)
            elif choice == '2':
                break
            elif choice == '1':
                cmd = "git clean -d -f ."
                (out, err, code) = common.command(cmd, root)
                if err:
                    sys.stderr.write("Failed: " + cmd + "\n" + err)
                    continue
                cmd = "git reset --hard HEAD"
                (out, err, code) = common.command(cmd, root)
                if err:
                    sys.stderr.write("Failed: " + cmd + "\n" + err)
                    continue
                break
    
def checkout(root, point, type):
    """Checkout a branch or tag of the container / a component.
    
    `point' is the branch or tag's name. The value of `type' should be 'branch' or 'tag'.
    """

    cmd = "git checkout " + point
    (out, err, code) = common.command(cmd, root)
    if err and err[:8] != "Switched" and err[:7] != "Already" \
        and err[:5] != "Note:" and err[:4] != "HEAD" and err[:8] != "Previous":
        sys.stderr.write("Failed: " + cmd + "\n" + err)
        sys.exit(2)
    else:
        print("Success to checkout " + type + " '" + point + "'.")

def rebase(root, remote):
    """Run `git rebase' to rebase current local branch based on the tip of remote-tracking branch"""

    print("Start rebase from remote-tracking branch " + remote +"...")
    cmd = "git rebase " + remote
    (out, err, code) = common.command(cmd, root)

    match1 = re.search(r"fatal: ", err)
    match2 = re.search(r"When you have resolved this problem run ", out)
    match3 = re.search(r"Current branch \S+ is up to date.", out)
    if match1 != None or match2 != None:
        print("Failed to do rebase fullly automatically: " + cmd + "\n" + out + err)
        print("1: fixed the merge conflict and *finished all* for " \
            + "this rebase, pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit()
            elif choice == '1':
                break
    elif match3 != None:
        print("Nothing to do: Already up-to-date.")    
    else:
        print("Success to rebase fully automatically.")

def merge(root, remote):
    """Run `git merge' to merge from remote-tracking branch to current local branch."""

    print("Start merge from remote-tracking branch '" + remote + "'...")
    cmd = "git merge " + remote
    (out, err, code) = common.command(cmd, root)
    
    match1 = re.search(r"fatal: ", err)
    match2 = re.search(r"Automatic merge failed", out)
    match3 = re.search(r"Already up-to-date", out)
    if match1 != None or match2 != None:
        print("Failed to do merge fully automatically: " + cmd + "\n" + out + err)
        print("1: fixed the merge conflict and *committed*, " \
            + "pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit(2)
            elif choice == '1':
                break
    elif match3 != None:
        print("Nothing to do: Already up-to-date.")    
    else:
        print("Success to merge fully automatically.")
    

def push(root, remote):

    if remote[:8] == "remotes/":
        remote = remote[8:]
    
    if remote[:7] != "origin/":
        assert False, "it's not a remote-tracking branch."
        
    print("Start push to branch '" + remote[7:] + "' in remote repository...")

    cmd = "git push origin HEAD:" + remote[7:]
    (out, err, code) = common.command(cmd, root)

    match1 = re.search(r"fatal: ", err)
    match2 = re.search(r"error: ", err)
    match3 = re.search(r"Everything up-to-date", err)
    if match1 != None or match2 != None:
        print("Failed to push: " + cmd + "\n" + out + err)
        print("1: handled manually, pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit(2)
            elif choice == '1':
                break
    elif match3 != None:
        print("Nothing to do: Already up-to-date in remote repository.")
    else:
        print("Success to push.")
        
def push_tag(root, tag):

    if tag[:5] == "refs/":
        tag = tag[5:]
    if tag[:5] == "tags/":
        tag = tag[5:]
    
    print("Start push tag '" + tag + "' to remote repository...")

    cmd = "git push origin tag " + tag
    (out, err, code) = common.command(cmd, root)
    
    match1 = re.search(r"fatal: ", err)
    match2 = re.search(r"error: ", err)
    match3 = re.search(r"Everything up-to-date", err)
    if match1 != None or match2 != None:
        print("Failed to push tag: " + cmd + "\n" + out + err)
        print("1: handled manually, pls continue\n2: quit")
        while True:
            choice = input("? ")
            if choice == '2':
                sys.exit(2)
            elif choice == '1':
                break
    elif match3 != None:
        print("Nothing to do: Already exists in remote repository.")
    else:
        print("Success to push tag.")

def create_tag(root, tag, bl_cfg_fl_name):

    cmd = "git tag -F " + bl_cfg_fl_name + " " + tag
    (out, err, code) = common.command(cmd, root)
    
    match = re.search(r"fatal: ", err)
    if match != None:
        sys.stderr.write("Failed to create tag: " + cmd + "\n" + out + err)
        sys.exit(2)

    print("Success to create tag '" + tag + "'.")
        
def download(root, config, component):
    """Download/sync/update a component from Git remote repository to Git local repository and working tree.
    
    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    if not config.has_option(component, "url"):
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'url' option in '" + component + "' section.")
        sys.exit(2)
    url = config.get(component, "url")

    if not os.path.isdir(os.path.join(root, ".git")):
        init(root, url)
    
    pushurl = url
    if config.has_option(component, "pushurl"):
        pushurl = config.get(component, "pushurl")
    set_remote(root, url, pushurl) #remote settings in local repository
   
    if common.cfgs['online']:
        fetch(root)

    local = remote = tag = ""
    if config.has_option(component, "branch"):
        point = config.get(component, "branch")
        if is_local_br(root, point):
            local = point
            remote = get_remote_br_via_local(root, local)
            if remote == "":
                sys.stderr.write("Failed: can not find local branch "\
                    + local + "'s remote-tracking branch\n")
                sys.exit(2)
        elif is_local_br_to_create(root, point):
            local = create_default_local_br(root, point)
            remote = "origin/" + local
        elif is_remote_br(root, point):
            remote = point
            local = get_local_br_via_remote(root, remote)
            if local == "":
                local = create_default_local_br(root, point)
        else:
            sys.stderr.write("Failed: '" + point + "' is not a local branch or "\
                + "remote-tracking branch.")
            sys.exit(2)
    elif config.has_option(component, "tag"):
        point = config.get(component, "tag")
        if is_tag(root, point):
            tag = point
        else:
            sys.stderr.write("Failed: '" + point + "' is not a tag.")
            sys.exit(2)
    else:
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'branch' or 'tag' option in '" + component + "' section.")
        sys.exit(2)

    if local != "":
        cleanup_working_tree(root)
        checkout(root, local, "branch")
        if common.cfgs['gitrebase']:
            rebase(root, remote)
        else:
            merge(root, remote)
    else:
        cleanup_working_tree(root)
        checkout(root, tag, "tag")

    
def status(root, config, component):
    """Show status of a component.
    
    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    if not config.has_option(component, "url"):
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'url' option in '" + component + "' section.")
        sys.exit(2)
    url = config.get(component, "url")

    if not os.path.isdir(os.path.join(root, ".git")):
        print("Warning: this component does not exist yet.")
        return
    
    pushurl = url
    if config.has_option(component, "pushurl"):
        pushurl = config.get(component, "pushurl")
    set_remote(root, url, pushurl) #remote settings in local repository
   
    if common.cfgs['online']:
        fetch(root)

    local = remote = tag = ""
    if config.has_option(component, "branch"):
        point = config.get(component, "branch")
        if is_local_br(root, point):
            local = point
            remote = get_remote_br_via_local(root, local)
            if remote == "":
                print("Warning: can not find local branch "\
                    + local + "'s remote-tracking branch\n")
        elif is_local_br_to_create(root, point):
            local = create_default_local_br(root, point)
            remote = "origin/" + local
        elif is_remote_br(root, point):
            remote = point
            local = get_local_br_via_remote(root, remote)
            if local == "":
                local = create_default_local_br(root, point)
        else:
            print("Warning: '" + point + "' is not a local branch or "\
                + "remote-tracking branch.")
    elif config.has_option(component, "tag"):
        point = config.get(component, "tag")
        if is_tag(root, point):
            tag = point
        else:
            print("Warning: '" + point + "' is not a tag.")
    else:
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'branch' or 'tag' option in '" + component + "' section.")
        sys.exit(2)

        
    if local != "" and remote != "": #to check if current branch is the given branch
        (local_now, remote_now) = get_current_br_pair(root)
        if local_now == "":
            print("Warning: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's not on a local branch " \
                + "that follow a remote-tracking branch.")
        elif local_now != local:
            print("Warning: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's on local branch '" + local_now \
                + "' that follow remote-tracking branch '" + remote_now + "'.")
        remind_multi_local(root, remote)
        
    elif tag != "": # to check if HEAD on the given tag or not
        if not is_on_tag(root, tag):
            print("Warning: it's expected to be on tag '" + tag \
                + "', but currently it's not.")
        
    get_status(root)

def upload(root, config, component):
    """Upload/deliver a component's local modifications (in working tree and local repository) to its remote repository.

    `root' is the root of container. `config' stores the stream/baseline config.
    `component' is the name of the component.
    """

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    if not config.has_option(component, "url"):
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'url' option in '" + component + "' section.")
        sys.exit(2)
    url = config.get(component, "url")

    if not os.path.isdir(os.path.join(root, ".git")):
        sys.stderr.write("Failed: This component does not exist yet.")
        sys.exit(2)
    
    pushurl = url
    if config.has_option(component, "pushurl"):
        pushurl = config.get(component, "pushurl")
    set_remote(root, url, pushurl) #remote settings in local repository
   
    local = remote = tag = ""
    if config.has_option(component, "branch"):
        point = config.get(component, "branch")
        if is_local_br(root, point):
            local = point
            remote = get_remote_br_via_local(root, local)
            if remote == "":
                sys.stderr.write("Failed: can not find local branch "\
                    + local + "'s remote-tracking branch\n")
                sys.exit(2)
        elif is_local_br_to_create(root, point):
            local = create_default_local_br(root, point)
            remote = "origin/" + local
        elif is_remote_br(root, point):
            remote = point
            local = get_local_br_via_remote(root, remote)
            if local == "":
                local = create_default_local_br(root, point)
        else:
            sys.stderr.write("Failed: '" + point + "' is not a local branch or "\
                + "remote-tracking branch.")
            sys.exit(2)
    elif config.has_option(component, "tag"):
        point = config.get(component, "tag")
        if is_tag(root, point):
            tag = point
        else:
            sys.stderr.write("Failed: '" + point + "' is not a tag.")
            sys.exit(2)
    else:
        sys.stderr.write("Failed: bad format of stream/baseline config: ")
        sys.stderr.write("No 'branch' or 'tag' option in '" + component + "' section.")
        sys.exit(2)

    if local != "": #to check if current branch is the given branch
        (local_now, remote_now) = get_current_br_pair(root)
        if local_now == "":
            sys.stderr.write("Failed: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's not on a local branch " +\
                "that follow a remote-tracking branch.")
            sys.exit(2)
        elif local_now != local:
            sys.stderr.write("Failed: it's expected to be on local branch '"\
                + local + "' to follow remote-tracking branch '" + remote +"', "\
                + "but currently it's on local branch '" + local_now +\
                "' that follow remote-tracking branch '" + remote_now + "'.")
            sys.exit(2)

            
    fetch(root)
    if tag == "":
        cleanup_working_tree(root)
        if common.cfgs['gitrebase']:
            rebase(root, remote)
        else:
            merge(root, remote)
        push(root, remote)
    else:
        push_tag(root, tag)
    
def freeze(root, config_now, config_ref, component, baseline):
    """Find out tag (create tag if neccessary) for a component."""

    root = os.path.join(root, component) #now it's the root of this component.
    print("---- " + root)

    (url, pushurl) = get_remote(root)
    config_now.set(component, "url", url)
    config_now.set(component, "pushurl", pushurl)

    tag_now = ""
    if config_ref.has_option(component, "tag"):
        tag_ref = config_ref.get(component, "tag")
        if is_on_tag(root, tag_ref):
            print("Still on previous tag '" + tag_ref + "'.")
            tag_now = tag_ref
        else:
            print("No longer on previous tag '" + tag_ref + "'.")
            tag_now = get_current_tag(root, baseline)
    else:
        tag_now = get_current_tag(root, baseline)

    config_now.set(component, "tag", tag_now)
    if config_now.has_option(component, "branch"):
        config_now.remove_option(component, "branch")
