TransLily
=========

A minimalist assistant for transcribing vocal and instrumental parts in
LilyPond notation.
          

TransLily Documentation (version 0.1)

All of the following topics are in the online help in the program


LICENSE  
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


INTRODUCTION  
TransLily is a transcription assistant for LilyPond. It's optimized for the
task of transcribing multiple parts from existing paper scores to produce
individual part sheets. Transcribing parts can be a laborious process,
especially if the music contains many articulations, dynamic markings, and
other performance indications. 

TransLily reduces the labor by making it easier to exploit the repetitive
aspects found in almost all music. Perhaps the most important feature in this
regard is separating pitch indications from rhythm + markup.  This makes it
possible to paste from one voice to another and rapidly change only the
pitches. Much music, especially choral music, is homophonic with 4 or more
parts singing identical lyrics and rhythms in harmony. TransLily greatly speeds
up the entry process for such music.

TransLily can also help with polyphonic music.  Polyphony is, more often than
not, imitative from voice to voice with entrances spaced apart by one or more
bars. TransLily's 'paste' command lets you copy from from a range of measures
in one voice to a different range of measures in another voice and the alter to
pitches as needed.  




USAGE      
TransLily is a command-line program written in Python. You need to have
working installations of Python (2.6 or later) and LilyPond (2.18 or later).
You should be able to type 'python' at a command line and get the usual Python
shell. Similarly, you should be able to type 'lilypond' to run the LilyPond
program.  For advanced use, you'll want to have a $EDITOR environment variable
set to invoke a non-forking text editor, e.g $EDITOR="gvim -f" or similar.

The present version of TransLily does not have an installer or setup program.
Installation consists of unzipping the TransLily archive in any convenient
location in your file system.  To start the program,  cd to the translily
directory and run it with either

    python translily.py  <projectname>

    or
    
    ./translily.py <projectname>

where <projectname> is the path to the folder where you want to keep your work
for a particular transcription project.  I usually name the project folder for
the piece I'm transcribing, e.g. 

    ./translily StarSpangledBanner

If the folder doesn't exist, it will be created and TransLily will prompt you
for the title, composer, poet, and transcriber for the piece before offering a
command prompt (Cmd), as shown below

    python translily.py StarSpangledBanner
    No current file!
    Starting from scratch ...
    poet :Francis Scott Key
    transcriber :Mike Ellis
    composer :John Stafford Smith
    title :The Star-Spangled Banner
    Saved 0.json
    (Cmd) 

If the folder already exists, TransLily will let you know there's prior work
and resume where you last left off, e.g.

    python translily.py StarSpangledBanner
    Loaded 0.json
    Found prior work:
      structure : 1 bars
    (Cmd)

At this point, you're ready enter and compile music.  See the help pages for
the 'a' (append), 'c' (compile) and 'e' (edit) commands to get started with the
three commands you'll use most often.

TransLily's help pages are always available by typing 'help' at any command prompt.      



TIPS AND SHORTCUTS:

    1. You can enter LilyPond code for pitches/rhythms/lyrics on multiple
       lines, but this is rarely needed. Entering a blank line terminates the
       input and moves to the prompt for the next item.

    2. Hitting Return at a (Cmd) prompt will re-execute the last command. This
       provides a convenient workflow for appending a series of measures to a
       voice without having to retype the 'a voice' command.

    3. Entering a blank line (or a line ending with 'm') at the pitches prompt
       (i.e. no pitches) is a shortcut for inserting a full measure rest and no
       lyrics.  You can use this feature to rapidly enter a series of rest
       measures by repeatedly hitting Return.

    4. TAB Completion:  Enter the first few characters of a notation line
       you've previously entered and hit the Tab key.  If only one entry
       matches, Translily will complete the line for you. If more than entry
       matches, TransLily will show you a list of possible matches. Enter more
       characters and hit Tab again to reduce the list.  This can be a huge
       timesaver for complicated rhythmic expressions that appear multiple
       times in a composition.

    5. History:  Use the up/down arrow keys to scroll through recent entries. 
       Very useful for entering measures with the same pitches, rhythms, or
       words as prior measures. History and Tab Completion are both
       context-sensitive, i.e. you'll only see pitches at the "pitches' prompt,
       rhythms at the 'rhythms' prompt, and so on.

