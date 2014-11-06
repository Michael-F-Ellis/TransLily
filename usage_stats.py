"""
Usage_stats.py 

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
import time
import operator
from utils import advance_generator_once

@advance_generator_once
def user_action_tracker():
    """ 
    An analyzer to assist in development.  Records time spent in various editing commands
    and time spent between commands.  Prints a summary at program exit.
    """
    accum = dict(waiting=[])
    wait_start = time.time()
    wait_end = None
    cmd_start = None
    cmd_end = None
    try:
        while True:
            ## state: Waiting ...
            cmd = yield
            wait_end = cmd_start = time.time()
            accum['waiting'].append(wait_end - wait_start)
            ## state: in cmd
            yield
            cmd_end = wait_start = time.time()
            cmd_name = cmd.split(' ')[0]
            assert len(cmd_name) > 0
            try:
                accum[cmd_name].append(cmd_end - cmd_start)
            except KeyError:
                ## First instance of cmd in this session
                accum[cmd_name] = [cmd_end - cmd_start]


    finally:
        sums = dict()
        for k, v in accum.iteritems():
            sums[k] = sum(v)
        total = sum(sums.values())
        sorted_sums = sorted(sums.items(), key = operator.itemgetter(1))
        sorted_sums.reverse()
        print "Usage stats:"
        print "{:0.2f} seconds elapsed".format(total)
        for c, v in sorted_sums:
            print "{} : {:0.1f}%".format(c, 100*v/total)


