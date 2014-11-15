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

import re
from utils import external_edit
import rl_interface as rli
## Don't complain about importing string module
## pylint: disable=W0402
## Ignore blacklisted name complaints: pylint: disable=C0102
from string import Template
_isnotedur = re.compile(
        r""" (^1(\D|$))|
        (^2(\D|$))|
        (^4(\D|$))|
        (^8(\D|$))|
        (^16(\D|$))|
        (^32(\D|$))|
        (^64(\D|$))|
        (^128(\D|$))
        """, re.VERBOSE)

## Matches single pitches or chords in <>'s
_pitch_or_chord = re.compile(r"<[^<>]+>|\S+")

## Pattern for full measure rest
_fmr = re.compile(r"""
        R         # literal 'R'
        \d+       # followed by at least 1 digit
        [0-9.*/]* # followed by 0 or more digits, dots, '*'s, or '/'s
        """, re.VERBOSE)

## Pattern for full measure spacer rest
_fms = re.compile(r"""
        s         # literal 's'
        \d+       # followed by at least 1 digit
        [0-9.*/]* # followed by 0 or more digits, dots, '*'s, or '/'s
        """, re.VERBOSE)

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

def isduration(tok):
    """
    Note: To simplify parsing, adopt convention that any token beginning with a
    number that could be mistaken for a duration be prefixed with with '@', e.g
    tempos, repeat counts, partials.  tuplet fractions, ... These are many
    times less common that note durations so the extra typing will be minimal.

    >>> isduration('1')
    True
    >>> isduration(r'64\\rest')
    True
    >>> isduration('4*3')
    True
    >>> isduration('@4=60')
    False
    >>> isduration('1*3/4')
    True
    """
    if _isnotedur.match(tok):
        return True
    else:
        return False

def linelist(text):
    """
    >>> text = "   foo\\nbar      spam"
    >>> linelist(text)
    [['foo'], ['bar', 'spam']]

    """
    return [line.split() for line in text.split('\n')]

def barcount(voicename, music):
    """
    Return the number of bars in the voice so far.
    """
    return len(music[voicename]['rhythm'])

def merge(pitches, other):
    """
    Examples:

    Notes and chords case:
    >>> merge("a bes <c d ees>", r"\\tempo @4=60 1 ~ " "\\n( 1 ) 1")
    ['\\\\tempo 4=60 a1 ~', '( bes1 ) <c d ees>1']

    Out of pitches case:
    >>> merge("a bes", r"\\tempo @4=60 1 ~ " "\\n( 1 ) 1")
    ['\\\\tempo 4=60 a1 ~', '( bes1 )']
    """
    ## Split pitches without preserving lines
    plist = _pitch_or_chord.findall(pitches)

    ## split other preserving lines
    olist = linelist(other)
    
    #print plist
    #print olist

    merged = []
    pindex = 0
    out_of_pitches = False
    for line in olist:
        if out_of_pitches:
            ## Found fewer pitches than durations.
            ## Stop processing so the .ly output will
            ## still be valid.
            break

        mlist = []
        for tok in line:
            if isduration(tok):
                #print tok, plist[pindex]
                try:
                    mlist.append(plist[pindex] + tok)
                except IndexError:
                    out_of_pitches = True
                    break
                pindex += 1
            else:
                mlist.append(tok.lstrip('@'))
            
        merged.append(" ".join(mlist))
    return merged        

def structure_merge(srhythm, vrhythm, stripit=False):
    """
    Prepend the non-durational items from srhythm with vrhythm. 

    >>> sr = r'\\repeat volta @2 { 1 }'
    >>> vr = r'4 4 4 4'
    >>> structure_merge(sr, vr, stripit=True)
    '\\\\repeat volta 2 { 4 4 4 4 }'
    >>> sr = r'\\repeat volta @2 { 1*3/4'
    >>> vr = r'4 4 4 4'
    >>> structure_merge(sr, vr, stripit=True)
    '\\\\repeat volta 2 { 4 4 4 4'
    
    This function is used to create voices with repeat indications
    that can be unfolded for MIDI output.
    """
    fstrip = lambda x : x if not stripit else x.lstrip('@')
    merged = []
    toks = srhythm.split(' ')
    front = True
    i = 0
    for i, tok in enumerate(toks):
        if not isduration(tok):
            if front:
                merged.append(fstrip(tok))
            else:
                break
        else:
            front = False
    else:
        i += 1
    for tok in vrhythm.split(' '):
        merged.append(fstrip(tok))

    for tok in toks[i:]:
        merged.append(fstrip(tok))

    return ' '.join(merged)   
            

