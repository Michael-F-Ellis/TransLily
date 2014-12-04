#!/usr/bin/env python
"""
Quick test of core functionality.

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
## Don't fuss about toplevl names. pylint: disable=C0103
from shutil import rmtree
import pexpect

base = "quicktest"
try:
    rmtree(base)
except OSError:
    pass

def append(child, voice, pitches, rhythm, lyrics):
    """ Append music to voice """
    snd = child.sendline
    exp = child.expect

    snd('a {}'.format(voice))
    exp(r"pitches: bar \d+")
    snd(pitches)
    snd('')

    exp(r"rhythm: bar \d+")
    snd(rhythm)
    snd('')

    if lyrics is not None:
        exp(r"lyrics: bar \d+")
        snd(lyrics)
        snd('')

    exp(r'\(Cmd\)')

child = pexpect.spawn('./translily.py {}'.format(base))
#child = pexpect.spawn('./BaritoneTemplate.py {}'.format(base))
child.logfile = file('quicktest.log','w+')
snd = child.sendline
exp = child.expect

## Show help
exp("Poet")
snd('')
exp("Here")
snd('')
exp("Composer")
snd('')
exp("Title")
snd('')

## Add 'b1' voice
snd('n b1')
exp('Adding voice b1')
exp('name.* :')
snd('Bass I')
exp('abbr.* :')
snd('B1')
exp('rel.* :')
snd('c')
exp('clef.* :')
snd('bass')
exp('lyrics.* :')
snd('y')

## pitches, rhythm, lyrics for bar 1 of bass1
exp('pitches: bar 1')
snd('a b c d')
snd('')
exp('bar 1')
snd('4 4 4 4')
snd('')
exp('bar 1')
snd('no no no no')
snd('')

## compile 'bass1'
exp('(Cmd)')
snd('c b1')
exp('Success:.*(Cmd)')

append(child, 'b1', 'e f g a', '4 4 4 4', 'la la la la')

## test insertion
snd('i structure 2 4')
exp('(Cmd)')
snd('i b1 2 3')

## compile 'bass1' again. Should see 2 measure rest in middle
exp('(Cmd)')
snd('c b1')
exp('Success:.*(Cmd)')

## Add s1 voice, paste from b1, then compile
snd('n s1')
exp('Adding voice s1')
exp('name.* :')
snd('Soprano I')
exp('abbr.* :')
snd('S1')
exp('rel.* :')
snd("c''")
exp('clef.* :')
snd('treble')
exp('lyrics.* :') 
snd('y')
exp('pitches: bar 1')
snd('')
exp('(Cmd)')

snd('p b1 1 4 s1 1')
exp('(Cmd)')
snd('c s1')
exp('Success:.*(Cmd)')

child.interact()
#snd('q')
exp(pexpect.EOF)
