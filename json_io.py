"""
Provides JSONFolder, a class for managing a folder of json files that represent
snapshots of a single work in progress.

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
import json
#import gzip
import re

_fileptn = re.compile(r"^\d+\.json$")

class JSONFolder(object):
    """
    A class for managing a folder of json files that represent snapshots
    of a single work in progress.
    """

    def __init__(self, path, workname, onload=None):
        """
        Create a folder named after workname if none exists.  Otherwise use the
        existing one.  Initialize variables needed for saving, retrieving, undo,
        and redo.
        """
        path = os.path.abspath(path)
        self.foldername = os.path.join(path, workname)
        self.jsonfoldername = os.path.join(self.foldername, 'json')
        self.filenames = []
        self.current = None
        self.loadindex = None
        self.saveindex = 0
        self.onload = onload
        try:
            os.makedirs(self.foldername)
        except OSError:
            if not os.path.isdir(self.foldername):
                raise
            else:
                self._update()

        try:
            os.makedirs(self.jsonfoldername)
        except OSError:
            if not os.path.isdir(self.jsonfoldername):
                raise
            else:
                self._update()

    def _update(self):
        """
        Private method to update list of files and  indices.
        """
        sortkey = lambda x: os.stat(
                  os.path.join(self.jsonfoldername, x)).st_mtime

        names = os.listdir(self.jsonfoldername)
        names.sort(key=sortkey)
        #names.reverse()
        self.filenames = [name for name in names if _fileptn.match(name)]
        if len(self.filenames):
            last = self.filenames[-1]
            index = int(last.split('.')[0])
            self.saveindex = index + 1
            self.current = last
            self.loadindex = len(self.filenames) - 1
        else:
            self.saveindex = 0

    def save(self, obj):
        """
        Serialize the object and save in the folder.
        """
        name = "{}.json".format(self.saveindex)
        jsonf = open(os.path.join(self.jsonfoldername, name), 'w')
        json.dump(obj, jsonf)
        jsonf.close()
        self._update()
        print "Saved {}".format(name)
        #self.current = name
        #self.undostack.append(self.current)
        #self.saveindex += 1



    def load(self):
        """
        Deserialize, and return the content of the file identified by
        self.current as a python object. Self.current is the filename whose
        content is currently active.
        """
        if self.current is not None:
            jsonf = open(os.path.join(self.jsonfoldername, self.current))
            obj = json.load(jsonf)
            jsonf.close()
            print "Loaded {}".format(self.current)
            self.onload(obj)  ## No protection. Fail quickly and loudly.
            return obj
        else:
            raise ValueError("No current file!")

    def undo(self):
        """
        Make the previous file active and load it. Return None if no previous
        file exists.
        """
        if self.loadindex is not None and self.loadindex > 0:
            self.loadindex -= 1
            self.current = self.filenames[self.loadindex]
            return self.load()
        else:
            print "Nothing to undo"
            return None

    def redo(self):
        """
        Make the following file active and load it. Return None if no following
        file exists.
        """
        lastindex = len(self.filenames) - 1
        if self.loadindex is not None and self.loadindex < lastindex:
            self.loadindex += 1
            self.current = self.filenames[self.loadindex]
            return self.load()
        else:
            print "Nothing to redo"
            return None


def test():
    """
    >>> import shutil
    >>> dirname = os.path.join(os.path.abspath('/tmp'), 'foo')
    >>> shutil.rmtree(dirname)
    >>> J = JSONFolder(os.path.abspath(r'/tmp'), 'foo')
    >>> obj = [1]
    >>> J.save(obj)
    >>> obj.append(2)
    >>> J.save(obj)
    >>> J.undo()
    [1]
    >>> J.redo()
    [1, 2]
    >>> obj = J.load()
    >>> obj
    [1, 2]
    """
    pass

if __name__ == '__main__':
    from doctest import testmod
    testmod()