def mk_mmr(measure, count, ptn=_fmr):
    """
    >>> mk_mmr('\\time 4/4 R1', 3)
    '\\time 4/4 R1*3'
    """
    index = ptn.search(measure).span()[1]
    return measure[0:index] + '*{}'.format(count) + measure[index:]
    
def classify(bar, ptn, exact=None):
    """
    >>> classify("a1", _fmr)
    ('unmatched', None)

    >>> classify(" R1*4/4 ", _fmr)
    ('begin', 'R1*4/4')

    >>> classify(" R1*4/4 ", _fmr, exact='R1*4/4' )
    ('append', 'R1*4/4')

    >>> classify(" R1*4/4 \\tempo 4=90", _fmr)
    ('append_end', None)

    >>> classify(" R1*3/4 ", _fmr, exact='R1*4/4' )
    ('end_begin', 'R1*3/4')

    >>> classify(" R1*3/4 \\time 4/4 ", _fmr, exact='R1*4/4' )
    ('end', None)

    """
    bar = bar.strip()
    found = ptn.findall(bar)
    if len(found) != 1:
        return 'unmatched', None

    else:
        matched = found[0]
        start = bar.find(matched)
        end = start + len(matched)

    if exact is None:
        if end == len(bar):
            return 'begin', matched
        else:
            if start == 0:
                return 'append_end', None
            else:
                return 'end', None

    elif matched == exact:
        if start == 0:
            if end == len(bar):
                return 'append', exact
            else:
                return 'append_end', None

        else:
            return 'end', None

    else:
        if end == len(bar):
            return 'end_begin', matched
        else:
            return 'end', None


def gather_fm_rests(mergelist, ptn=_fmr):
    """
    Combine all possible sequences of full measure rests in mergelists into
    equivalent multi-measure rests.

    Sequences must begin with a measure that contains exactly one matching rest
    pattern as its last element.

    Sequences may be extended by measures with exactly one matching rest
    pattern as a first element.

    Sequencess are ended three possible ways:
        1. A non-matching measure is found.
        2. A matching measure with extra elements after the match
        3. No more measures in the mergelist.

    The element that begins the sequence sets the pattern for the remainder of the sequence. This prevents combining across
    time signature changes, e.g ['R1', 'R2.']
    >>> gather_fm_rests([r'\\time 4/4 R1', r'R1', r'R1'])
    ['\\\\time 4/4 R1*3']

    >>> gather_fm_rests([r'\\time 4/4 R1', r'R1', r'R1', r'R1*3/4'])
    ['\\\\time 4/4 R1*3', 'R1*3/4*1']

    >>> gather_fm_rests([r'\\time 4/4 R1', r'R1', r'R1', r'R1*3/4', r'a1'])
    ['\\\\time 4/4 R1*3', 'R1*3/4*1', 'a1']

    >>> gather_fm_rests([r'\\time 4/4 r1', r'R1', r'R1'])
    ['\\\\time 4/4 r1', 'R1*2']

    >>> gather_fm_rests([r'\\time 4/4 r1', r's1', r's1'], ptn=_fms)
    ['\\\\time 4/4 r1', 's1*2']

    """


    result = []
    #gathering = False
    count = 0
    startbar = None
    exact = None
    #mergelist.append(r'')
    for s in mergelist:
        #print "{}".format(s)
        # match = ptn.search(s)
        #print match
        action, exact = classify(s, ptn, exact=exact)
        #print action, exact, s
        if action == 'begin':
            startbar = s
            count = 1
        elif action == 'append':
            count += 1
        elif action == 'append_end':
            count += 1
            result.append(mk_mmr(startbar, count, ptn=ptn))
            count = 0
            startbar = None
        elif action in ('end', 'unmatched'):
            if startbar is not None:
                result.append(mk_mmr(startbar, count, ptn=ptn))
                #print result
                count = 0
                startbar = None
                if action == 'unmatched':
                    result.append(s)
            else:
                result.append(s)
        elif action == 'end_begin':
            result.append(mk_mmr(startbar, count, ptn=ptn))
            startbar = s
            count = 1

    else:
        ## handle sequences the extend to end mergelist
        if startbar is not None:
            result.append(mk_mmr(startbar, count, ptn=ptn))


    return result                


_timesig = re.compile(r"\\time\s+@(\d+/\d+)")
_partialptn = re.compile(r'partial\s+(\S+)\s+')

def drum_mode_cleanup(drumnotes):
    """ 
    Remove key signatures from drumnotes to prevent LilyPond errors.
    >>> test = r"foo \key d \dorian wbl4\pp"
    >>> drum_mode_cleanup(test)
    'foo  wbl4\\\\pp'
    """
    ## key signatures look like '\key c \major'.
    kptn = re.compile(r'\\\key\s+\w+\s+\\\w+') 
    return re.sub(kptn, '',  drumnotes)


