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
from utils import lilysafe_name, gather_token_sequences

## Pattern for full measure rest
_fmr = re.compile(r"""
        R         # literal 'R'
        \d+       # followed by at least 1 digit
        [0-9.*/]* # followed by 0 or more digits, dots, '*'s, or '/'s
        """, re.VERBOSE)

                  #  
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
        print >> fp, structmusic

    else:
        structmusic = merge_structure(music)
        print >> fp, structmusic
        metromusic  = merge_metronome(music)
        print >> fp, "\n".join(metromusic)

    mergelist = [abbr + 'Music = ' + rwrapper[0]]

    ## Append merged elements to mergelists
    for i, rhy in enumerate(vdict['rhythm']):
        pitches = vdict['pitches'][i]
        mergelist.append(merge(pitches, rhy)[0])

    ## Print merged music to LilyPond file.
    mergelist.append(rwrapper[1])
    merged = "\n".join(mergelist)  
    #print >> fp, fm_gather_all(merged, _fmr)
    print >> fp, gather_token_sequences(_fmr, merged)
    #mergelist = gather_fm_rests(mergelist, ptn=_fmr)
    #print >> fp, "\n".join(mergelist)

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
    merged = "\n".join(mergelist)
    return gather_token_sequences(_fms, merged)
    #return fm_gather_all(merged, ptn=_fms)

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


def mk_mmr(startbar, endbar, count, ptn=_fmr):
    """
    >>> mk_mmr('\\time 4/4 { R1', 'R1 }', 3)
    '\\time 4/4 { R1*3 }'
    """
    startindex = ptn.search(startbar).span()[1]
    measure = startbar[0:startindex] + '*{}'.format(count)
    try:
        endindex = ptn.search(endbar).span()[1]
        measure += endbar[endindex:]
    except AttributeError:
        ## no ptn match in endbar.
        ## don't append anything
        pass
    return measure

if __name__ == '__main__':
    from doctest import testmod
    testmod()