Advanced usage:

    These are features of interest to shell wizards. They're not necessary for
    normal usage.

    1. The command processor uses readline by default and will inherit whatever
       keymaps you've defined in your .inputrc file.
    2. If your $EDITOR environment variables is set to a suitable non-forking
       text editor, you can escape to the editor when entering pitches,
       rhythms, or lyrics by typing '%%' at the end of an input line. This is
       an alternative to using whatever keymap you'd normally use for this
       purpose as Python doesn't support this correctly on all platforms.


VITAL INFORMATION

To work successfully with TransLily, you *really* need to understand the following:

1. TransLily notation is pure LilyPond syntax with one exception:
    The @ Hack: 
    Put an '@' sign in from of any numbers that aren't note durations, e.g.
        \time @4/4
        \tempo @2=96

    Why: At compile time, TransLily needs to match pitches with their
    respective durations. The '@' hack allows TransLily to distinguish which
    tokens that start with numbers are really durations and which are arguments
    to LilyPond functions without having to maintain a detailed representation
    of the syntax for all LilyPond functions.  There are many, many more note
    events than function calls in most LilyPond files, so this is not a large
    burden during notation entry. The '@'s are stripped out after the
    pitch/duration merging operations.

2.  Know what goes where:
    Pitches: 
    When prompted for a bar's pitches, enter ONLY the pitches and nothing else.
    A pitch may include alterationss, octave change, forced accidentals, and
    octave checks, e.g.  "aqs,!='" as per the LilyPond docs.  Most of the time
    you'll be entering simply the pitch names, e.g.  "a b c d" for a measure
    containing 4 pitches.

    Rhythms: 
    When prompted for rhythms, enter the durations plus articulations, slurs,
    dynamics, etc that go with the pitches, e.g.  "4.\< 8 4( 4)\!".   You can
    enter directives like \tempo and \key but some of these ought to be put in
    the 'structure' voice discussed below.

    Lyrics:
    Enter lyrics when prompted using the normal LilyPond rules for syllable
    breaks, etc, e.g. "Hel -- lo World! __"

3.  Structure
    TransLily includes a special voice named 'structure' in every project.
    Structure is the place to enter tempos, time signatures, rehearsal marks,
    and volta repeats, ... i.e. things that are common to all voices.
    Otherwise, structure consist full measure spacer rests.  Structure acts as
    a sort of template for all the voices.

    The main reason for keeping structural items in a separate voice is to
    facilitate pasting notation across voices.  The paste command allows you to
    paste a segment of measures from one voice into a different segment of
    another voice. Keeping non-notational elements in the structure voice
    reduces the chance of creating a conflict between voices that LilyPond
    can't resolve.

4.  MIDI output: 
    Translily automatically produces a MIDI file when you compile a voice.
    These files are useful for 'proof-listening' and/or as plunk tracks for
    learning parts. A difficulty arises when your transcription requires use of
    the LilyPond '\repeat volta' construct to produce repeats in the music.
    Due to a LilyPond limitation, your score will be displayed correctly, but
    the repeats will not be executed in the MIDI file unless you transcribe the
    '\repeat volta' syntax from the 'structure' voice into each voice and into
    the metronome voice as well (if it exists).

5.  Metronome: You may optionally create a voice named 'metronome' to produce a
    click-track in the midi output. Just do 'n metronome' to get started.
    TransLily defines patterns for most common time signatures.  You can
    automatically insert these patterns in the metronome entering a blank line
    when prompted for 'pitches' during appending or editing operations. This
    differs from the editing behavior in other voices where blank pitch lines
    create a full measure rest in the current time signature.  Otherwise, all
    editing commands work the same with the metronome voice as with any other
    voice.

    The metronome voice is a percussion voice. You must use valid LilyPond
    percussion insrtument names in the 'pitches' line instead of pitch names.
    The default patterns use 'wbh' (High Wood Block) and 'wbl' (Low Wood
    Block), but if you may specify other percussion instruments according to
    your preferences. 
    
6. Watch out for auto-repeats when editing!: 
    The Python Cmd module includes, by default, a handler that automatically
    repeats the previous command when you enter a blank line at a (Cmd) prompt.
    This is very handy for things like appending several bars of rests, but can
    lead to confusion if you forget to stop hitting Return at the appropriate
    point. If this bites you, remember that the 'u' (undo) command is your friend.





