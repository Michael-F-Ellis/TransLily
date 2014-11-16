"""
Miscellaneous functions and decorators.
"""
import os
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

if __name__ == '__main__':
    from doctest import testmod
    testmod()

