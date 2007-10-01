from speaker import RED as ERR_COL
from speaker import GREEN as OKI_COL
from speaker import YELLOW as INF_COL

def MotherNaming(s, pref=None):
    """ MotherNaming(s[,pref=None]) -- > string

    return the CaMeLeD s. If prefix is not None, 
    return pref+CaMeLeD.
    """
    l=s.split("_")
    l=["%s%s" % (i[0].upper(),i[1:]) for i in l]
    return (pref or "") + "".join(l)
