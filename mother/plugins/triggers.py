# file: triggers.py
# This file is part of Mother: http://dbmother.org
#
# Copyright (c) 2007, Federico Tomassini aka efphe (effetom AT dbmother DOT org)
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

from mother.commons import MO_NOA, MO_DEL, MO_UP, MO_SAVE, MO_LOAD
from mother.commons import MO_BEFORE, MO_AFTER
from mother.commons import OKI_COL, ERR_COL

class MotherTrigger:

    def __init__(self):

        self.initTriggers()
        
    def _trigger_actions(self, flag):

        if flag == MO_UP: return self._update
        if flag == MO_DEL: return self._delete
        if flag == MO_SAVE: return self._insert
        if flag == MO_LOAD: return self._load
        self.log_int_raise("Invalid flag %s", ERR_COL(flag))

    def initTriggers(self):
        """ initTriggers() -> None

        Initialize triggers. 
        This is done automatically when calling addTrigger, so
        there is no need to call this function.\n"""

        self._triggers_map= {}
        t= self._triggers_map
            
        for flag in [MO_UP, MO_LOAD, MO_SAVE, MO_DEL]:
            t[flag]= {}
            for when in [MO_AFTER, MO_BEFORE]:
                t[flag][when]= []

        self.delete= self._trig_delete
        self.update= self._trig_update
        self.load= self._trig_load
        self.insert= self._trig_insert

    def _triggers_are_initialized(self):
        return hasattr(self, '_triggers_map')

    def get_triggers(self, flag, when):
        """ get_triggers(flag, when) -> list(functions)

        Returns triggers.
        """

        if not self._triggers_are_initialized():
            return []

        t= self._triggers_map
        try:
            d= t[flag]
        except:
            self.log_int_raise("get_trigger(): invalid flag %s.", ERR_COL(flag))

        try:
            l= d[when]
        except:
            self.log_int_raise("get_trigger(): invalid time %s.", ERR_COL(when))

        return l

    def get_flag_triggers(self, flag):
        """ get_flag_triggers(flag) -> list(functions)

        Returns triggers.
        """
        return  self.get_triggers(flag, MO_BEFORE) + \
                self.get_triggers(flag, MO_AFTER)

    def has_trigger(self, flag):
        """ has_trigger(flag) -> bool

        Is there a trigger for the flag `flag`?
        """
        if not self._triggers_are_initialized():
            return False

        return len(self.get_flag_triggers(flag)) > 0

    def add_trigger(self, flag, when, trigger):
        """ add_trigger(flag, when, f) --> None

        flag= MO_LOAD, MO_SAVE, MO_DEL, MO_UP
        when= MO_AFTER, MO_BEFORE

        f is the trigger: a python function
        """

        if not self._triggers_are_initialized():
            self.initTriggers()

        self._triggers_map[flag][when].append(trigger)

    def trigger(self, flag, when, *args):
        """ trigger(flag, when, *args) --> None

        flag= MO_LOAD, MO_SAVE, MO_DEL, MO_UP
        when= MO_AFTER, MO_BEFORE

        execute the tasked triggers for action flag and when
        """

        if not self._triggers_are_initialized():
            self.log_int_raise("Triggers are not initialized.")

        l= self.get_triggers(flag, when)

        if not l:
            return

        when_str= when == MO_AFTER and 'After' or 'Before'

        for f in l:
            f(*args)
            self.log_info("Trigger %s (%s-%s) Fired!", 
                    OKI_COL(f.func_name), when_str, self._mo_flags[flag])
            
    def _triggered_action(self, flag, *args):

        f= self._trigger_actions(flag)

        if not self._triggers_are_initialized() or \
           not self.get_flag_triggers(flag):
            res= f(*args)
        else:
            self._safeBeginTrans()
            try:
                self.trigger(flag, MO_BEFORE)
                res= f(*args)
                self.trigger(flag, MO_AFTER)

            except Exception, s:
                self._safeRollback()
                self.log_int_raise(str(s))

            self._safeCommit()

        self.log_info("Action %s.", OKI_COL("completed"))
        return res

    def _trig_delete(self):
        self._triggered_action(MO_DEL)

    def _trig_load(self, fields= None):
        self._triggered_action(MO_LOAD, fields)

    def _trig_update(self, updict= None):
        self._triggered_action(MO_UP, updict)

    def _trig_insert(self):
        self._triggered_action(MO_SAVE)
