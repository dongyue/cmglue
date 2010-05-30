"""common functions and global variables of CMG."""

import os
import sys
import subprocess
import re
import configparser  #for Python 3.x
#import ConfigParser  #for Python 2.x

VERSION = "0.9.1" #CMG version

STREAMFILE = "_stream" #The file in root of container which stores the stream configuration.
BASELINEFILE = "_baseline" # The file in .git in container which stores the baseline configuration to write to tag

cfgs = {'verbose': False, \
    'gitrebase': True, \
    'online': True, \
    'addnewfile': True}
"""Some global CMG configuations that alternate CMG's behavior.

* verbose: True if you want CMG show verbose information.
* gitrebase: True if you want 'git rebase' instead of 'git merge' when you 
update a local branch from a remote branch. It affects both the container
and all components under Git.
* online: False if you can not / do not want link to remote repository/place
to download from / upload to. Accordingly, Git will not 'git fetch', and SVN
can not 'svn update', 'svn commit' etc.

All these values may changed when initialize. See get_cmg_cfg(root) in git.py
"""


def command(cmd, dir):
    """ To run a command line. `cmd' is the command line. `dir' is the working
    directory to run the command line. Return output msg, err/warn msg, as well
    as the exit code.
    """
   
    if cfgs['verbose']:
        print("\n[call cmd] " + cmd)
        print("[in dir] " + dir)

    pipe = subprocess.Popen(cmd, shell=True, cwd=dir, universal_newlines=True,\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    (stdoutdata, stderrdata) = pipe.communicate()
    
    if cfgs['verbose']:
        print("[output msg]\n" + stdoutdata)
        print("[err/warn msg] " + stderrdata)
        print("[exit code] " + str(pipe.returncode))
    
    return (stdoutdata, stderrdata, pipe.returncode)


def command_free(cmd, dir):
    """ To run a command line interactively, and without monitor the result.
    `cmd' is the command line. `dir' is the working directory to run the command line.
    """

    if cfgs['verbose']:
        print("\n[call cmd] " + cmd)
        print("[in dir] " + dir)

    pipe = subprocess.Popen(cmd, shell=True, cwd=dir, universal_newlines=True)
    pipe.communicate()
    
    return pipe.returncode


DEFAULTSECT = "DEFAULT" #the defult section name. See codes in base class.
class MyCfgParser(configparser.SafeConfigParser):  #for Python 3.x
#class MyCfgParser(ConfigParser.SafeConfigParser):  #for Python 2.x
    """Some wrap on standard lib configperser.SafeConfigParser."""

    class StrFp:
        """A internal class to make string as if a file handle to read."""
    
        def __init__(self, string):
            self.lines = string.splitlines(True)
            self.pointer = -1
        def readline(self):
            self.pointer = self.pointer + 1
            if self.pointer < len(self.lines):
                return self.lines[self.pointer]
            else:
                return ""

    def readstr(self, string, title):
        """To read config from a multiline string"""
    
        fp = self.StrFp(string)
        self._read(fp, title)

    def _read(self, fp, fpname):
        """Different to base class's: allow whitespaces as prefix of each valid line.
        
        This is to accept Git style cfg format. While the side effect is, you can
        not have a value longer than one line.
        """
        #only one line is different from base class. See highlighted comment below.
    
        cursect = None                            # None, or a dictionary
        optname = None
        lineno = 0
        e = None                                  # None, or an exception
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
            #########################
            # Below is the only line different from base class, to accept git style cfg format.
            line = line.lstrip()
            #########################
            # continuation line?
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname] = "%s\n%s" % (cursect[optname], value)
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == DEFAULTSECT:
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise configparser.MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if vi in ('=', ':') and ';' in optval:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = optval.find(';')
                            if pos != -1 and optval[pos-1].isspace():
                                optval = optval[:pos]
                        optval = optval.strip()
                        # allow empty values
                        if optval == '""':
                            optval = ''
                        optname = self.optionxform(optname.rstrip())
                        cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

def get_root():
    """Get the root path of the container.
    
    If a super-directory of current directory has a special sub-directory named
    `_stream', then the super-directory is the answer.
    """

    root = os.path.abspath('.')
    while True:
        if os.path.isfile(os.path.join(root, STREAMFILE)):
            break
        else:
            newroot = os.path.dirname(root)
            if newroot == root:
                sys.stderr.write("Failed to find the " + STREAMFILE +\
                    " file which indicate the container.")
                sys.exit(2)
            root = newroot
    return root

def get_stream_cfg(root, local, remote):
    """Get current stream's configuration.
    
    `root' is the container's root dir. `local' stands for the local branch.
    `remote' stands for the remote branch.
    """
    
    config = MyCfgParser()

    std_cfg = os.path.join(root, STREAMFILE)
    try:
        config.readfp(open(std_cfg))
#    except configparser.ParsingError as err:
#        sys.stderr.write("Failed to read stream config from " + std_cfg \
#            + ":\n" + str(err))
#        exit(2)
    except:
        sys.stderr.write("Failed to read stream config from " + std_cfg \
            + ":\n" + str(sys.exc_info()[0]))
        exit(2)
        
    if local != "":
        cfg_local = os.path.join(root, STREAMFILE + "_" + re.sub(r"\\|/", "_", local))
        try:
            config.read(cfg_local)
#        except configparser.ParsingError as err:
#            sys.stderr.write("Failed to read stream config from " + cfg_local \
#                + ":\n" + str(err))
#            exit(2)
        except:
            sys.stderr.write("Failed to read stream config from " + cfg_local \
                + ":\n" + str(sys.exc_info()[0]))
            exit(2)

    if remote != "":
        cfg_remote = os.path.join(root, STREAMFILE + "_" + re.sub(r"\\|/", "_", remote))
        try:
            config.read(cfg_remote)
#        except configparser.ParsingError as err:
#            sys.stderr.write("Failed to read stream config from " + cfg_remote \
#                + ":\n" + str(err))
#            exit(2)
        except:
            sys.stderr.write("Failed to read stream config from " + cfg_remote \
                + ":\n" + str(sys.exc_info()[0]))
            exit(2)
        
    return config

def get_baseline_cfg(root, tag_name, tag_annotation):
    """Get a baseline's configuration.
    
    `root' is the container's root dir. the configuration information is stored
    in `tag_annotation' string.
    """

    config = MyCfgParser()
    try:
        config.readstr(tag_annotation, tag_name)
    except configparser.ParsingError as err:
        sys.stderr.write("Failed to read baseline config from tag " + tag_name + \
            "' annotation:\n" + str(err))
        print("Is this tag an tag with annotation that in CMG special format?")
        exit(2)
    return config
