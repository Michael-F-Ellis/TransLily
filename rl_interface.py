"""
Interface for gathering musical input within TransLily.

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
import os
import readline
from tempfile import NamedTemporaryFile
from utils import external_edit, uniqify

import intermodular_globals as G


def rlinput(prompt, prefill='', oneline=False, ctxkey=''):
    """
    Get user input with readline editing support.
    """

    sentinel = ''
    if prefill is None:
        prefill = ''
    
    def only_once(text):
        """ generator for startup hook """
        readline.insert_text(text)
        yield
        while True:
            yield

    savedhist = NamedTemporaryFile()
    readline.write_history_file(savedhist.name)
    ctxhistname = ".tl" + ctxkey + "history"
    ctxhistfile = os.path.join(G.ProjectFolder, ctxhistname)
    try:
        readline.clear_history()
    except AttributeError:
        print "This readline doesn't support clear_history()"
        raise
    
    savedcompleter = readline.get_completer()
    try:
        ulines = uniqify(ctxhistfile)
        readline.read_history_file(ctxhistfile)
        readline.set_completer(HistoryCompleter(ulines).complete)
    except IOError:
        pass

    readline.parse_and_bind('tab: complete')
    saveddelims = readline.get_completer_delims()
    readline.set_completer_delims('') ## No delims. Complete entire lines.
    readline.set_completion_display_matches_hook(match_display_hook)
    gen = only_once(prefill)
    readline.set_startup_hook(gen.next)
    try:
        if oneline:
            edited = raw_input(prompt)
        else:
            print prompt
            edited = "\n".join(iter(raw_input, sentinel))

        if edited.endswith(r'%%'):
            ## Invoke external editor
            edited = external_edit(edited[0:-2])
        return edited
    finally:
        ## Restore readline state 
        readline.write_history_file(ctxhistfile)
        readline.clear_history()
        readline.read_history_file(savedhist.name)
        savedhist.close()
        readline.set_completer(savedcompleter)
        readline.set_completer_delims(saveddelims)
        readline.set_startup_hook()    

def match_display_hook(substitution, matches, longest_match_length):
    ## Unused args are ok. pylint: disable=W0613
    """ Cleaner display for line completion """
    print '\n--- possible matches ---'
    for match in matches:
        print match
    #print self.prompt.rstrip(),
    print '------------------------'
    print readline.get_line_buffer(),
    readline.redisplay()

class HistoryCompleter(object):
## Suppress complaint about 'too few public methods'
## pylint: disable=R0903
    """ 
    Adapted and simplified from http://pymotw.com/2/readline/ 
    """
    def __init__(self, history_items):
        self.matches = []
        self.history_items = history_items
        return

    def complete(self, text, state):
        """ Completion method for readline """
        def dbg(msg):
            """ localized debug() """
            G.debug("complete :" + msg)

        response = None
        dbg("Text {}, state {}".format(text, state))
        if state == 0:
            if len(text) > 0:
                self.matches = sorted(h 
                                      for h in self.history_items 
                                      if h and h.startswith(text))
            else:
                self.matches = []
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        dbg('response {}'.format(response))    
        return response



