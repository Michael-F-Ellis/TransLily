"""
LilyPond file creation functions

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
## Don't complain about importing string module
## pylint: disable=W0402
## Ignore blacklisted name complaints: pylint: disable=C0102
from string import Template
import re
from utils import lilysafe_name

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

## Matches single pitches or chords in <>'s
_pitch_or_chord = re.compile(r"<[^<>]+>|\S+")

## Pattern to match a note duration token
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

def mklily(music, fp, voicename):
    """
    Process and catenate the score and print it to the LilyPond file
    object 'fp'. 
    """
    vdict = music[voicename]
    name = vdict['name']
    abbr = lilysafe_name(vdict['labbr'])
    rwrapper = vdict['rwrapper']

    _ = Template(music['_top']['body'])
    top = _.substitute(music['_top']['items'], voicename=name)
    print >> fp, top
    
    if voicename == 'structure':
        print >> fp, r"structure = {}"
        metromusic  = merge_metronome(music)
        print >> fp, "\n".join(metromusic)

    elif voicename == 'metronome':
        print >> fp, r"metronome = {}"
        structmusic = merge_structure(music)
        print >> fp, "\n".join(structmusic)

    else:
        structmusic = merge_structure(music)
        print >> fp, "\n".join(structmusic)
        metromusic  = merge_metronome(music)
        print >> fp, "\n".join(metromusic)

    mergelist = [abbr + 'Music = ' + rwrapper[0]]

    ## Append merged elements to mergelists
    for i, rhy in enumerate(vdict['rhythm']):
        pitches = vdict['pitches'][i]
        mergelist.append(merge(pitches, rhy)[0])

    ## Print merged music to LilyPond file.
    mergelist.append(rwrapper[1])
    mergelist = gather_fm_rests(mergelist, ptn=_fmr)
    print >> fp, "\n".join(mergelist)

    if vdict.has_key('lyrics'):
        lwrapper = vdict['lwrapper']
        lyriclist = [abbr + 'Words = ' +  lwrapper[0]]
        lyriclist.extend(vdict['lyrics'])
        lyriclist.append(lwrapper[1])
        print >> fp, "\n".join(lyriclist)




    iflyrics = '' if vdict.has_key('lyrics') else '% '
    _ = Template(music['_bottom']['body'])
    bottom = _.substitute(vdict, iflyrics=iflyrics)

    print >> fp, bottom


def merge_structure(music):
    """ Special handling for 'structure' voice """
    vdict = music['structure']
    rwrapper = vdict['rwrapper']
    mergelist = ['structure = ' + rwrapper[0]]

    for i, rhy in enumerate(vdict['rhythm']):
        pitches = vdict['pitches'][i]
        mergelist.append(merge(pitches, rhy)[0])   

    mergelist.append(rwrapper[1])
    ptn = _fms
    mergelist = gather_fm_rests(mergelist, ptn=ptn)
    return mergelist

def merge_metronome(music):
    """ Special handling for metronome voice """

    rwrapper = [r'metronome = \drums { ', r' }' ]
    try:
        vdict = music['metronome']
    except KeyError:
        print "Music has no metronome voice."
        return [r'metronome = \drums { ', r' }' ]

    
    mergelist = [rwrapper[0]]

    for i, rhy in enumerate(vdict['rhythm']):
        pitches = vdict['pitches'][i]
        mergelist.append(merge(pitches, rhy)[0])   

    mergelist.append(rwrapper[1])
    return mergelist


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

def classify_rest_ptn(bar, ptn, exact=None):
    # allow excess branches and returns.
    # pylint: disable = R0911, R0912
    """
    Called by gather_fm_rests() to classify a bar
    according to whether it contains a full-measure rest
    and where the rest lies in the bar relative to 
    other content.

    >>> classify_rest_ptn("a1", _fmr)
    ('unmatched', None)

    >>> classify_rest_ptn(" R1*4/4 ", _fmr)
    ('begin', 'R1*4/4')

    >>> classify_rest_ptn(" R1*4/4 ", _fmr, exact='R1*4/4' )
    ('append', 'R1*4/4')

    >>> classify_rest_ptn(" R1*4/4 \\tempo 4=90", _fmr)
    ('append_end', None)

    >>> classify_rest_ptn(" R1*3/4 ", _fmr, exact='R1*4/4' )
    ('end_begin', 'R1*3/4')

    >>> classify_rest_ptn(" R1*3/4 \\time 4/4 ", _fmr, exact='R1*4/4' )
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
        action, exact = classify_rest_ptn(s, ptn, exact=exact)
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

def mk_mmr(measure, count, ptn=_fmr):
    """
    >>> mk_mmr('\\time 4/4 R1', 3)
    '\\time 4/4 R1*3'
    """
    index = ptn.search(measure).span()[1]
    return measure[0:index] + '*{}'.format(count) + measure[index:]
    
if __name__ == '__main__':
    from doctest import testmod
    testmod()
