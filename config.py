#!/usr/bin/env python
"""
Default configuration file for TransLily

This file consists mostly of templates used by the TransLily 'compile' command
to generate a LilyPond file.  

The templates are enclosed in Python triple-quotes. They specify various
LilyPond settings that are appropriate for single line part transcriptions. 

LilyPond offers a huge variety of typesetting options. If some of your
preferences are different, you can make a copy of this file, edit it, and save
it as '_config.py'. 

When TransLily starts, it uses '_config.py' if it exists before defaulting to
'config.py.'



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


## The _top template appears at the top of the LilyPond file. It controls aspects
## such as paper size, margins. Information about the title, composer, etc is also
## substitued into the template when the output file is generated.  Look for the
## items that begin with '$' signs. If you define any new ones, you must add a
## corresponding item to the 'tmusic' template at the bottom of this file.

#pylint: disable=W0402
_toptemplate = r"""
%{
    THIS FILE WAS GENERATED AUTOMATICALLY BY TransLily.  A new version
    overwrites the old one each time you compile from TransLily. 
    
    Please use a COPY of this file if you want to edit it and keep your
    changes.
%}

% LilyPond requires a version statement,
\version "2.18.2"

% Makes compilation somewhat faster.
\pointAndClickOff

% Import convenience functions provided with TransLily
\include "transcription_helpers.ly"

\paper {
  % Typical margin settings  
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
  % Some useful settings for single voice parts

  % Next 2 lines, if uncommented, alter the default beaming in 3/4 time.
  \set Timing.beamExceptions = #'()
  \set Voice.beatStructure = #'(1 1 1) 

  % Place breath marks a little higher than the default.
  \override BreathingSign #'Y-offset = #3

  % Vertically center multi-measure rest symbols.
  \override MultiMeasureRest #'staff-position = #0

  % Tell LilyPond not to expand multi-measure rests.
  \compressFullBarRests

  % Vertically center all rest symbols
  \override Rest #'staff-position = #0

  % Suppress Kirchenpausen rests.
  \override MultiMeasureRest.expand-limit = #1

  % Number each bar for easier proofing.
  \override Score.BarNumber.break-visibility = ##(#f #t #t)
} 

"""

## The _bottom template contains the \score block that tells LilyPond how to
## create the PDF and MIDI files.  It also contains '$' sign items that are
## substitued by LilyPond. You shouldn't change or add to these.

_bottomtemplate = r"""

\score {
  %% PDF Creation
  <<
      \new Staff = "${labbr}" \with {
          instrumentName = #"${name} "
          shortInstrumentName = #"${abbr} " 
          } <<
        \clef "$clef"
        \new Voice = "${labbr}" { \global \${labbr}Music }
        \new Voice = "structure" { \global \structure }
      >>

     %% TransLily prepends '% ' to comment out the lines
     %% below if the voice has no lyrics
         $iflyrics \new Lyrics = "${labbr}"
         $iflyrics \context Lyrics = "${labbr}" \lyricsto "${labbr}" \${labbr}Words
  >>

  \layout { }
  }

  %% MIDI Creation

  % The 'articulate' module included with LilyPond adjusts the midi
  % output for increased musicality.
  
  \include "articulate.ly"
  
  \score {
      \unfoldRepeats \articulate { <<  \${labbr}Music  \\ \structure \\ \metronome >>  }
      
      \midi {
          % The following lets us specify the instrument in the melody
          % instead of at the staff level. This allows playing cue notes
          % with a different midi instrument than the main voice.
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

    
## TickDict is a python dictionary of metronome tick patterns for common meters.
## The patterns in this list create loud down beats and soft sub-beats using a
## 'woodblock' instrument. 

TickDict = { 
    # allow long lines. pylint: disable = C0301    
    '2/2': {   'pitches': 'wbh wbl wbl wbl',
               'rhythm': r'4\fff 4\ppp 4\ff 4\ppp'},

    '2/4': {   'pitches': 'wbh wbl', 
               'rhythm': r'4\fff 4\ppp'},
    
    '3/2': {   'pitches': 'wbh wbl wbl', 
               'rhythm': r'2\fff 2\ppp 2'},
    
    '3/4': {   'pitches': 'wbh wbl wbl', 
               'rhythm': r'4\fff 4\ppp 4'},
    
    '3/8': {   'pitches': 'wbh wbl wbl', 
               'rhythm': r'8\fff 8 8'},
    
    '4/4': {   'pitches': 'wbh wbl wbl wbl', 
               'rhythm': r'4\fff 4\ppp 4 4'},
    
    '5/2': {   'pitches': 'wbh wbl wbl wbl wbl',
               'rhythm': r'2\fff 2\ppp 2\ff 2\ppp 2'},
    
    '5/4': {   'pitches': 'wbh wbl wbl wbl wbl', 
               'rhythm': r'4\fff 4\ppp 4 4 4'},
    
    '5/8': {   'pitches': 'wbh wbl wbl wbl wbl', 
               'rhythm': r'8\fff 8 8 8\fff 8'},
    
    '6/4': {   'pitches': 'wbh wbl wbl wbl wbl wbl',
               'rhythm': r'4\fff 4\ppp 4 4\fff 4\ppp 4'},
    
    '6/8': {   'pitches': 'wbh wbl', 
               'rhythm': r'4.\fff 4.\fff'},
    
    '7/4': {   'pitches': 'wbh wbl wbl wbl wbl wbl wbl',
               'rhythm': r'4\fff 4\ppp 4 4 4\fff 4\ppp 4'},
    
    '8/8': {   'pitches': 'wbh wbl wbl', 
               'rhythm': r'4.\fff 4.\fff 4\fff'},
    
    '9/2': {   'pitches': 'wbh wbl wbl wbl wbl wbl wbl wbl wbl',
               'rhythm': r'2\fff 2\ppp 2 2\fff 2\ppp 2 2\fff 2\ppp 2'},
    
    '9/8': {   'pitches': 'wbh wbl wbl', 
               'rhythm': r'4.\fff 4.\fff 4.\fff'},

    '10/4': {   'pitches': 'wbh wbl wbl wbl wbl wbh wbl wbl wbl wbl',
                'rhythm': r'4\fff 4\ppp 4\fff 4\ppp 4 4\f 4\ppp 4\fff 4\ppp 4'},

    '10/8': {   'pitches': 'wbh wbl wbl wbl',
                'rhythm': r'4.\fff 4.\fff 4.\fff 4\fff'},

    '12/2': {   'pitches': 'wbh wbl wbl wbl wbl wbl wbl wbl wbl wbl wbl wbl',
                'rhythm': r'2\fff 2\ppp 2 2\fff 2\ppp 2 2\fff 2\ppp 2 2\fff 2\ppp 2'},

    '12/8': {   'pitches': 'wbh wbl wbl wbl',
                'rhythm': r'4.\fff 4.\fff 4.\fff 4.\fff'},

    }


## TransLily imports the following dictionary to create new projects. Don't 
## edit it unless you really, really know what you're doing.

## allow 'tmusic' as a toplevel name pylint: disable=C0103
tmusic = dict(
    ## structure should contain only time sigs, tempos, and repeats    
    structure = dict(
        rwrapper = [r"{ ", r" }"],  
        rhythm = [r'\time @4/4 1*4/4',],
        pitches = ['s'],
        name = "Structure",
        clef = "treble",
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
        ## No 'items' key for this dictionary
        #items = dict()
        ),

    _ticks = TickDict


    )
