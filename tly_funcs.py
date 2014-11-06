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

## Pttern for full measure rest
_fmr = re.compile(r"""
        R         # literal 'R'
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
            

def mk_mmr(measure, count):
    """
    >>> mk_mmr('\\time 4/4 R1', 3)
    '\\time 4/4 R1*3'
    """
    index = _fmr.search(measure).span()[1]
    return measure[0:index] + '*{}'.format(count) + measure[index:]
    
def gather_fm_rests(mergelist):
    """
    >>> gather_fm_rests([r'\\time 4/4 R1', r'R1', r'R1'])
    ['\\\\time 4/4 R1*3']

    """
    result = []
    gathering = False
    count = 0
    start = None
    mergelist.append(r'')
    for s in mergelist:
        #print "{}".format(s)
        match = _fmr.search(s)
        #print match
        if gathering:
            if match == None:
                result.append(mk_mmr(start, count))
                result.append(s)
                gathering = False
            else:
                span = match.span()
                if 0 == span[0] and len(s) == span[1]:
                    ## it's bare so bump the count and continue
                    count += 1
                    #print 'bare'

                else:
                    ## not bare, so start a new gathering 
                    ## after saving the current one.
                    result.append(mk_mmr(start, count))
                    count = 1
                    start = s
                    #print "Not bare"
                    #print result
        else:
            if match == None:
                result.append(s) # copy with out modification
            else:
                ## start mew gathering
                gathering = True
                start = s
                count = 1
                #print "Starting to gather with {}".format(s)

    return result[0:-1] ## drop the final (empty) element                


_timesig = re.compile(r"\\time\s+@(\d+/\d+)")
_partialptn = re.compile(r'partial\s+(\S+)\s+')

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
        try:
            metronome = vdict['metronome']
            metronome = [] # clear any leftovers from prior compilations.
            #print "{} has metronome!".format(voice)
        except KeyError:
            metronome = None

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
        if len(voice_order) == 1:
            mergelist = gather_fm_rests(mergelist)
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

import readline
def rlinput(prompt, prefill=''):
    """
    Get user input with readline editing support.
    """
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        edited = raw_input(prompt)
        if edited.endswith(r'%%'):
            ## Invoke external editor
            edited = external_edit(edited[0:-2])
        return edited
    finally:
        readline.set_startup_hook()

# ignore pylint warnings about too many branches and statements
# pylint: disable = R0912, R0915
def get_input(music, voice, bar):
    """
    The overall handler for user input. Prompts for 
    pitches, rhythm, and lyrics (for voices with lyrics).
    Pre-processes the input and stores it into the _music dict().
    """
    ## Convert bar number to list index -- assumes music starts at bar 1  
    # pylint: disable=C0102
    if bar == None:
        appending = True
        ibar = len(music[voice]['rhythm'])
        bar = ibar + 1
    else:
        ibar = bar - 1
        appending = False


    sentinel = ''

    prompt = "{} pitches: bar {}\n".format(voice, bar)
    while True:     
        print prompt
        if appending:
            pitches = '\n'.join(iter(raw_input, sentinel))
            if pitches == sentinel:
                ## Interpret empty string to mean user wants a full bar rest
                ## and no lyrics.
                tsig = last_time_signature(music['structure']['rhythm'])
                if tsig is None:
                    print "No time signature found in structure!"
                    return
                else:
                    barlength = "1*"+tsig
                    if voice == 'structure':
                        rest = 'r'  #special case
                    else:
                        rest = 'R'
                    music[voice]['pitches'].append(rest)
                    music[voice]['rhythm'].append(barlength)
                    if music[voice].has_key('lyrics'): 
                        music[voice]['lyrics'].append('')
                    msg = "Appended full measure rest of length {}."
                    print msg.format(barlength)
                    return

            else:
                music[voice]['pitches'].append(pitches)
        else:
            prefill = music[voice]['pitches'][ibar]
            pitches  = rlinput('', prefill)
            music[voice]['pitches'][ibar] = pitches
            
        if pitches != '':
            print "ok"
            break

    prompt = "{} rhythm: bar {}\n".format(voice, bar)
    while True:     
        print prompt
        if appending:
            rhythm = '\n'.join(iter(raw_input, sentinel))
            music[voice]['rhythm'].append(rhythm)
        else:
            prefill = music[voice]['rhythm'][ibar]
            rhythm  = rlinput('', prefill)
            music[voice]['rhythm'][ibar] = rhythm
            
        if rhythm != '':
            print "ok"
            break

    if not music[voice].has_key('lyrics'):
        return

    prompt = "{} lyrics: bar {}\n".format(voice, bar)
    print prompt
    if appending:
        lyrics = '\n'.join(iter(raw_input, sentinel))
        music[voice]['lyrics'].append(lyrics)
    else:
        prefill = music[voice]['lyrics'][ibar]
        lyrics  = rlinput('', prefill)
        music[voice]['lyrics'][ibar] = lyrics

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
            _[k] = rlinput("{} :".format(k), dflt)

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
            itemd[k] = rlinput("{} :".format(k), v)
            
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

if __name__ == '__main__':
    from doctest import testmod
    testmod()



