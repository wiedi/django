import re
import urllib
from email.Utils import formatdate

from django.utils.encoding import smart_str, force_unicode
from django.utils.functional import allow_lazy

ETAG_MATCH = re.compile(r'(?:W/)?"((?:\\.|[^"])*)"')

def urlquote(url, safe='/'):
    """
    A version of Python's urllib.quote() function that can operate on unicode
    strings. The url is first UTF-8 encoded before quoting. The returned string
    can safely be used as part of an argument to a subsequent iri_to_uri() call
    without double-quoting occurring.
    """
    return force_unicode(urllib.quote(smart_str(url), safe))

urlquote = allow_lazy(urlquote, unicode)

def urlquote_plus(url, safe=''):
    """
    A version of Python's urllib.quote_plus() function that can operate on
    unicode strings. The url is first UTF-8 encoded before quoting. The
    returned string can safely be used as part of an argument to a subsequent
    iri_to_uri() call without double-quoting occurring.
    """
    return force_unicode(urllib.quote_plus(smart_str(url), safe))
urlquote_plus = allow_lazy(urlquote_plus, unicode)

def urlencode(query, doseq=0):
    """
    A version of Python's urllib.urlencode() function that can operate on
    unicode strings. The parameters are first case to UTF-8 encoded strings and
    then encoded as per normal.
    """
    if hasattr(query, 'items'):
        query = query.items()
    return urllib.urlencode(
        [(smart_str(k),
         isinstance(v, (list,tuple)) and [smart_str(i) for i in v] or smart_str(v))
            for k, v in query],
        doseq)

def cookie_date(epoch_seconds=None):
    """
    Formats the time to ensure compatibility with Netscape's cookie standard.

    Accepts a floating point number expressed in seconds since the epoch, in
    UTC - such as that outputted by time.time(). If set to None, defaults to
    the current time.

    Outputs a string in the format 'Wdy, DD-Mon-YYYY HH:MM:SS GMT'.
    """
    rfcdate = formatdate(epoch_seconds)
    return '%s-%s-%s GMT' % (rfcdate[:7], rfcdate[8:11], rfcdate[12:25])

def http_date(epoch_seconds=None):
    """
    Formats the time to match the RFC1123 date format as specified by HTTP
    RFC2616 section 3.3.1.

    Accepts a floating point number expressed in seconds since the epoch, in
    UTC - such as that outputted by time.time(). If set to None, defaults to
    the current time.

    Outputs a string in the format 'Wdy, DD Mon YYYY HH:MM:SS GMT'.
    """
    rfcdate = formatdate(epoch_seconds)
    return '%s GMT' % rfcdate[:25]

# Base 36 functions: useful for generating compact URLs

def base36_to_int(s):
    """
    Convertd a base 36 string to an integer
    """
    return int(s, 36)

def int_to_base36(i):
    """
    Converts an integer to a base36 string
    """
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    factor = 0
    # Find starting factor
    while True:
        factor += 1
        if i < 36 ** factor:
            factor -= 1
            break
    base36 = []
    # Construct base36 representation
    while factor >= 0:
        j = 36 ** factor
        base36.append(digits[i / j])
        i = i % j
        factor -= 1
    return ''.join(base36)

def parse_etags(etag_str):
    """
    Parses a string with one or several etags passed in If-None-Match and
    If-Match headers by the rules in RFC 2616. Returns a list of etags
    without surrounding double quotes (") and unescaped from \<CHAR>.
    """
    etags = ETAG_MATCH.findall(etag_str)
    if not etags:
        # etag_str has wrong format, treat it as an opaque string then
        return [etag_str]
    etags = [e.decode('string_escape') for e in etags]
    return etags

def quote_etag(etag):
    """
    Wraps a string in double quotes escaping contents as necesary.
    """
    return '"%s"' % etag.replace('\\', '\\\\').replace('"', '\\"')

def ip6_normalize(addr):
     """
     Normalize an IPv6 address to allow easy regexp validation
     mostly checks the length, and gets ride of tricky things
     like IPv4 mapped addresses and :: shortcuts
     
     Outputs a string
     """
     # Some basic error checking
     if addr.count('::') > 2 or ':::' in addr:
         raise ValueError
 
     ip = addr.split(':')
     nbfull = len([elem for elem in ip if elem != ''])
     nb = len(ip)
 
     if nbfull >= 1 and '.' in ip[-1]:
         # Convert IPv4 mapped addresses to full hexa
         ipv4 = ip[-1].split('.')
         hex1 = (int(ipv4[0]) << 8) + int(ipv4[1])
         hex2 = (int(ipv4[2]) << 8) + int(ipv4[3])
         ip[-1:] = [hex(hex1)[2:], hex(hex2)[2:]]
         nbfull = nbfull + 1
         nb = nb + 1
 
     if nbfull == 8 or nbfull == nb:
         # No need to bother
         return addr
     elif nbfull > 8:
         # Has to be invalid anyway
         raise ValueError
 
     # Begin normalization
     start, end, index = (None, None, 0)
     for elem in ip:
         if elem == '':
             if start is None:
                 start = index
                 end = index
             else:
                 end = index
         index += 1
     pad = 8 - nbfull
     if end != start:
         ip[start:end-start+1] = ['0'] * pad
     else:
         ip[start] = '0'
         if pad > 1:
             ip[start:1] = ['0'] * (pad - 1)
     return ':'.join([item for item in ip if len(item) > 0])



