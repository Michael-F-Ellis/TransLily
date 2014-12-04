"""
Miscellaneous functions and decorators.
"""
import os
import re
def advance_generator_once(original_fn):
    """
    From Ian Ward's blog article at http://excess.org/article/2013/02/itergen2/

    The flow is always the same when working with generators.

    1. a generator object is created by the caller
    2. the caller starts the generator
    3. the generator passes data to the caller (or signals the end of the sequence)
    4. the caller passes data to the generator
    5. repeat from (3)

    For generators that are driven by input to .send() no data is transferred
    in the first 3 steps above.

    This is a decorator that arranges for .next() to be called once immediately
    after a generator is created. This will turn a generator function into a
    function that returns a generator immediately ready to receive data (step 4).
    """
    def actual_call(*args, **kwargs):
        """ Function wrapper """
        gen = original_fn(*args, **kwargs)
        assert gen.next() is None
        return gen
    return actual_call

def external_edit(initial=""):
    """
    Fire up an external editor with initial text
    and return result of users editing.

    Returns None if no editor is available or if user
    kills editing.

    Cribbed from http://stackoverflow.com/a/2581571/426853
    and modified to use $EDITOR from environment.
    """
    from tempfile import NamedTemporaryFile

    editor = os.getenv('EDITOR')
    if editor is None:
        print "You need to set your 'EDITOR' environment variable!"
        return None

    # Create the initial temporary file.
    with NamedTemporaryFile(delete=False) as tf:
        tfName = tf.name
        tf.write(initial)

    # Fire up the editor.
    #print editor, tfName
    if os.system(editor + ' ' + tfName) != 0:    
        return None # Editor died or was killed.

    # Get the modified content.
    with open(tfName) as tf:
        result = tf.readlines()
        os.remove(tfName)
    
    return "".join(result)

def uniq(seq, stripit=True):
    """ 
    Return a unique list from seq with elements ordereed by first appearance
    >>> uniq(['z', 'c', 'z', 'a'])
    ['z', 'c', 'a']

    >>> uniq([])
    []
    """
    seq = [s.strip() for s in seq] if stripit == True else seq
    seqset = set(seq)
    ordered = []
    for k in seq:
        try:
            seqset.remove(k)
            ordered.append(k)
        except KeyError:
            if len(seqset) == 0:
                break

    return ordered

def uniqify(filename, final_newline=True):
    """ 
    Apply uniq() in place to file. 
    Raises IOError if file does not exist.
    """

    with file(filename, 'r') as f:
        ulines = uniq(f.readlines())
    
    with file(filename, 'w') as f:
        print >> f, "\n".join(ulines) ,
        if final_newline:
            print >> f
        
    return ulines


def lilysafe_name(name):
    """
    Create a valid variable name for use in LilyPond files.
    Convert numbers to strings and remove other non-alpha chars.
    >>> lilysafe_name('Bass 1')
    'BassOne'
    """
    numnames = "Zero One Two Three Four Five Six Seven Eight Nine".split(' ') 
    # Don't complain about string module. pylint: disable=W0402
    from string import letters, digits
    def safechar(c):
        """ Convert one char to a safe string """
        if c in letters:
            return str(c)
        elif c in digits:
            return numnames[int(c)]
        else:
            return ""
    return ''.join([safechar(c) for c in name])    



def gather_token_sequences(masterptn, target):
    """
    Find all sequences in 'target' of two or more identical adjacent tokens
    that match 'masterptn'.  Count the number of tokens in each sequence.
    Return a new version of 'target' with each sequence replaced by one token
    suffixed with '*N' where N is the count of tokens in the sequence.
    Whitespace in the input is preserved (except where consumed within replaced
    sequences).

    >>> mptn = r'ab\w'
    >>> tgt = 'foo abc abc'
    >>> gather_token_sequences(mptn, tgt)
    'foo abc*2'

    >>> tgt = 'abc abc '
    >>> gather_token_sequences(mptn, tgt)
    'abc*2 '

    >>> tgt = '\\nabc\\nabc abc\\ndef\\nxyz abx\\nabx\\nxxx abc'
    >>> gather_token_sequences(mptn, tgt)
    '\\nabc*3\\ndef\\nxyz abx*2\\nxxx abc'
    """

    # Emulate python's strip() function except that the leading and trailing
    # whitespace are captured for final output. This guarantees that the
    # body of the remaining string will start and end with a token, which
    # slightly simplifies the subsequent matching loops.
    stripped = re.match(r'^(\s*)(\S.*\S)(\s*)$', target, flags=re.DOTALL)
    head, body, tail = stripped.groups()

    # Init the result list and loop variables.
    result = [head]
    i = 0
    token = None
    while i < len(body):
        ## try to match master pattern
        match = re.match(masterptn, body[i:])
        if match is None:
            ## Append char and advance.
            result += body[i]
            i += 1

        else:
            ## Start new token sequence
            token = match.group(0)
            esc = re.escape(token) # might have special chars in token
            ptn = r"((?:{}\s+)+{})".format(esc, esc)
            seq = re.match(ptn, body[i:])
            if seq is None: # token is not repeated.
                result.append(token)
                i += len(token)
            else:
                seqstring = seq.group(0)
                replacement = "{}*{}".format(token, seqstring.count(token))
                result.append(replacement)
                i += len(seq.group(0))


    result.append(tail)
    return ''.join(result)

if __name__ == '__main__':
    from doctest import testmod
    testmod()

