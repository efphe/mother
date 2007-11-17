# file: eccez.py
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

"""
Mother Exceptions.
"""

class MotherException(Exception):

    def __init__(self, value):
        self.value= value

    def __str__(self):
        return self.value

class QueryError(MotherException):
    def __init__(self, value= ''):
        MotherException.__init__(self,
                    "Query error - %s" % value)

class ConnectionError(MotherException):
    def __init__(self, value= ''):
        MotherException.__init__(self,
                "Db connection re-established: old session is lost.")

class BrokenConnection(MotherException):
    def __init__(self, value= ''):
        MotherException.__init__(self,
                    "Broken Connection :(")

class InsertError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot insert - %s" % value)

class SelectError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot select - %s" % value)

class UpdateError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot update - %s " % value)

class DeleteError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Cannot delete - %s" % value)

class InternalError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self,
                    "Internal error - %s" % value)

class WrongTypeError(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self, str(value))
        
class InvalidFilter(MotherException):
    def __init__(self, value= ""):
        MotherException.__init__(self, str(value))
        
