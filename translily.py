#!/usr/bin/env python
"""
Top level script for translily program.

Copyright 2014 Ellis & Grant, Inc. 

This file is part of TransLily.

    TransLily is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    TransLily is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TransLily.  If not, see <http://www.gnu.org/licenses/>.   
"""

import os, sys, json
from json_io import JSONFolder
from usage_stats import user_action_tracker
try:
    ## pylint: disable=F0401
    from _config import tmusic
except ImportError:
    from config import tmusic

import tly_funcs as tf
import re

import cmd
import cmdhelp

## Process input
## Ignore toplevel name conventions: pylint: disable=C0103

## Ignore blacklisted name complaints: pylint: disable=C0102
usage_msg = """
translily.py -- A musical transcription assistant for LilyPond

Usage: translily.py path/to/folder
If folder does not exist it will be created.

"""

if len(sys.argv) != 2:
    print usage_msg
    sys.exit()

filepath = sys.argv[1]
if filepath.startswith(('-h', '--h')):
    print usage_msg
    sys.exit()

lilyprog = "lilypond"

## extract directory and basename without extension
filepath = os.path.abspath(filepath)
dirname, base = os.path.split(filepath)
sys.path.append(dirname)
jsonf = JSONFolder(dirname, base)


## Try to load existing work from the json folder.
## If no work is found, initialize the music dictionary
## from the template in the config file. Let the user
## know what's happening in either case.
try:
    music = jsonf.load()
except ValueError as e:
    print e
    print "Starting from scratch ..."
    music = tmusic
    tf.edit_template('_top', 'items', music)
    jsonf.save(music)

else:
    print "Found prior work:"
    tf.print_barcounts(music)


## Start the usage tracker that accumulates time spent
## in various actions and prints stats at the end of the session

usage_tracker = user_action_tracker()

