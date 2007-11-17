# file: commons.py
# This file is part of Mother: http://dbmother.org
#
# Copyright (c) 2007, Federico Tomassini aka efphe (effetom AT gmail DOT com)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the University of California, Berkeley nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS

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
