#-----------------------------------------------------------
def mkiter(x):
    """ list -> list, el -> [el], None -> []

    Always returns an iterable.
    """
    return (x if hasattr( x, "__iter__" ) # list tuple ...
            else [] if x is None
            else [x])
#-----------------------------------------------------------
def mkitem(l):
    """ [el] -> el, [] -> None, list -> list

    Collapses single element items
    """
    if hasattr(l, "__iter__"):
        if len(l) == 0:
            return None
        elif len(l) == 1:
            x, = l
            return x
    return l
