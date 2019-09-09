"""Code is based on Python3.6 posixpath.py.
"""
import fnmatch
#: name separator
sep = "/"
empty = ""
dot = "."
dotdot = ".."
pardir = dotdot
curdir = dot

def match(name, pat):
    """Test whether FILENAME matches PATTERN.

    Patterns are Unix shell style:

    *       matches everything
    ?       matches any single character
    [seq]   matches any character in seq
    [!seq]  matches any char not in seq

    An initial period in FILENAME is not special.
    Both FILENAME and PATTERN are first case-normalized
    if the operating system requires it.
    If you don't want this, use fnmatchcase(FILENAME, PATTERN).
    """
    return fnmatch.fnmatch(name, pat)

def filter(names, pat):
    """Return the subset of the list NAMES that match PAT.
    """
    return fnmatch.filter(names, pat)

def matchcase(name, pat):
    """Test whether FILENAME matches PATTERN, including case.

    This is a version of fnmatch() which doesn't case-normalize
    its arguments.
    """
    return fnmatch.fnmatchcase(name, pat)

def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """
    return fnmatch.translate(pat)

def translate_longest_prefix(pat):
    """Translate a shell PATTERN to a regular expression
    that matches longest prefix of the path.

    For example the pattern  'A/B/C' would match
    'A', 'A/B' , 'A/B/C'
    as all are prefixes of the full match 'A/B/C'.
    
    However it would not match any path prefix
    that ends with '/' such as 'A/', or 'A/B/'
    as these paths are treated as incompleted.
    If you need to match such path you need to 
    rstrip() the '/' before matching.

    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    level = 0
    while i < n:
        c = pat[i]
        i = i+1
        if c == '/':
            level += 1
            res = res + '(/'
        elif c == '*':
            level += 1
            res = res + '(.*'
        elif c == '?':
            level += 1
            res = res + '(.'
        elif c == '[':
            has = False
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                if pat[j] == '/':
                    has = True
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                if has:
                    level += 1
                    res = '%s([%s]' % (res, stuff)
                else:
                    res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    for l in range(level):
        res = res + ')?'
    return r'(?s:%s)\Z' % res

# Normalize a path, e.g. A//B, A/./B and A/foo/../B all become A/B.
def normname(name):
    comps = name.split(sep)
    new_comps = []
    initial_slashes = name.startswith(sep)
    for comp in comps:
        if comp in (empty, dot):
            continue
        if (comp != dotdot or (not initial_slashes and not new_comps) or
             (new_comps and new_comps[-1] == dotdot)):
            new_comps.append(comp)
        elif new_comps:
            new_comps.pop()
    comps = new_comps
    name = sep.join(comps)
    if initial_slashes:
        name = sep * initial_slashes + name
    return name or dot

# Join pathnames.
# Ignore the previous parts if a part is absolute.
# Insert a '/' unless the first part is empty or already ends in '/'.
def join(a, *p):
    """Join two or more name components, inserting '/' as needed.
    If any component is an absolute name, all previous name components
    will be discarded.  An empty last part will result in a name that
    ends with a separator."""
    name = a
    if not p:
        name[:0] + sep
    for b in p:
        if b.startswith(sep):
            name = b
        elif not name or name.endswith(sep):
            name += b
        else:
            name += sep + b
    return name

def isabs(name):
    """Test whether a name is absolute.
    """
    return name.startswith(sep)

def absname(n, at):
    """Return an absolute name relative
    to the name specified in the `at`.
    """
    if not isabs(n):
        n = join(at, n)
    return normname(n)

# Return the tail (basename) part of a name, same as split(name)[1].
def basename(name):
    """Returns the final component of a name.
    """
    i = name.rfind(sep) + 1    
    return name[i:]

# Return the head (dirname) part of a name, same as split(name)[0].
def suitename(name):
    """Returns the directory component of a name.
    """
    i = name.rfind(sep) + 1
    head = name[:i]
    if head and head != sep * len(head):
        head = head.rstrip(sep)
    return head

def depth(name):
    """Return depth of the path.
    """
    return name.count(sep)

# Split a path in head (everything up to the last '/') and tail (the
# rest).  If the path ends in '/', tail will be empty.  If there is no
# '/' in the path, head  will be empty.
# Trailing '/'es are stripped from head unless it is the root.
def split(name):
    """Split a name.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty.
    """
    i = name.rfind(sep) + 1
    head, tail = name[:i], name[i:]
    if head and head != sep * len(head):
        head = head.rstrip(sep)
    return head, tail

def relname(name, at, start=None):
    """Return a relative version of a name
    relative to the `at`. 
    """
    if not name:
        raise ValueError("no name specified")

    if start is None:
        start = curdir

    start_list = [x for x in absname(start, at).split(sep) if x]
    name_list = [x for x in absname(name, at).split(sep) if x]
    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, name_list]))

    rel_list = [pardir] * (len(start_list)-i) + name_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)

# Return the longest prefix of all list elements.
def commonprefix(m):
    """Given a list of pathnames, returns the longest common leading component.
    """
    if not m: return ''
    # Some people pass in a list of pathname parts to operate in an OS-agnostic
    # fashion; don't try to translate in that case as that's an abuse of the
    # API and they are already doing what they need to be OS-agnostic and so
    # they most likely won't be using an os.PathLike object in the sublists.
    if not isinstance(m[0], (list, tuple)):
        m = tuple(m)
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1

# Return the longest common sub-path of the sequence of paths given as input.
# The paths are not normalized before comparing them (this is the
# responsibility of the caller). Any trailing separator is stripped from the
# returned path.
def commonname(names):
    """Given a sequence of names, returns the longest common sub-name.
    """
    if not names:
        raise ValueError('names is an empty sequence')


    split_names = [name.split(sep) for name in names]

    try:
        isabs, = set(n[:1] == sep for n in names)
    except ValueError:
        raise ValueError("can't mix absolute and relative names") from None

    split_names = [[c for c in s if c and c != curdir] for s in split_names]
    s1 = min(split_names)
    s2 = max(split_names)
    common = s1
    for i, c in enumerate(s1):
        if c != s2[i]:
            common = s1[:i]
            break

    prefix = sep if isabs else sep[:0]
    return prefix + sep.join(common)