AUTO SAVE  
TransLily automatically saves your work after each successful change to any
bar.  You can use the 'u' (undo) and 'r' (redo) to walk back and forth in the
revision history.  When you restart TransLily after quitting a project, the
most recent revision will be reloaded.

Caveat: If you undo several steps and then make a change, the newest revision
will be based on the revision you accessed by undoing.  This is normally not a
problem, but you should be aware that 'undo' moves back by the files'
timestamps without any concept of branching.  To make this more concrete,
suppose you're at revision 103.json and undo 3 times, thereby reloading version
100.json. If you then make a change, the new version will be 104.json.  Now if
you hit 'u', you'll be reverted to 103.json which may not be what you want.
You'll need to hit 'u' 3 more times to get back to 100.json.



COMMAND SUMMARY

    * 'a voice' to append,
    * 'b' to show bar counts for each voice,
    * 'c voice' to compile,
    * 'd voice firstbar lastbar' delete range of bars,
    * 'e voice firstbar  lastbar' to edit,
    * 'help cmds' to show this summary,
    * 'i voice firstbar lastbar' insert a range of bars,
    * 'n newvoice' to add a new voice,
    * 'p fromvoice firstbar lastbar tovoice startbar' to paste,
    * 't _top|_bottom body|items' to edit template info (ADVANCED),
    * 'r' to redo, i.e undo the last undo,
    * 'u' to undo last command,
    * 'v voice firstbar lastbar' to view a range of bars,
    * 'q' to quit.



APPEND  
The 'a voice' (append) command adds one bar of music to the specified voice. If
the voice doesn't exist, you'll be asked if you want to create it.  Answer
'y' to create the voice.  In the example below, a new voice is created and the
first bar of pitches, rhythm, and lyrics are added.

    (Cmd) a bass2
    bass2 pitches: bar 1

    c d e f

    ok
    bass2 rhythm: bar 1

    4 4 4 4

    ok
    bass2 lyrics: bar 1

    Here's Trans -- Lil -- y!

    ok
    Saved 4.json
    (Cmd) 

In the example above, the program prompted us to enter 

    Pitches : Enter valid Lilypond pitch names including modifiers. There
    should be one pitch for each note in the bar, separated by one or more
    spaces. The default pitch symbol set is English and/or Chromatic Fixed Do
    solfege. If you prefer symbols from another lanaguage,  you can do so by
    modifying the '_top' template in config.py.

    Rhythm : Enter the durations for each note plus dynamics, articulations,
    and any other valid LilyPond notations for the bar.

    Lyrics:  Enter the words and syllables that go with the notes in the bar.
    The normal LilyPond conventions for lyric entry applly.

After  the program printed 'Saved 4.json' to let us
know that the score had been saved with the new empty voice added. 


BARCOUNTS  
The 'b' (barcount) command prints a list of all voices in the project and
the number of measures contained in each, e.g.

    (Cmd) b
      sop2 : 39 bars
      tenor2 : 39 bars
      soprano1 : 39 bars
      tenor1 : 39 bars
      bass2 : 39 bars
      alt1 : 39 bars
      bass1 : 39 bars
      alt2 : 39 bars
      structure : 39 bars
    (Cmd)  



COMPILE  
The 'c voice' (compile) command merges the pitches, rhythms and lyrics from the
specified voice into a well-formatted LilyPond file. The file is then processed
by the LilyPond compiler to produce a PDF score and MIDI file containing the
voice plus metronome clicks synchronized to the meter(s) in the music.  

The output files are saved in the project folder and named by appending the
voice name to the folder name, e.g.

    StarSpangledBanner_bass1.ly
    StarSpangledBanner_bass1.pdf
    StarSpangledBanner_bass1.midi

