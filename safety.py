import string

VALID_CHARS = frozenset("-_.() %s%s" % (string.ascii_letters, string.digits))

def slugify(s):
    return ''.join(c for c in s if c in VALID_CHARS)

