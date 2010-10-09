# file: speaker.py
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

import logging
_fmt_log= logging.Formatter('%(asctime)s: %(message)s', datefmt= '%h %d %H:%M:%S')



"""
The Mother logger: Speaker.
"""

# From Syslog: facilities
LOG_KERN= 0
LOG_USER= 8
LOG_MAIL= 16
LOG_DAEMON= 24
LOG_AUTH= 32
LOG_LPR= 48
LOG_NEWS= 56
LOG_UUCP= 64
LOG_CRON= 72
LOG_LOCAL0= 128
LOG_LOCAL1= 136
LOG_LOCAL2= 144
LOG_LOCAL3= 152
LOG_LOCAL4= 160
LOG_LOCAL5= 168
LOG_LOCAL6= 176
LOG_LOCAL7= 184

#
## Log Levels
#
DBG_CRITICAL= logging.CRITICAL   
DBG_ERROR   = logging.ERROR   
DBG_WARNING = logging.WARNING    
DBG_INFO    = logging.INFO    
DBG_NORMAL  = logging.DEBUG   
DBG_SOFT    = logging.DEBUG -3
DBG_NOISE   = logging.DEBUG -5
DBG_INSANE  = logging.DEBUG -8
DBG_NONE    = logging.NOTSET  

logging.addLevelName(DBG_SOFT, 'DBG_SOFT')
logging.addLevelName(DBG_NOISE, 'DBG_NOISE')
logging.addLevelName(DBG_INSANE, 'DBG_INSANE')


def SpeakerDefaults():
    return {
        'LOG_LEVEL'           : DBG_INFO,
        'LOG_TO_STDOUT'       : True,
        'LOG_TO_SMTP'         : False,
        'LOG_SMTP_SERVER'     : None,
        'LOG_SMTP_SENDER'     : None,
        'LOG_SMTP_RCPT'       : None,
        'LOG_SMTP_SUBJECT'    : None,
        'LOG_TO_SYSLOG'       : False,
        'LOG_TO_TWISTED'      : False,
        'LOG_SYSLOG_FACILITY' : LOG_USER,
        'LOG_SYSLOG_SERVER'   : ('localhost', 514),
        'LOG_TO_FILE'         : None,
        'LOG_FILE_ROTATE'     : 24,
        'LOG_FILE_NUMBER'     : 7,
        'LOG_PREFIX'          : "Mother",
        'LOG_COLOR'           : True,
        }


class InternalError(Exception):
    def __init__(self,value):
        self.value="InternalError: %s" % str(value)
    def __str__(self):
        return self.value


#
## The Great Speaker class ;)
#

