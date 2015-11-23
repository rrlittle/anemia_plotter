from numpy import ndarray

def prettify(obj, indent='  ',max_depth=10, max_indexes = 15, sort_keys=True, **kwargs):
    """
    Returns a well formatted string with \\n and \\t so that it looks good. 
    Takes a list-like, serializable object
    you can also specify the indent, it defaults to 2 spaces
        """
    line = ' '
    if('line' in kwargs): line = kwargs['line']
    cur_depth = 0
    if('cur_depth' in kwargs): cur_depth = kwargs['cur_depth']
    cur_index = 0
    if('cur_index' in kwargs): cur_index = kwargs['cur_index']

    if(cur_depth > max_depth): 
        return ''
    pretty = ''

    # if it's a list ....
    if(type(obj) is list or type(obj) is ndarray):
        pretty = '%s[\n' %line
        for i,x in enumerate(obj):
            pretty = pretty + prettify(x,   \
                indent = indent,                \
                sort_keys = sort_keys,          \
                line = line + indent,           \
                cur_depth = cur_depth + 1,      \
                max_depth = max_depth,          \
                cur_index = i,                  \
                max_indexes = max_indexes)      \



        pretty = pretty + '%s]\n' % line
    # if it's a dict...
    elif(type(obj) is dict):
        pretty = '%s{\n' % line
        keys = obj.keys()
        if(sort_keys): keys = sorted(obj.keys())
        for k in keys:
            pretty = pretty + '%s%s%s: \n' %(line,line, k)
            pretty = pretty + prettify(obj[k],  \
                indent = indent,                    \
                sort_keys = sort_keys,              \
                line = (line + indent),             \
                cur_depth = cur_depth + 1,          \
                max_depth = max_depth,              \
                max_indexes = max_indexes)          \


        pretty = pretty + '%s}\n' % line
    # otherwise it's content
    else:
        if max_indexes == -1 or cur_index < max_indexes:
            pretty = pretty + '%s' %line + obj.__repr__().replace('\n','%s\n') + '%s\n' % line
        elif cur_index == max_indexes:
            pretty = pretty + '%s...\n' % line

    # In any case return pretty 
    return pretty

def log_file(path,message = None, keep_alive = False, mode='w'):
    """ Writes a string to a file, optionally specify mode. 
            'r' reading
            'w' writing
            'a' append to the end
            'b' binary mode
            ... etc. look at doc for open for more options. 
        """
    f = open(path, mode)
    written = 0
    if(message):
        written = f.write(message)
    if(keep_alive):
        return f
    else:
        f.close()
        return written
