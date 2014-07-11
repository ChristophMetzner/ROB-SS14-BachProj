import inspyred

from nevo.eval import fitness
from nevo.util.misc import mkiter,mkitem
from nevo.mutator.nu_mutation import nuMutation
from nevo import chromgen

def parse_callable(pconf, logger, sections, known_kwargs = None):
    """Returns the callable object or function defined in the specified section
    with the accumulated parsed_kwargs.

    evaluates the value of the "class" key and returns the callable together with
    any other parameters in a (callable, dictionary) tuple.
    The parsed_kwargs are not modified and will be returned together with any new
    key / eval(value) pairs in the specified section.
    Throws a RuntimeError if any arguments are in conflict.
    """
    callables = []
    if known_kwargs is None:
        parsed_kwargs = {}
    else:
        parsed_kwargs = dict(known_kwargs)
    for section in mkiter(sections):
        for item in pconf.cfg.items(section):
            try:
                value = eval(item[1])
            except:
                logger.exception("Error during evaluation")
                raise RuntimeError("Could not evaluate the expression '" + item[1]
                                   + "' for the callable '" + section + "'")
            if item[0] == "class":
                callables.append(value)
            elif item[0] in parsed_kwargs:
                if parsed_kwargs[item[0]] == eval(item[1]):
                    logger.warning("Redefined the option '" + item[0] + "' in the section '" + section
                                   + "' with the same value using the expression '"
                                   + item[1] + "'")
                else:
                    raise RuntimeError("Redefined the option '" + item[0] + "' in the section '" + section
                                       + "' with a different value using the expression '"
                                       + item[1] + "'"
                                       + ". Please remove the duplicate entry from your configuration.")
            else:
                parsed_kwargs[item[0]] = value
    return (mkitem(callables), parsed_kwargs)