def mkticks(metronome, rhythm, meter=None):
    """
    Scan rhythm string for time sig. Update
    meter if one is found.  Append ticks to
    metronome list.
    """
    match = _timesig.search(rhythm)
    if match:
        meter = match.groups()[0]
    if meter is None:
        raise ValueError("No meter is available for metronome!")

    ## if meter is one we know about, append the corresponding tick
    ## pattern to the metronome list.  Otherwise, insert a full
    ## measure rest.

    ticks = {
        ## Allow long lines    
        #pylint: disable=C0301
        '2/2' : r' wbh4\fff wbl\ppp wbl\ff wbl\ppp ',
        '2/4' : r' wbh4\fff wbl\ppp ',
        '3/2' : r' wbh4\fff r wbl\ppp r wbl r ',
        '3/4' : r' wbh4\fff wbl\ppp wbl ',
        '3/8' : r' wbh8\fff wbl wbl ',
        '4/4' : r' wbh4\fff wbl\ppp wbl wbl ',
        '5/2' : r' wbh2\fff wbl\ppp wbl\ff wbl\ppp wbl ',
        '5/4' : r' wbh4\fff wbl\ppp wbl wbl wbl ',
        '5/8' : r' wbh8\fff wbl wbl  wbl\fff wbl  ',
        '6/4' : r' wbh4\fff wbl\ppp wbl wbl\fff wbl\ppp wbl ',
        '6/8' : r' wbh8\fff r r   wbl\fff r r  ',
        '8/8' : r' wbh8\fff r r   wbl\fff r r  wbl\fff r  ',
        '9/2' : r' wbh2\fff wbl\ppp wbl  wbl\fff wbl\ppp wbl  wbl\fff wbl\ppp wbl ',
        '9/8' : r' wbh8\fff r r   wbl\fff r r  wbl\fff r r  ',
        '7/4' : r' wbh4\fff wbl\ppp wbl wbl wbl\fff wbl\ppp wbl ',
        '10/4' : r' wbh4\fff wbl\ppp wbl\fff wbl\ppp wbl wbh4\f wbl\ppp wbl\fff wbl\ppp wbl ',
        '10/8' : r' wbh8\fff r r   wbl\fff r r  wbl\fff r  wbl\fff r  ',
        '12/2' : r' wbh2\fff wbl\ppp wbl   wbl\fff wbl\ppp wbl  wbl\fff wbl\ppp wbl  wbl\fff wbl\ppp wbl ',
        '12/8' : r' wbh8\fff r r   wbl\fff r r  wbl\fff r r  wbl\fff r r  ',

        } 
    ## ignore pylint complaint about backslashes in doc test
    ## pylint: disable = W1401
    def partialrepl(match):
        """ 
        Append an appropriately sized rest after an occurrence of the LilyPond
        \partial construct.  The match argument is a match object supplied if
        the partialptn regex matches an input string.
        >>> test = r"\foo \partial 4 wbl4 \partial 2 wbl2"
        >>> re.sub(_partialptn, partialrepl, test)
        >>> re.sub(partialptn, partialrepl, test)
        '\\foo \\partial 4 r4 wbl4 \\partial 2 r2 wbl2'
        """
        i, j = match.span()
        return match.string[i:j] + 'r' + match.groups()[0] + ' '


    try:
        #print rhythm
        #print ticks[meter]
        #print structure_merge(rhythm, ticks[meter], stripit=True)
        smerge = structure_merge(rhythm, ticks[meter], stripit=True)
        patched = re.sub(_partialptn, partialrepl, smerge)
        patched = drum_mode_cleanup(patched)
        #print patched
        metronome.append(patched)

    except KeyError:
        print "No ticks defined for {} meter!".format(meter)
        print "Inserting full measure rest"
        fmr = "R1*{}".format(meter)
        metronome.append(fmr)



    return meter

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

def lilysafe_name(name):
    """
    Convert numbers to strings and remove other non-alpha chars.
    >>> lilysafe_name('Bass 1')
    'BassOne'
    """
    numnames = "Zero One Two Three Four Five Six Seven Eight Nine".split(' ') 
    # Don't complain about string module. pylint: disable=W0402
    from string import letters, digits
    def safechar(c):
        """ Convert one char to a safe string """
        if c in letters:
            return str(c)
        elif c in digits:
            return numnames[int(c)]
        else:
            return ""
    return ''.join([safechar(c) for c in name])    


