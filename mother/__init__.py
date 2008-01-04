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

""" 
Mother is a python module that hides SQL syntax and gives 
you a set of intelligent classes and methods. With `intelligent` 
we mean the capability of self-adaption, understanding various 
situations.
Mother could be considered as a Object Relational Mapper with a 
strong introspection. 
In fact, configuration files, tables, fields and keys declarations 
are not needed, because Mother knows the database structure herself.
Mother works with PostgreSQL and SQlite.
BSD License.
"""

__all__     = ['speaker', 'abdbda', 'commons', 'eccez', 'mothers']
__version__ = '0.6.4-r2'
__author__  = 'Federico Tomassini aka efphe'
__contact__ = 'Report Bugs and Ideas to efphe@freaknet.org '
__website__ = 'dbmother.org'