## Ignore 'too many public methods' warning.
## pylint: disable=R0904
class TransLily(cmd.Cmd):
    """ Command handler """
    ## Suppress pylint 'could be a function' warnings
    ## pylint: disable=R0201 
    ## Unused 'line' arg is ok here. pylint: disable=W0613

    doc_header = "Music entry commands (type help <cmd>)"
    misc_header = "Topical help (type help <topic>)"
    ruler = None

    def __init__(self, music, dirname, base):
        cmd.Cmd.__init__(self)
        #self.last_voice = None

        self.aptn = re.compile(r'^(\w+)$')

        #self.eptn2 = re.compile(r'^(\d+)\s+(\d+)$') 
        self.eptn3 = re.compile(r'^(\w+)\s+(\d+)\s+(\d+)$')

        self.pptn = re.compile(r'^(\w+)\s+(\d+)\s+(\d+)\s+(\w+)\s+(\d+)$')
        self.tptn = re.compile(r'^(_top|_bottom)\s+(body|items)$')
        self.vptn = re.compile(r'^(\w+)\s+(\d+)$') 
        self.in_action = False
        self.music = music
        self.dirname = dirname
        self.base = base
        print dirname, base

    def _voice_in_music(self, voice):
        """ Returns True if voice exists in self.music, False otherwise. """
        if self.music.has_key(voice):
            return True
        else:
            print "No voice named {}!".format(voice)
            return False


    def _validate_voice(self, line):
        """ 
        Validator for commands that take "voice' as the only arg. 
        Returns voicename if validation succeeds, None
        otherwise.
        """
        args = tf.parse_action(self.aptn, line)
        if args is not None:
            voice = args[0]
        else:
            msg = "Can't interpret '{}' as 'voice'"
            print msg.format(line)
            return None

        if not self._voice_in_music(voice):
            ret = None

        else:
            ret = voice

        return ret    
    
    def _validate_voice_bar(self, line):
        """ 
        Validator for commands that take "voice bar' as args. 
        Returns (voice, bar) if validation succeeds, None
        otherwise.
        """
        args = tf.parse_action(self.vptn, line)
        if args is not None:
            voice, bar = args
            bar = int(bar)
        else:
            msg = "Can't interpret '{}' as 'voice bar'"
            print msg.format(line)
            return None

        if not self._voice_in_music(voice):
            ret = None

        elif bar < 1:
            print "bar must be >= 1"
            ret = None
        else:
            ret = voice, bar

        return ret    

    def _validate_voice_first_last(self, line):
        """ 
        Validator for commands that take "voice firstbar lastbar' as args. 
        Returns (voice, firstbar, lastbar) if validation succeeds, None
        otherwise.
        """
        args = tf.parse_action(self.eptn3, line)
        if args is not None:
            voice, firstbar, lastbar = args
            firstbar = int(firstbar)
            lastbar = int(lastbar)
        else:
            msg = "Can't interpret '{}' as 'voice firsbar lastbar'"
            print msg.format(line)
            return None

        if not self._voice_in_music(voice):
            ret = None

        elif firstbar < 1:
            print "firstbar must be >= 1"
            ret = None

        elif lastbar < firstbar:
            msg = "lastbar ({}) is less than firstbar ({})"
            print msg.format(lastbar, firstbar)
            ret = None
        else:
            ret = voice, firstbar, lastbar

        return ret    

    #def _voicefix(self, voice, actionverb):
    #    """ DEPRECATED Support omitting voice name from commands """
    #    if voice in (None, ''):
    #        if self.last_voice is not None:
    #            return self.last_voice
    #        else:
    #            print "Please specify a voice to {}!".format(actionverb)
    #            return None
    #    else:
    #        return voice

    def help_cmds(self):
        """ Show the command summary """
        print cmdhelp.HELP['commands']

    def help_introduction(self):
        """ Introduction to TransLily """
        print cmdhelp.HELP['introduction']

    def help_usage(self):
        """Usage information for getting started."""
        print cmdhelp.HELP['usage']

    def help_autosave(self):
        """ Help for autosave """
        print cmdhelp.HELP['autosave']

    def help_vital(self):
        """ Vital information topic """
        print cmdhelp.HELP['vital']

    def help_a(self):
        """ Help for the 'a' cmd."""
        print cmdhelp.HELP['append']

    def do_a(self, line):
        """ 'a voice' Append to existing voice or create new one. """
        voice = self._validate_voice(line)
        if voice is None: 
            return 
       
        tf.get_input(self.music, voice, None, insert=True)
        jsonf.save(self.music)


    def help_b(self):
        """ Help barcounts """
        print cmdhelp.HELP['barcounts']

    def do_b(self, line):
        """b Show bar counts for each voice. """
        tf.print_barcounts(self.music)


    def help_c(self):
        """ Compile command help """
        print cmdhelp.HELP['compile']

    def do_c(self, line):
        """ 'c voice' to compile """
        voice = self._validate_voice(line)
        if voice is None:
            return
       
        if voice != 'structure':
            vlen =  len(self.music[voice]['rhythm'])
            slen =  len(self.music['structure']['rhythm'])
            if vlen > slen:
                msg = "Can't compile. 'structure' is shorter than '{}'"
                print msg.format(voice)
                return

        ## open an output file with .ly extension in write mode
        ## in the project folder
        voice_order = ['structure', voice]
        lilyname = os.path.join(self.dirname, self.base, self.base + '_' + voice + '.ly')
        lilyf = file(lilyname, 'w+')
        tf.mklily(self.music, lilyf, voice_order)
        lilyf.flush()
        lilyf.close()
        outspec = "-o {}".format(os.path.splitext(lilyname)[0])
        print outspec
        os.system('{} {} {}'.format(lilyprog, outspec, lilyname ))
        return

    def help_d(self):
        """ Help for 'd' command """
        print cmdhelp.HELP['delete']


    def do_d(self, line):
        """ 'd voice firstbar lastbar' delete range of bars """
        try:
            voice, firstbar, lastbar = self._validate_voice_first_last(line)
        except TypeError:
            return

        tf.deletebars(self.music, voice, firstbar, lastbar)
        print "deleted {} {} thru {}".format(voice, firstbar, lastbar)
        if [] == self.music[voice]['rhythm']:
            self.music.pop(voice)
            print "deleted empty voice {}".format(voice)

        jsonf.save(self.music)

        
    def help_e(self):
        """ Edit command help """
        print cmdhelp.HELP['edit']

    def do_e(self, line):
        """ 'e voice firstbar lastbar' edit a range of bars """
        try:
            voice, firstbar, lastbar = self._validate_voice_first_last(line)
        except TypeError:
            return

        if firstbar > tf.barcount(voice, self.music):
            print "There's no bar {} to edit in {}.".format(firstbar, voice)
            return

        elif lastbar  > tf.barcount(voice, self.music):
            print "There's no bar {} to edit in {}.".format(lastbar, voice)
            return

        else:
            pass

        for bar in range(firstbar, lastbar + 1):
            tf.get_input(self.music, voice, bar)

            ## Save the input
            jsonf.save(self.music)

    def help_i(self):
        """ Help for 'i' command """
        print cmdhelp.HELP['insert']


    def do_i(self, line):
        """ 'i voice firstbar lastbar' rests in range of bars """
        try:
            voice, firstbar, lastbar = self._validate_voice_first_last(line)
        except TypeError:
            return

        tf.insert_rests(self.music, voice, firstbar, lastbar)
        jsonf.save(self.music)

    def help_n(self):
        """ Help for new voice command """
        print cmdhelp.HELP['new']
        
    def do_n(self, line):
        """ Add a new voice """
        args = tf.parse_action(self.aptn, line)
        if args is None:
            msg = "Can't interpret '{}' as 'voice'"
            print msg.format(line)
            return

        voice = args[0]
        if self.music.has_key(voice):
            print "Voice {} already exists!".format(voice)
            return

        print "Adding voice {}".format(voice)
        tf.add_voice(voice, self.music, jsonf)
        tf.get_input(self.music, voice, None)

        jsonf.save(self.music)

    def help_p(self):
        """ Paste command help """
        print cmdhelp.HELP['paste']


    def do_p(self, line):
        """ 'p fromvoice firstbar lastbar tovoice startbar' paste """

        args = tf.parse_action(self.pptn, line)
        if args is not None:
            sfv, sb, sn, stv, tb = args

        if not self.music.has_key(sfv):
            print "No voice named {}!".format(sfv)
            return

        if not self.music.has_key(stv):
            print "No voice named {}!".format(stv)
            return

        try:
            firstbar = int(sb)
        except ValueError:
            print "{} is not a valid bar number".format(sb)
            return

        try:
            tobar = int(tb)
        except ValueError:
            print "{} is not a valid bar number".format(sb)
            return

        try:
            lastbar = int(sn)
        except ValueError:
            print "{} is not a valid bar number".format(sb)
            return

        if firstbar < 1:
            print "First bar must be greater than 0"
            return 

        elif firstbar > tf.barcount(sfv, self.music):
            print "There's no bar {} to paste from!".format(firstbar)
            return
        elif lastbar > tf.barcount(sfv, self.music):
            print "There's no bar {} to paste from!".format(lastbar)
            return
        elif tobar > 1 + tf.barcount(stv, self.music):
            print "There's no bar {} to paste to!".format(tobar)
            return
        else:
            pass


        for __ in range(firstbar, lastbar + 1):
            for k in ('pitches', 'rhythm', 'lyrics'):
                if self.music[sfv].has_key(k) and self.music[stv].has_key(k):
                    i0 = int(firstbar) - 1
                    i1 = lastbar
                    j0 = tobar - 1
                    j1 = j0 + i1 - i0
                    #self.music[stv][k].extend(self.music[sfv][k][i0:i1])
                    self.music[stv][k][j0:j1] = self.music[sfv][k][i0:i1]

        jsonf.save(self.music)

    def help_v(self):
        """ View help """
        print cmdhelp.HELP['view']

    def do_v(self, line):
        """ View pitches, rhythm, and lyrics for selected bar. """
        
        try:
            voice, firstbar, lastbar = self._validate_voice_first_last(line)
        except TypeError:
            return

        for b in range(firstbar, lastbar + 1):    
            tf.viewbar(self.music, voice, b)
        
        return
        
    def do_t(self, line):  ## TEMPLATE EDITOR
        """ 't _top|_bottom body|items' template editor """
        args = tf.parse_action(self.tptn, line)
        if args is not None:
            name, which = args
        else:
            print "Can't interpret {} as template command".format(line)
            return

        if name not in ('_top', '_bottom'):
            print "The only editable template names are '_top' and '_bottom'"
            return

        _ = self.music[name].keys()
        if which not in _:
            print "{} has no {} to edit".format(name, which)
            return

        if tf.edit_template(name, which, self.music):
            jsonf.save(self.music)

    def help_u(self):
        """ Help for undo """
        print cmdhelp.HELP['undo']

    def do_u(self, line):
        """ 'u' undo """
        undone = jsonf.undo()
        if undone is not None:
            self.music = undone


    def do_r(self, line):
        """ 'r' redo i.e. undo last undo. """
        redone = jsonf.redo()
        if redone is not None:
            self.music = redone

    def precmd(self, line):
        """Tell usage tracker we've started a command. """
        if len(line) > 0 and not line.startswith('EOF'):
            usage_tracker.send(line[0])
            self.in_action = True

        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        """ Tell usage_tracker command is finished. """
        if self.in_action == True:
            usage_tracker.next()
            self.in_action = False

        return cmd.Cmd.postcmd(self, stop, line)

    def do_q(self, line):
        """ Quit """
        return True

    def do_EOF(self, line):
    #    """ Quit the program via Ctrl-D. """
        return True

TransLily(music, dirname, base).cmdloop()