def mklily(music, fp, voice_order):
    """
    Process and catenate the full score and print it to the LilyPond file
    object 'fp'.  At present, we restrict this function to one voice at a time
    and require that the voice_order arg have 'structure' as the first item,
    e.g. voice_order = ['structure', 'bass1']

    The restriction is enforce by assertions.
    """
    assert len(voice_order) == 2
    assert voice_order[0] == 'structure'

    name = music[voice_order[1]]['name']
    _ = Template(music['_top']['body'])
    top = _.substitute(music['_top']['items'], voicename=name)
    print >> fp, top
    
    _ = Template(music['_bottom']['body'])
    bottom = _.substitute(music[voice_order[1]])

    meter = None
    for voice in voice_order:
        ## Make some short names to access subdicts 
        vdict = music[voice]
        abbr = lilysafe_name(vdict['labbr'])
        rwrapper = vdict['rwrapper']
        if voice == 'structure':
            metronome = []
        else:
            metronome = None

        #try:
        #    metronome = vdict['metronome']
        #    metronome = [] # clear any leftovers from prior compilations.
        #    #print "{} has metronome!".format(voice)
        #except KeyError:
        #    metronome = None

        ## Init mergelists
        mergelist = [abbr + 'Music = ' + rwrapper[0]]
        mergemidi = [abbr + 'Midi = ' + rwrapper[0]]

        ## Append merged elements to mergelists
        for i, rhy in enumerate(vdict['rhythm']):
            pitches = vdict['pitches'][i]
            mergelist.append(merge(pitches, rhy)[0])
            if metronome is not None: #music[voice].has_key('metronome'):
                meter = mkticks(metronome, rhy, meter)
            else:
                midirhythm = structure_merge(music['structure']['rhythm'][i], 
                                                 rhy, 
                                                 stripit = False)
                mergemidi.append(merge(pitches, midirhythm)[0])


        ## Print merged music to LilyPond file.
        mergelist.append(rwrapper[1])
        if voice == 'structure':
            ptn = _fms
        else:
            ptn = _fmr

        mergelist = gather_fm_rests(mergelist, ptn=ptn)
        print >> fp, "\n".join(mergelist)

        if music[voice].has_key('lyrics'):
            lwrapper = vdict['lwrapper']
            lyriclist = [abbr + 'Words = ' +  lwrapper[0]]
            lyriclist.extend(vdict['lyrics'])
            lyriclist.append(lwrapper[1])
            print >> fp, "\n".join(lyriclist)

        if metronome is not None:
            metromerge = [voice + r'Ticks = \drums {']
            metromerge.extend(metronome)
            metromerge.append('}')
            print >> fp, "\n".join(metromerge)
        else:
            mergemidi.append(rwrapper[1])
            print >> fp, "\n".join(mergemidi)



    print >> fp, bottom


# ignore pylint warnings about too many branches and statements
# pylint: disable = R0912, R0915
def get_input(music, voice, bar, insert=False):
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
    # pylint: disable=C0102
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

    sentinel = ''

    prompt = "{} pitches: bar {}\n".format(voice, bar)
    while True:     
        #print prompt
        if insert:
            #pitches = '\n'.join(iter(raw_input, sentinel))
            pitches = rli.rlinput(prompt, sentinel, ctxkey='pitches')
            if pitches == sentinel:
                ## Interpret empty string to mean user wants a full bar rest
                ## and no lyrics.
                srhythm = music['structure']['rhythm']
                tsig = last_time_signature(srhythm[0:ibar+1])
                if tsig is None:
                    print "No time signature found in structure!"
                    return
                else:
                    barlength = "1*"+tsig
                    if voice == 'structure':  #special case
                        rest = 's' 
                    else:
                        rest = 'R'

                    vpitches[ibar] = rest
                    vrhythm[ibar] = barlength
                    
                    #music[voice]['pitches'].append(rest)
                    #music[voice]['rhythm'].append(barlength)
                    #if music[voice].has_key('lyrics'): 
                    #    music[voice]['lyrics'].append('')
                    msg = "Appended full measure rest of length {}."
                    print msg.format(barlength)
                    return

            else:
                vpitches[ibar] = pitches
                #music[voice]['pitches'].append(pitches)
        else:
            #prefill = music[voice]['pitches'][ibar]
            prefill = vpitches[ibar]
            pitches  = rli.rlinput(prompt, prefill, ctxkey='pitches')
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
    else:
        _ = dict()
        props = "name abbr rel clef has_lyrics".split(' ')
        defaults = ('Bass I', 'B1', 'c', 'bass', 'y')
        for k, dflt in zip(props, defaults) :
            _[k] = rli.rlinput("{} :".format(k), dflt, 
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
            rest = 'r'  #special case
        else:
            rest = 'R' 

        vdict['pitches'] = insertrange(vdict['pitches'],
                                       [rest,]*nbars, i0)        
        vdict['rhythm'] = insertrange(vdict['rhythm'],
                                      [barlength,]*nbars, i0)        
    
if __name__ == '__main__':
    from doctest import testmod
    testmod()