from twisted.python.log import msg as _twilog
class Speaker:

    _spkr_initialized= False
    colored= True
    level= 0
    _root_logger= None
    _totwisted= False

    @staticmethod
    def initConsoleLogging():
      if Speaker._root_logger: return
      _root_logger= Speaker.init_logging(1, 'console')
      _handler= logging.StreamHandler()
      _root_logger.addHandler(_handler)
      _handler.setFormatter(_fmt_log)
      Speaker.disableTwisted()

    @staticmethod
    def disableTwisted():
      Speaker._totwisted= 0

    @staticmethod
    def init_logging(lvl, pref):
      if Speaker._root_logger: return
      Speaker._root_logger= logging.getLogger(pref)
      Speaker._root_logger.setLevel(lvl)
      return Speaker._root_logger

    @staticmethod
    def lastMsg(ss):
      try:
        print 'Error: %s' % str(ss)
        if Speaker._root_logger:
          Speaker._root_logger.info('spkr_error %s ' % str(ss))
        if Speaker._totwisted:
          _twilog('spkr_error %s ' % str(ss))
      except: pass

    @staticmethod
    def log_info(msg, *a, **kw):
      if Speaker.level > DBG_INFO: return
      try:
        if Speaker._totwisted:
          #_twilog('spkr (INFO): %s ' % msg, *a, **kw)
          _twilog(('(INFO): %s ' % msg) % a)
        if Speaker._root_logger:
          Speaker._root_logger.info('(INFO): %s ' % msg, *a, **kw)
      except Exception, ss:
        Speaker.lastMsg(ss)

    @staticmethod
    def log_insane(msg, *a, **kw):
      if Speaker.level > DBG_INSANE: return
      try:
        if Speaker._totwisted:
          #_twilog('spkr (INSANE): %s ' % msg, *a, **kw)
          _twilog(('(INSANE): %s ' % msg) % a)
        if Speaker._root_logger:
          Speaker._root_logger.info('(INSANE): %s ' % msg, *a, **kw)
      except Exception, ss:
        Speaker.lastMsg(ss)

    @staticmethod
    def log_debug(msg, *a, **kw):
      if Speaker.level > DBG_INSANE: return
      try:
        if Speaker._totwisted:
          #_twilog('spkr (DEBUG): %s ' % msg, *a, **kw)
          _twilog(('(DEBUG): %s ' % msg) % a)
        if Speaker._root_logger:
          Speaker._root_logger.info('(DEBUG): %s ' % msg, *a, **kw)
      except Exception, ss:
        Speaker.lastMsg(ss)

    @staticmethod
    def log_warning(msg, *a, **kw):
      if Speaker.level > DBG_WARNING: return
      try:
        if Speaker._totwisted:
          #_twilog('spkr (WARNING): %s ' % msg, *a, **kw)
          _twilog(('(WARNING): %s ' % msg) % a)
        if Speaker._root_logger:
          Speaker._root_logger.info('(WARNING): %s ' % msg, *a, **kw)
      except Exception, ss:
        Speaker.lastMsg(ss)

    @staticmethod
    def log_error(msg, *a, **kw):
      try:
        if Speaker._totwisted:
          #_twilog('spkr (ERROR): %s ' % msg, *a, **kw)
          _twilog(('(ERROR): %s ' % msg) % a)
        if Speaker._root_logger:
          Speaker._root_logger.info('(ERROR): %s ' % msg, *a, **kw)
      except Exception, ss:
        Speaker.lastMsg(ss)

    @staticmethod
    def log_critical(msg, *a, **kw):
      if Speaker.level > DBG_CRITICAL: return
      try:
        if Speaker._totwisted:
          #_twilog('spkr (CRITICAL): %s ' % msg, *a, **kw)
          _twilog(('(CRITICAL): %s ' % msg) % a)
        if Speaker._root_logger:
          Speaker._root_logger.info('(CRITICAL): %s ' % msg, *a, **kw)
      except Exception, ss:
        Speaker.lastMsg(ss)

    @staticmethod
    def log_log(*a, **kw):
      return
    @staticmethod
    def set_log_level(l): Speaker.level= l
    @staticmethod
    def get_log_level(*a, **kw): return Speaker.level
    @staticmethod
    def set_log_color(*a, **kw): pass

    @staticmethod
    def get_log_color(): return 1
        #return Speaker.colored

    @staticmethod
    def log_raise(*args):
        """ log_raise(*args): --> logging and Raising
        
        args[0:-1] is the un-formatted string.
        args[-1] is the Exception to be raised.
        """ 
        exc= args[-1]
        s= (args[0] % args[1:-1])
        Speaker.log_error(s)
        raise exc(s)

    @staticmethod
    def log_int_raise(*args):
        s= (args[0] % args[1:])
        Speaker.log_error(s)
        raise InternalError(s)

#
##
### logging initialization
##
#


