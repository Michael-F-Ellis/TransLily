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

## Add 'bass1' voice
snd('a bass1')
exp('No such voice: bass1')
snd('y')
exp('name :')
snd('')
exp('abbr :')
snd('')
exp('rel :')
snd('')
exp('clef :')
snd('')
exp('lyrics :')
snd('')

## pitches, rhythm, lyrics for bar 1 of bass1
exp('bass1 pitches: bar 1')
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
snd('c bass1')
exp('Success:.*(Cmd)')
child.interact()
#snd('q')
exp(pexpect.EOF)
