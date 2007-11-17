# file: mocaster.py
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

""" Form And Fields Adaption

MotherCaster is a MotherPlugin that controls fields types and, 
optionally, required fields.

To use this plugin, you have to subclass your Mother class with 
MotherCaster and you have to define a dictionnary for fieds types.

Example:

  # Begin Code
  ClsStars(DbMother, MotherCaster):
      self.cast_fields = {star_mass: int}
      # and optionally:
      self.required_fields= ['star_age']

      def __init__(self, d, flag, session):
          MotherCaster.__init__(self, autocast= True)
          DbMother.__init__(self, d, flag, session)
  # End Code

Fields with wrong types are casted (if possible).
If you don't like that, turn off autocast.

The dict to initialize Mother must have all fields listed on 
required_fields (if specified).

On errors, a MoWrongFields is raised. 

  try:
    Sun= ClsStars(MyDict, MO_SAVE)
  except MoWrongFields, wrongs:
    print wrongs.ifields
    print wrongs.mfields

where wrong.ifields means invalid fields (not castable) and
wrong.mfields means missing fields (required but not present).

    """



class MoWrongFields(Exception):

    def __init__(self, ifields, mfields):
        self.ifields = ifields
        self.mfields = mfields

    def __str__(self):
        l= self.ifields + self.mfields
        return ','.join([str(k) for k in l])


class MotherCaster:

    def __init__(self, autocast= True):

        self._motherInitStore= self._initStore
        self._initStore= self._casterInitStore
        self._autocast= autocast

        if not hasattr(self, 'required_fields'):
            self.required_fields= []

    def _casterInitStore(self, store, flag):

        newstore= {}
        ifields= []

        for k, v in store.iteritems():

            if k not in self.fields:
                continue

            if k not in self.cast_fields:
                newstore[k]= v
                continue

            t= self.cast_fields[k]
            if not isinstance(v, t):

                if not self.autocast:
                    ifields.append(k)
                    continue

                try:
                    newv= t(v)
                except:
                    ifields.append(k)

            else:
                newv= v
            
            newstore[k]= newv

        mfields= set(self.required_fields) - set(newstore)

        if mfields or ifields:
            raise MoWrongFields(ifields, list(mfields))

        return self._motherInitStore(newstore, flag)


