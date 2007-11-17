from mother.speaker import RED as ERR_COL
from mother.speaker import GREEN as OKI_COL
from mother.speaker import YELLOW as INF_COL

#
## MoThEr: init flags.
#

MO_NOA    = 0     # No Action
MO_DEL    = 1     # Del Action
MO_UP     = 2     # Update Action
MO_SAVE   = 3     # Save Action
MO_LOAD   = 4     # Load Action

MO_BEFORE = 0     # Before?!?
MO_AFTER  = 1     # After?!?

def MotherNaming(s, pref=None):
    """ MotherNaming(s[,pref=None]) -- > string

    return the CaMeLeD s. If prefix is not None, 
    return pref+CaMeLeD.
    """
    l=s.split("_")
    l=["%s%s" % (i[0].upper(),i[1:]) for i in l]
    return (pref or "") + "".join(l)
