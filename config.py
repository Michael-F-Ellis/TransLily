#!/usr/bin/env python
"""
Default configuration file for TransLily

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


#pylint: disable=W0402
_toptemplate = r"""
\version "2.18.2"
\pointAndClickOff

\include "transcription_helpers.ly"

\paper {
  top-system-spacing #'basic-distance = #10
  score-system-spacing #'basic-distance = #20
  system-system-spacing #'basic-distance = #20
  last-bottom-spacing #'basic-distance = #10
}

\header {
    %% Comment out any fields that are not needed.

    % The following fields are centered
        %dedication = "Dedication?"
        title = "$title"
        %subtitle = "Subtitle"
        subsubtitle = "$voicename"

    % The following fields are evenly spread on one line
    % the field "instrument" also appears on following pages
        %instrument = \markup \with-color #green "Instrument"
        poet = "$poet"
        composer = "$composer"

    % The following fields are placed at opposite ends of the same line
        % meter = ""
        % arranger = ""

    % The following fields are centered at the bottom
        tagline = "Transcribed by $transcriber"
        %copyright = "copyright goes at the bottom of the first page"
}

global = {


  % Next 2 lines, if uncommented, alter the default beaming in 3/4 time.
  %\set Timing.beamExceptions = #'()
  %\set Voice.beatStructure = #'(1 1 1) 

  \override BreathingSign #'Y-offset = #3  
  \override MultiMeasureRest #'staff-position = #0   
  \compressFullBarRests     
} 
vglobal = {
    % Initial settings for choral voices
    \slurDown
    \override Rest #'staff-position = #0
}


"""






##
## This section is emitted verbatim and must be valid Lilypond input.
## Gnerally speaking, you should not need to edit this.
##

_bottomtemplate = r"""

\score {
  <<
     \set Score.markFormatter = #format-mark-box-numbers
      
      \new Staff = "${labbr}" \with {
          instrumentName = #"${name} "
          shortInstrumentName = #"${abbr} " 
          } <<
        \clef "$clef"
        \new Voice = "${labbr}" { \voiceOne \global \vglobal \${labbr}Music }
        \new Voice = "structure" { \voiceTwo \global \vglobal \structMusic }
      >>
      \new Lyrics = "${labbr}"
      

    \context Lyrics = "${labbr}" \lyricsto "${labbr}" \${labbr}Words



  >>

  \layout {
  \context {
    %\Staff \RemoveEmptyStaves
    \override VerticalAxisGroup.remove-first = ##t
    }
  }
}

\include "articulate.ly"

\score {
    \unfoldRepeats \articulate { <<  \${labbr}Midi  \\ \structureTicks >>  }
    
    \midi {
        % voodoo that lets us specify instrument in melody
        \context {
            \Staff
            \remove "Staff_performer"
        }
        \context {
            \Voice
            \consists "Staff_performer" 
        }
    }
}    
"""


##
## This section is merged
##
## allow 'music' as a toplevel name pylint: disable=C0103
tmusic = dict(
    ## structure should contain only time sigs, tempos, and repeats    
    structure = dict(
        rwrapper = [r"{\hideNotes ", r"\unHideNotes}"],  
        rhythm = [r'\time @4/4 1',],
        pitches = ['r'],
        metronome = [],
        abbr = "struct",
        labbr = "struct",
        ),

    _top = dict(
        body = _toptemplate,
        items = dict(
            title="Excellent Title",
            poet="Famous Poet",
            composer="Famous Composer",
            transcriber="Your Name Here",)
        ),

    _bottom = dict(
        body = _bottomtemplate,
        #items = dict()
        ),


    )

    

