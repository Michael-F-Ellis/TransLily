"""
A few things that really do need to be shared among modules.

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
import sys
## The dictionary where we store the present state of the notation.

Music = None

## The absolute path to the project folder

ProjectFolder = None

SessionLogfile = None

## Intentional use of [] as kwarg initializer. pylint: disable=W0102
def debug(msg, _cache=[None]):
    """ Writes msg to SessionLogfile or stderr """
    if SessionLogfile is not None:
        if _cache[0] in (None, sys.stderr):
            _cache[0] = file(os.path.join(ProjectFolder, SessionLogfile), 'w+')
    else:
        if _cache[0] is None:
            _cache[0] = sys.stderr

    print >> _cache[0], msg
    ## Flush and sync so we can use 'tail -f' to watch output in real time.
    _cache[0].flush()
    os.fsync(_cache[0].fileno())
