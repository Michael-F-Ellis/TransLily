
\include "english-solfa.ly" % modified to include solfa syllables

%% --------------------------------------------
%{
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
%}    
%% --------------------------------------------
#(define (make-named-instrument default-name)
  (define iname default-name)
     
  (define (set newname)
    (set! iname newname)) 
  
  (define (interface op . rest)
    (cond
      ((eq? op 'set)
        (set (car rest)))
      ((eq? op 'get)
        iname)
      (else (error "Undefined operation"))))
      
   interface)
      
#(define mainInstrument (make-named-instrument "cello"))
#(define cueInstrument (make-named-instrument "acoustic grand"))
#(define clapInstrument (make-named-instrument "woodblock"))

#(define (setMainCueClapInstruments main cue clap)
   (mainInstrument 'set main)
   (cueInstrument 'set cue)
   (clapInstrument 'set clap)
   '())


clap = #(define-music-function (p l m) (ly:music?) 
   #{
    \set midiInstrument = #(clapInstrument 'get)  
    \override NoteHead #'style = #'cross 
    $m
    \revert NoteHead #'style
    \set midiInstrument = #(mainInstrument 'get)
   #})
    
cueLyrics=
#(define-music-function (p l music) (ly:music?)
  "For printing cue lyrics in italic maroon font."
#{
    \override Lyrics.LyricText #'color = #(x11-color 'maroon)
    \override Lyrics.LyricHyphen #'color = #(x11-color 'maroon)
    \override Lyrics.LyricExtender #'color = #(x11-color 'maroon)
    \override LyricText #'font-shape = #'italic
    $music
    \revert Lyrics.LyricText #'color
    \revert Lyrics.LyricHyphen #'color
    \revert Lyrics.LyricExtender #'color
    \revert LyricText #'font-shape
#})

cueNotes=
#(define-music-function (p l music) (ly:music?)
  "for printing cue notes in teeny font in color"
  #{  
      \set midiInstrument = #(cueInstrument 'get)
      \override Accidental #'color = #(x11-color 'maroon)
      \override Beam #'color = #(x11-color 'maroon)
      \override NoteHead #'color = #(x11-color 'maroon)
      \override Rest #'color = #(x11-color 'maroon)
      \override Slur #'color = #(x11-color 'maroon)
      \override Stem #'color = #(x11-color 'maroon)
      \override Tie #'color = #(x11-color 'maroon)
      \override Flag #'color = #(x11-color 'maroon)
      
      \teeny 
      $music 
      \normalsize
      
      \revert  Accidental #'color
      \revert  Beam #'color
      \revert  NoteHead #'color
      \revert  Rest #'color
      \revert  Slur #'color
      \revert  Stem #'color
      \revert  Tie #'color
      \revert  Flag #'color
      
      \set midiInstrument = #(mainInstrument 'get)
  #})

cueBoth=
#(define-music-function (p l lyrics notes) (string? ly:music?)
  "Allows to specify lyrics and notes together"
  #{
    
    \override Lyrics.LyricText #'color = #(x11-color 'maroon)
    \override Lyrics.LyricHyphen #'color = #(x11-color 'maroon)
    \override Lyrics.LyricExtender #'color = #(x11-color 'maroon)
    \override LyricText #'font-shape = #'italic
    \lacc \lyricmode $lyrics
    \revert Lyrics.LyricText #'color
    \revert Lyrics.LyricHyphen #'color
    \revert Lyrics.LyricExtender #'color
    \revert LyricText #'font-shape     
    \cueNotes $notes
  #})
    
%% --------------------------------------------
#(define (make-script x)
   (make-music 'ArticulationEvent
               'articulation-type x))

#(define (add-script m x)
   (if
     (equal? (ly:music-property m 'name) 'EventChord)
     (set! (ly:music-property m 'elements)
           (cons (make-script x)
                 (ly:music-property m 'elements))))
   m)

#(define (add-staccato m)
   (add-script m "staccato"))
   
addStacc =
#(define-music-function (p l music) (ly:music?)
  "for adding stacatto dots to a group of notes."
   (music-map add-staccato music))	 
			
%% -------------------------------------------
 
%#(set-global-staff-size 16)

%% --------------------------------------------
crpoco =
#(make-music 'CrescendoEvent
         'span-direction START
         'span-type 'text
         'span-text "cresc. poco a poco")

sffp = #(make-dynamic-script "sffp")

%% --------------------------------------------
dutchtosolfa =
#`(("ceses" . "daw")
   ("ces" . "de")
   ("c" . "do")
   ("cis" . "di")
   ("cisis" . "dai")
   ("deses" . "raw")
   ("des" . "ra")
   ("d" . "re")
   ("dis" . "ri")
   ("disis" . "rai")
   ("eeses" . "maw")
   ("ees" . "me")
   ("e" . "mi")
   ("eis" . "mai")
   ("eisis" . "my")
   ("feses" . "faw")
   ("fes" . "fe")
   ("f" . "fa")
   ("fis" . "fi")
   ("fisis" . "fai")
   ("geses" . "saw")
   ("ges" . "se")
   ("g" . "sol")
   ("gis" . "si")
   ("gisis" . "sai")
   ("aeses" . "law")
   ("aes" . "le")
   ("a"  . "la")
   ("ais" . "li")
   ("aisis" . "lai")
   ("beses" . "taw")
   ("bes" . "te")
   ("b"   . "ti")
   ("bis"   . "tai")
   ("bisis" . "ty")
   ) 

solfaNames =
#(lambda (grob)
   (let* ((default-name (ly:grob-property grob 'text))
          (new-name (assoc-get default-name dutchtosolfa)))
         (ly:grob-set-property! 
           grob 
           'text 
           (markup #:italic #:smaller new-name))
         (ly:text-interface::print grob)))  

%% From LSR #760. Converts tied notes to skips.  Used to prevent
%% NoteNames engraver from repeating note names on ties.
skipTies = 
#(define-music-function (parser location music) (ly:music?)
(let ((prev-was-tie? #f))
  (define (tied-note->skip evt)
     (let ((elt (ly:music-property evt 'element))
           (elts (ly:music-property evt 'elements))
           (name (ly:music-property evt 'name)))
      (cond ((and prev-was-tie?
                  (eq? name 'EventChord)
                  (pair? elts)
                  (ly:duration? (ly:music-property (car elts) 'duration)))
                (set! prev-was-tie? #f)
                (skip-of-length  evt)) ;; eventChord -> skip 
            ((eq? name 'TieEvent)
                (set! prev-was-tie? #t)
                #f) ;; all tie events will be deleted
            (else
                (if (ly:music? elt) (ly:music-set-property! evt 'element
                                        (tied-note->skip elt)))
                (if (pair? elts) (ly:music-set-property! evt 'elements
                                        (filter-map tied-note->skip elts)))
                evt))))
 (tied-note->skip music)))
         

%% --------------------------------------------
#(define (make-counter)
  (define count 0)
  
  (define (inc)
    (set! count (+ 1 count))
    (number->string count)
    )
    
  (define (set n)
    (set! count n)) 
  
  (define (interface op . rest)
    (cond
      ((eq? op 'set)
        (set (car rest)))
      ((eq? op 'inc)
        (inc))
      (else (error "Undefined operation"))))
      
   interface)
      
#(define sourcePageCounter (make-counter))

setSourcePageNumber =
#(define-music-function (p l n) (number?)
  "Initialize or change the value of the page counter"
  (sourcePageCounter 'set n)
  (make-music 'SequentialMusic 'void #t))

pn =
#(define-music-function (p l m) (ly:music?)
  "Place current page number above staff"
  #{
      $m ^"$(sourcePageCounter 'inc)"
  #})
  
%% --------------------------------------------
#(define (make-music-accumulator)
  (define acc '())

  (define (add lyr) 
    (set! acc (append acc lyr)))

  (define (get) acc)

  (define (interface op . rest)
    (cond
      ((eq? op 'add)
        (add (car rest)))
      ((eq? op 'get)
        (get))
      (else (error "Undefined operation"))))

  interface) 

%% Lyric accumulator functions
#(define defaultLyricAccumulator (make-music-accumulator))

lacc = 
#(define-music-function (parser location music) (ly:music?)
  "For accumulating lyrics mixed with notation"
  (defaultLyricAccumulator 
    'add 
    (ly:music-property music 'elements))
  (make-music 'SequentialMusic 'void #t))



getLyrics = 
#(define-music-function (parser location) ()
 "for retrieving accumulated lyrics."
  (make-music 
    'SequentialMusic 
    'elements 
    (defaultLyricAccumulator 'get))) 


%% Metronome accumulator functions
#(define defaultMetronomeAccumulator (make-music-accumulator))

macc =
#(define-music-function (parser location music) (ly:music?)
  "For accumulating metronome clicks mixed with notation"
  (defaultMetronomeAccumulator
     'add
     (ly:music-property music 'elements))
  (make-music 'SequentialMusic 'void #t))

getMetronomeTrack =
#(define-music-function (parser location) ()
 "for retrieving metronome track."
 (make-music
   'SequentialMusic
   'elements
   (defaultMetronomeAccumulator 'get)))


%% --------------------------------------------
%% Misc. music functions
%% --------------------------------------------
caesura =
#(define-music-function (p l) ()
#{
    \once \override BreathingSign #'text = \markup {
    \musicglyph #"scripts.caesura.straight" }
    \breathe
#})

%% puts a fermata on a barline
barlineFermata =
#(define-music-function (p l) ()
#{
  \once \override Score.RehearsalMark #'break-visibility = #begin-of-line-invisible
  \mark \markup { \musicglyph #"scripts.ufermata" }
#})

%% inserts a dashed barline 
bdash = { \noBreak \bar "dashed" }

%% For skipping notes in lyrics, 
%% Usage: "\lskip n"  where n is the number
%% of notes to skip. Typically used to keep lyrics from
%% being aligned on instrumental cue notes.
lskip = 
#(define-music-function (p l n) (number?) 
#{
    \repeat unfold $n {\skip 4}
#})

%% triplets are common enough to rate a shortcut
trp = 
#(define-music-function (p l music) (ly:music?)
#{
    \times 2/3 $music
#})

%% For hiding the metronome mark for the next tempo change
%% Usage example:
%% \mmHide \tempo "rit" 4=80
%% OR
%% \mmTrans \tempo 4=80
%% Use mmHide if you want the text to be visible, e.g for 
%% "rit." and "a tempo."  For things like
%% fermatas, mmTrans is better as is doesn't clutter the layout.
mmTrans = \once \override Score.MetronomeMark #'transparent = ##t
mmHide  = \once \set Score.tempoHideNote = ##t

%% For preprocessing include files ...
sysinc = 
#(define-music-function (p l cmd fname) (string? string?) 
   "Run system command, cmd, and redirect output to fname.
    then include fname in input"
    (system (string-concatenate (list cmd " > " fname)))
    #{ \include $fname #})

%{
    COMPLETION_BUFFER
%}
