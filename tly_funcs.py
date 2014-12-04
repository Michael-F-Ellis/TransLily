"""
Functions used to edit and process user input

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

## Ignore blacklisted name complaints: pylint: disable=C0102
import re
from utils import external_edit, lilysafe_name
import rl_interface as rli
## Try to import a user-defined config file before
## falling back on the default.
try:
    # pylint: disable = F0401
    import _config as config
except ImportError:
    import config


## Time signature
_timesig = re.compile(r"""
        \\time    # \time
        \s+       # whitespace
        @         # literal '@'
        (\d+/\d+)  # num/denom e.g. 4/4, 19/16, ... etc
        """, re.VERBOSE)

def last_time_signature(slist):
    """ Return last time signature in list.
    >>> sl = [r'\\time @3/4', r'',  r'\\time  @6/8']
    >>> last_time_signature(sl)
    '6/8'
    >>> sl = ['foo', 'bar']
    >>> last_time_signature(sl)
    
    """
    for s in reversed(slist):
        match = _timesig.search(s)
        if match:
            return match.groups()[0]
    else:
        ## No time sig found!
        return None


def barcount(voicename, music):
    """
    Return the number of bars in the voice so far.
    """
    return len(music[voicename]['rhythm'])



_timesig = re.compile(r"\\time\s+@(\d+/\d+)")
_partialptn = re.compile(r'partial\s+(\S+)\s+')


def mk_voice_dict(name="Soprano I", abbr="S1",
                  rel="c''", clef='treble', has_lyrics=True ):
    """ Return a new voice dictionary """
    supported_clefs = ('treble', 'treble_8', 'bass')
    if not clef in supported_clefs:
        print "clef must be one of {}.".format(supported_clefs)
        print "setting clef to 'treble'"

    vdict =  dict(
        rwrapper = [r"\relative " + rel + " {", r"}"],  
        rhythm = [],
        pitches = [],
        name=name,
        abbr=abbr,
        labbr=lilysafe_name(abbr),
        clef = clef,
        )
    if has_lyrics == True:
        vdict['lwrapper'] = [r" \lyricmode {", r"}"]
        vdict['lyrics'] = []

    return vdict

def mk_metronome_dict():
    """ Return special voice dict for the metronome """
    vdict =  dict(
        rwrapper = [r"\drums { ", r"}"],  
        rhythm = [],
        pitches = [],
        name='Metronome',
        abbr='mm',
        labbr=lilysafe_name('mm'),
        clef = 'percussion',
        )
    return vdict                


    # pylint: disable = C0102
def get_input(music, voice, bar, insert=False):
    # ignore pylint warnings about too many branches and statements
    # pylint: disable = R0912, R0915, C0102
    """
    The overall handler for user input. Prompts for 
    pitches, rhythm, and lyrics (for voices with lyrics).
    Pre-processes the input and stores it into the music dict().
    """
    ## Construct shorter refereences
    vpitches = music[voice]['pitches']
    vrhythm = music[voice]['rhythm']
    try:
        vlyrics = music[voice]['lyrics']
    except KeyError:
        vlyrics = None

    ## Convert bar number to list index -- assumes music starts at bar 1  
    if bar == None:
        ## insert a bar at the end of the lists
        insert = True
        bar = len(vrhythm)
        #bar = ibar + 1
    if insert:
        if len(vrhythm) == 0:
            ibar = 0
            bar = 1
        else:    
            bar += 1
            ibar = bar - 1
       
        vpitches.insert(ibar, '')
        vrhythm.insert(ibar, '')
        if vlyrics is not None:
            vlyrics.insert(ibar,'')
    else:
        ## editing an existing bar
        ibar = bar - 1 
    

    #msg = "bar, ibar, nbars, insert = ({}, {}, {}, {})"
    #print msg.format(bar, ibar, len(vrhythm), insert)

    def full_measure_rest(ibarnum):
        """ 
        Fill contents of ibarnum with an appropriate full-measure rest
        """
        srhythm = music['structure']['rhythm']
        tsig = last_time_signature(srhythm[0:ibar+1])
        msg = "Created full measure rest for {} meter .".format(tsig)
        if tsig is None:
            print "No time signature found in structure!"
            return
        else:
            if voice == 'structure':  #special case
                pitches = 's'
                rhythm = "1*"+tsig
            elif voice == 'metronome': #special case
                try:
                    pitches = config.TickDict[tsig]['pitches']
                    rhythm = config.TickDict[tsig]['rhythm']
                    msg = "Inserted metronome pattern for {} meter".format(tsig)
                except KeyError:
                    print "No pattern defined for {} meter!".format(tsig)
                    pitches = 'R'
                    rhythm = "1*"+tsig

                    
            else:
                pitches = 'R'
                rhythm = "1*"+tsig

            vpitches[ibar] = pitches
            vrhythm[ibar] = rhythm
            if vlyrics is not None:
                vlyrics[ibarnum] = ''

            print msg

            return


    sentinel = ''

    prompt = "{} pitches: bar {}\n".format(voice, bar)
    while True:     
        #print prompt
        if insert:
            #pitches = '\n'.join(iter(raw_input, sentinel))
            pitches = rli.rlinput(prompt, sentinel, ctxkey='pitches')
            if pitches == sentinel or pitches.strip().endswith('m'):
                full_measure_rest(ibar)
                return


            else:
                vpitches[ibar] = pitches
                #music[voice]['pitches'].append(pitches)
        else:
            #prefill = music[voice]['pitches'][ibar]
            prefill = vpitches[ibar]
            pitches  = rli.rlinput(prompt, prefill, ctxkey='pitches')
            if pitches == sentinel or pitches.strip().endswith('m'):
                full_measure_rest(ibar)
                return
            else:
                vpitches[ibar]  = pitches
            #music[voice]['pitches'][ibar] = pitches
            
        if pitches != '':
            print "ok"
            break

    prompt = "{} rhythm: bar {}\n".format(voice, bar)
    while True:     
        #print prompt
        if insert:
            #rhythm = '\n'.join(iter(raw_input, sentinel))
            rhythm = rli.rlinput(prompt, sentinel, ctxkey='rhythm')
            vrhythm[ibar] = rhythm
            #music[voice]['rhythm'].append(rhythm)
        else:
            #prefill = music[voice]['rhythm'][ibar]
            prefill = vrhythm[ibar]
            rhythm  = rli.rlinput(prompt, prefill, ctxkey='rhythm')
            vrhythm[ibar] = rhythm
            #music[voice]['rhythm'][ibar] = rhythm
            
        if rhythm != '':
            print "ok"
            break

    #if not music[voice].has_key('lyrics'):
    if vlyrics is None:
        return

    prompt = "{} lyrics: bar {}\n".format(voice, bar)
    #print prompt
    if insert:
        #lyrics = '\n'.join(iter(raw_input, sentinel))
        lyrics = rli.rlinput(prompt, sentinel, ctxkey='lyrics')
        vlyrics[ibar] = lyrics
        #music[voice]['lyrics'].append(lyrics)
    else:
        #prefill = music[voice]['lyrics'][ibar]
        prefill = vlyrics[ibar]
        lyrics  = rli.rlinput(prompt, prefill, ctxkey='lyrics')
        vlyrics[ibar] = lyrics
        #music[voice]['lyrics'][ibar] = lyrics

    print "ok"
    return

def parse_action(ptn, cmdstring):
    #pylint: disable = W1401
    """
    Return tuple of matched groups or None
    >>> pt = re.compile(r"(\d+)\s+(\d+)$")
    >>> parse_action(pt, " 12  13 ")
    ('12', '13')
    """
    match =  ptn.match(cmdstring.strip())
    return None if not match else match.groups()

def add_voice(voice, music, jsonfp):
    """
    Add a new voice to music.
    """
    if music.has_key(voice):
        print "{} voice already exists!"
        return

    elif voice == 'metronome':
        music[voice] = mk_metronome_dict()

    else:
        _ = dict()
        props = "name abbr rel clef has_lyrics".split(' ')
        examples = ('(e.g. Bass I) ', '(e.g. B1) ', 
                    '(e.g. c) ', '(e.g. bass) ', '(y/n) ')
        for k, eg in zip(props, examples) :
            _[k] = rli.rlinput("{} {}:".format(k, eg), 
                               oneline=True, ctxkey='_top')

        if _['has_lyrics'].startswith('y'):
            _['has_lyrics'] = True
        else:
            _['has_lyrics'] = False               

        ## Allow '**' magic. pylint: disable=W0142
        music[voice] = mk_voice_dict(**_)

    jsonfp.save(music)
    print "{} added.".format(voice)


def edit_template(name, which, music):
    """ 
    Allow user to edit either the template body or the substition items.
    """
    if which == 'body':
        result = external_edit(music[name][which])
        if result is not None:
            music[name][which] = result
            return True
        else:
            return False

    elif which == 'items':
        itemd = music[name][which]
        for k, v in itemd.iteritems():
            itemd[k] = rli.rlinput("{} :".format(k), v, 
                                   oneline=True, ctxkey=name)
            
        return True

    else:
        return False

def print_barcounts(music):
    """ Print the number of bars currently in each voice """
    for k in music:
        if music[k].has_key('rhythm'):
            nbars = len(music[k]['rhythm'])
            print "  {} : {} bars".format(k, nbars)


def viewbar(music, voice, bar):
    """ Print the pitches, rhythm, and lyrics for one bar."""
    if 1 <= bar <= len(music[voice]['pitches']):
        index = bar - 1
        print "{} bar {}:".format(voice, bar)
        pitches = music[voice]['pitches']
        print pitches[index]
        rhythm = music[voice]['rhythm']
        print rhythm[index]
        try:
            lyrics = music[voice]['lyrics']
            print lyrics[index]
        except KeyError:
            pass
        print    

def cutrange(seq, i0, i1):
    """ 
    Return new sequence with elements at indices i0:i1 inclusive.
    >>> cutrange([0, 1, 2, 3, 4], 2, 3)
    [0, 1, 4]

    >>> cutrange([0, 1, 2, 3, 4], 2, 4)
    [0, 1]

    >>> cutrange([0, 1, 2, 3, 4], 0, 10)
    []
    """
    return seq[0:i0] + seq[i1+1:]

def deletebars(music, voice, firstbar, lastbar):
    """ Delete bar numbers firstbar to lastbar, inclusive. """
    ifirst = firstbar - 1
    ilast  = lastbar - 1
    vdict = music[voice]
    vdict['pitches'] = cutrange(vdict['pitches'], ifirst, ilast)
    vdict['rhythm'] = cutrange(vdict['rhythm'], ifirst, ilast)
    
    if music[voice].has_key('lyrics'):
        vdict['lyrics'] = cutrange(vdict['lyrics'], ifirst, ilast)


def insertrange(seq, values, i0):
    """ 
    Return new sequence with values inserted starting at index i0.
    >>> insertrange([0,1,2,6,7], [3,4,5], 3)
    [0, 1, 2, 3, 4, 5, 6, 7]

    >>> insertrange([3,4,5], [0,1,2], 0)
    [0, 1, 2, 3, 4, 5]
    """
    return  seq[0:i0] + values + seq[i0:]


def insert_rests(music, voice, firstbar, lastbar):
    """ Insert full measure rests from firstbar to lastbar """
    i0 = firstbar - 1
    nbars = lastbar - firstbar + 1
    vdict = music[voice]

    srhythm = music['structure']['rhythm']
    tsig = last_time_signature(srhythm[0:i0+1])
    if tsig is None:
        print "No time signature found in structure!"
        return
    else:
        barlength = "1*"+tsig
        if voice == 'structure':
            rest = 's'  #special case
        else:
            rest = 'R' 

        vdict['pitches'] = insertrange(vdict['pitches'],
                                       [rest,]*nbars, i0)        
        vdict['rhythm'] = insertrange(vdict['rhythm'],
                                      [barlength,]*nbars, i0)        
        try:
            vdict['lyrics'] = insertrange(vdict['lyrics'], ['',]*nbars, i0)
        except KeyError:
            pass # no lyrics in this voice

if __name__ == '__main__':
    from doctest import testmod
    testmod()

