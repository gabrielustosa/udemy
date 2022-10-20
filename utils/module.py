def import_name(modulename, name):
    """ Import a named object from a module in the context of this function.
    """
    try:
        module = __import__(modulename, globals(), locals(), [name])
    except ImportError:
        return None
    try:
        function = vars(module)[name]
        return function
    except KeyError:
        return None