def init_speaker(conf= {}):

    # prevent multiple initilization
    if not hasattr(Speaker, '_spkr_initialized'):
        Speaker.log_info("Logger already initialized. If you "
                         "want to change log level or colored "
                         "logs, use set_log_level, set_log_color.")
        return

    sdefs= SpeakerDefaults()
    cf_ok= True
    smtp_ok= True

    # need to read conf file or already done?
    if isinstance(conf, dict):
        conf_dict= conf
    else:
        conf_dict= {}
        try:
            execfile(conf, globals(), conf_dict)
        except Exception, cf_ko:
            # Remember the error: after logger
            # initialization it will be emitted
            cf_ok= False

    sdefs.update(conf_dict)

    #colors= sdefs.get('LOG_COLOR', False)
    #Speaker.set_log_color(colors)

    pref= sdefs['LOG_PREFIX']
    lvl= sdefs['LOG_LEVEL']
    Speaker.level= lvl

    if sdefs['LOG_TO_STDOUT']:
        _root_logger= Speaker.init_logging(lvl, pref)
        _handler= logging.StreamHandler()
        _root_logger.addHandler(_handler)
        _handler.setFormatter(_fmt_log)


    logfile= sdefs['LOG_TO_FILE']
    if logfile:
        frot= sdefs['LOG_FILE_ROTATE']
        fnum= sdefs['LOG_FILE_NUMBER']
        if frot:
            from logging.handlers import TimedRotatingFileHandler
            _handler= TimedRotatingFileHandler(logfile, 'M', frot, fnum)
        else:
            _handler= logging.FileHandler(logfile)

        _root_logger= Speaker.init_logging(lvl, pref)
        _root_logger.addHandler(_handler)
        _handler.setFormatter(_fmt_log)

    if sdefs['LOG_TO_TWISTED']:
      Speaker._totwisted= 1

    if sdefs['LOG_TO_SYSLOG']:
        fac= sdefs['LOG_SYSLOG_FACILITY']
        srv= sdefs['LOG_SYSLOG_SERVER']
        from logging.handlers import SysLogHandler
        _handler= SysLogHandler(srv, fac)
        _root_logger= Speaker.init_logging(lvl, pref)
        _root_logger.addHandler(_handler)
        _handler.setFormatter(_fmt_log)


    logsmtp= sdefs['LOG_TO_SMTP']
    if logsmtp:
        srv= sdefs['LOG_SMTP_SERVER']
        rcp= sdefs['LOG_SMTP_RCPT']
        snd= sdefs['LOG_SMTP_SENDER']

        if srv and rcp and snd:
            from logging.handlers import SMTPHandler
            _smtp_logger= logging.getLogger('SMTP%s' % pref)
            sbj= sdefs['LOG_SMTP_SUBJECT']
            _handler= SMTPHandler(srv, snd, rcp, sbj)
            _smtp_logger.addHandler(_handler)
            _handler.setFormatter(_fmt_log)

        else:
            smtp_ok= False

    if not cf_ok:
        Speaker.log_error("Unable to load conf file %s: %s. "\
                          "Using default values for logger configuration. ",
                          RED(conf), str(cf_ko))

    if not smtp_ok:
        Speaker.log_error("Invalid configuration for SMTP logging: "
                "Options LOG_SMTP_SENDER, LOG_SMTP_SERVER and LOG_SMTP_RCPT "
                "are manadatory if you want to use SMTP. SMTP disabled.")

    del Speaker._spkr_initialized



#
## COLORS
#


DEFCOL = "\033[0m"
#BLACKCOL = "\033[0;30m"
REDCOL = "\033[0;31m"
GREENCOL = "\033[0;32m"
#BROWNCOL = "\033[0;33m"
#BLUECOL = "\033[0;34m"
PURPLECOL = "\033[0;35m"
#CYANCOL = "\033[0;36m"
#LIGHTGRAYCOL = "\033[0;37m"
#DARKGRAYCOL = "\033[1;30m"
#LIGHTREDCOL = "\033[1;31m"
#LIGHTGREENCOL = "\033[1;32m"
YELLOWCOL = "\033[1;33m"
#LIGHTBLUECOL = "\033[1;34m"
#MAGENTACOL = "\033[1;35m"
#LIGHTCYANCOL = "\033[1;36m"
#WHITECOL = "\033[1;37m"

def _STRCOLOR(s, col):
    return Speaker.colored and\
            "%s%s%s" %(col, s, DEFCOL) or str(s)

def RED(s):
    return _STRCOLOR(s, REDCOL)
def GREEN(s):
    return _STRCOLOR(s, GREENCOL)
def YELLOW(s):
    return _STRCOLOR(s, YELLOWCOL)
def PURPLE(s):
    return _STRCOLOR(s, PURPLECOL)