During compilation the LilyPond compiler messages are displayed to provide
feedback on the compilation. Successful compilation will look similar to the
following:


    (Cmd) c bass1
    -o /Users/mellis/Desktop/translily/StarSpangledBanner/StarSpangledBanner_bass1
    GNU LilyPond 2.18.2
    Changing working directory to: `/Users/mellis/Desktop/translily/StarSpangledBanner'
    Processing `/Users/mellis/Desktop/translily/StarSpangledBanner/StarSpangledBanner_bass1.ly'
    Parsing...
    Interpreting music...[8][16][24][32][40]
    Preprocessing graphical objects...
    Interpreting music...
    MIDI output to `StarSpangledBanner_bass1.midi'...
    Finding the ideal number of pages...
    Fitting music on 1 page...
    Drawing systems...
    Layout output to `StarSpangledBanner_bass1.ps'...
    Converting to `./StarSpangledBanner_bass1.pdf'...
    Success: compilation successfully completed
    (Cmd)

Unsuccessful compilations will contain LilyPond error messages that can be used
to find where the music entry went wrong.

At the end of compilation, TransLily will open your .pdf file for viewing in
whatever application is assigned to the '.pdf' extension.  This feature is
currently enabled only for Apple OS X.



DELETE  
The 'd voice firstbar lastbar' (delete) command removes a range of bars from
firstbar to lastbar, inclusive, from the specified voice. If the deletion
removes all bars in the voice, the voice itself is also deleted, as illustrated
in the example below.  

    (Cmd) b
      bass2 : 2 bars
      structure : 1 bars
      bass1 : 2 bars
    (Cmd) d bass2 1 2
    deleted bass2 1 thru 2
    deleted empty voice bass2
    Saved 7.json
    (Cmd) b
      structure : 1 bars
      bass1 : 2 bars
    (Cmd)


EDIT  
The 'e voice firstbar lastbar' (edit) command prompts you to edit the
pitches/rhythms/lyrics/ in each bar from firstbar to lastbar inclusive.  You
can keep the current contents of any item by hitting return without making any
changes.  A new version of the files is saved with each bar edited.  This
allows the undo/redo commands to walk back the history bar by bar.

Here's an example session editing 3 bars in the tenor2 part.

    (Cmd) e tenor2 26 28
    tenor2 pitches: bar 26

    bf, bf a
    ok
    tenor2 rhythm: bar 26

    2 4 4
    ok
    tenor2 lyrics: bar 26

    say does that
    ok
    Saved 415.json
    tenor2 pitches: bar 27

    g g g
    ok
    tenor2 rhythm: bar 27

    2 4 4
    ok
    tenor2 lyrics: bar 27

    Star Spang -- led
    ok
    Saved 416.json
    tenor2 pitches: bar 28

    c c bf c e
    ok
    tenor2 rhythm: bar 28

    2 8(\< 8) 8( 8)
    ok
    tenor2 lyrics: bar 28

    Ban -- ner yet
    ok
    Saved 417.json
    (Cmd) 

Note: Be careful not to hit an extra Return at the end of the edit for the
last bar. Otherwise, the automatic 'redo the last command' feature will walk
you through the edit all over again!  



INSERT RESTS  
The 'i voice firstbar lastbar' inserts new measures in the specified voice and
fills them with full-measure rests according to the most recent prior time
signature in 'structure'.  The newly inserted measures become firstbar thru
lastbar, inclusive. Prior measure numbers are unaffected and succeeding measure
numbers are shifted forward beginning with 1 + lastbar, as illustrated in the
example below.

(Cmd) b
  structure : 1 bars
  bass1 : 2 bars
(Cmd) i structure 2 3
Saved 4.json
(Cmd) b
  structure : 3 bars
  bass1 : 2 bars
(Cmd) v structure 1 3
structure bar 1:
r
\time @4/4 1

structure bar 2:
r
1*4/4

structure bar 3:
r
1*4/4



NEW  
The 'n voice' (new) command adds a new voice.   In the example below, a new voice is created and the
first bar of pitches, rhythm, and lyrics are added.

    (Cmd) n bass2
    Adding voice bass2
    name (e.g. Bass I) :Bass II
    abbr (e.g. B1) :B2
    rel (e.g. c) :c
    clef (e.g. bass) :bass
    has_lyrics (y/n) :y
    Saved 3.json
    bass2 added.
    bass2 pitches: bar 1

    c d e f

    ok
    bass2 rhythm: bar 1

    4 4 4 4

    ok
    bass2 lyrics: bar 1

    Here's Trans -- Lil -- y!

    ok
    Saved 4.json
    (Cmd) 

In the example above, the program prompted us to enter 

    1. Voice name (name) -- This is the formal name that will be printed in the
       score at the start of the first stave.

    2. Abbreviation, (abbr) -- This is the short name that appears before staves 
       after the first.

    3. Relative pitch (rel) -- This gets supplied to a LilyPond \relative directive.

    4. Lyrics flag (has_lyrics) -- Answer 'y' for choral voices, 'n' for instruments.

After the voice was created, the program printed 'Saved 3.json' to let us
know that the score had been saved with the new empty voice added. 

Finally, the program prompted for pitches, rhythms, and lyrics for the first
bar and saved again before returning to the (Cmd) prompt to await the next
command.

*See Also* The Tips and Shortcuts documented with the 'a voice' (append) command.



PASTE  
The  'p fromvoice firstbar lastbar tovoice startbar' (paste) command copies a
range of bars in 'fromvoice' to a range of bars in 'tovoice'. The range
'firstbar lastbar' includes both endpoints and both must exist in 'fromvoice'.
The initial bar 'startbar' must exist in 'tovoice', but the command will extend
'tovoice' as needed to hold the entire range being copied.  This is a pure copy
operation, i.e. the content of 'fromvoice' is unchanged.

The example below copies 4 bars (mm 17-20) from bass1 to mm 21-24 in alto2 and
saves the result.

    (Cmd) p bass1 17 20 alto2 21
    Saved 44.json
    (Cmd) 



PLAY  
The 'play voice' command will play the most recently compiled midi file for the
specified voice. The play command uses whatever midi player application is
currently mapped to the '.midi' file type. This command is currently supported
only for Apple Mac OS X.


QUIT  
The 'q' (quit) command exits TransLily. It is synonymous with 'EOF' and Ctrl-D.


REDO  
The 'r' (redo) command undoes the previous 'undo', if any.


TEMPLATE  
(ADVANCED) The 't _top|_bottom  body|items' (template) command allows you to
edit either of the templates, _top or _bottom, that TransLily emits during
compilation as part of the .ly file that goes to the LilyPond compiler. 

There are only 3 variants of the 't' command. The first, shown below, allows
you to edit title, poet, composer, and transcriber for the piece, e.g. 

    (Cmd) t _top items
    poet :Francis Scott Key
    transcriber :Mike Ellis
    composer :John Stafford Smith
    title :The Star-Spangled Banner
    Saved 45.json
    (Cmd) 

There is no corresponding 'items' member for the _bottom template.  It contains
the LilyPond \score block and the substitutions at compile time are based on
the name of the voice being compiled.

    (Cmd) t _bottom items
    _bottom has no items to edit
    (Cmd)


The next 2 variants allow you to edit the template body texts for _top or
_bottom.  Because both of these items are somewhat lengthy chunks of LilyPond
code, these commands attempt to open whatever external text editor you have
configured in your EDITOR environment variable.  There is currently no
alternative scheme in TransLily for editing the templates in-line.


    (Cmd) t _top body
    <... editor opens ...>
    Saved 46.json

    (Cmd) t _bottom body
    <... editor opens ...>
    Saved 47.json


Before attempting to use these commands you should study the config.py file to
understand how Python Template susbtitution is used in Translily. 

Note that using the 't' command changes the templates only for the project
being edited.  To change the templates for all (future) projects, you should
make a copy of config.py, edit the copy, and save it as '_config.py'. Translily
tries to import '_config.py' before falling back to 'config.py'. 



UNDO    
The 'u' (undo) command loads the last previous version of the project. Project
versions are saved as .json files in the project's json/ subdirectory.  There
is a complementary 'r' (redo) command that reloads newer versions in reverse
order.  See the 'autosave' topic for more information.


VIEW  
The 'v voice firstbar lastbar' (view) command prints the pitch/rhythm/lyric
tokens you've entered for the specified voice and bar numbers. The same
information is provided for the preceding and following bars to assist in
locating LilyPond syntax problems, e.g.

    (Cmd) v tenor2 26 28
    tenor2 bar 26:
    bf, bf a
    2 4 4
    say does that

    tenor2 bar 27:
    g g g
    2 4 4
    Star Spang -- led

    tenor2 bar 28:
    c c bf c e
    2 8(\< 8) 8( 8)
    Ban -- ner yet

    (Cmd) 

CONTACT: Michael Ellis, <michael DOT f DOT ellis AT gmail DOT com>
