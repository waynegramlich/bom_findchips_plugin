from bom_manager import bom

class FindChips(bom.Panda):
    def __init__(self, tracing=None):
        # Verify argument types:
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>FindChips.__init__()")

        # Initialize the super class of the *FindChips* object (i.e. *self*):
        super().__init__("FindChips", tracing=next_tracing)

        # Perform any requested *tracing*:
        if tracing is not None:
            print(f"{tracing}<=FindChips.__init__()")

    def lookup(self, part_name, tracing=None):
        # Verify argument types:

        assert isinstance(part_name, str)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>FindChips.lookup(*, '{part_name}')")

        # Wrap up any requested *tracing* and return the *matches_list*
        matches_list = list()
        if tracing is not None:
            print(f"{tracing}<=FindChips.lookup(*, '{part_name}')=>[...]")
        return matches_list
        

def panda_get(tracing=None):
    # Verify argument types:
    assert isinstance(tracing, str) or tracing is None

    # Perform any requested *tracing*:
    next_tracing = None if tracing is None else tracing + " "
    if tracing is not None:
        print(f"{tracing}=>findchips.py:panda_get()")

    # Create the *find_chips* object:
    find_chips = FindChips(tracing=next_tracing)

    # Wrap up any requested *tracing* and return *find_chips*:
    if tracing is not None:
        print(f"{tracing}<=findchips.py:panda_get()=>*")
    return find_chips

