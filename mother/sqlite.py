# file: sqlite.py
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


import apsw
from mother.speaker import Speaker
from mother.commons import ERR_COL, INF_COL

from mother.eccez import QueryError, BrokenConnection

class _SqliteInfo:

    dbfile= None

class MotherSqlite:
    
    def __init__(self):

        self._connect()

    def _connect(self):

        Speaker.log_insane('Initializing sqlite connection (db = %s)...', 
                INF_COL(_SqliteInfo.dbfile))
        dbfile= _SqliteInfo.dbfile

        try:
            self.connection= apsw.Connection(dbfile)
            self.cursor= self.connection.cursor()
        except Exception, ss:
            Speaker.log_raise('Unable to establish a connection '
                    'with the database: %s', ERR_COL(ss), 
                    BrokenConnection)

        if self.connection.getautocommit():
            self.cursor.execute('BEGIN')

    def _rollback(self):
        self.cursor.execute('ROLLBACK')
        self.cursor.execute('BEGIN')

    def _commit(self):
        self.cursor.execute('COMMIT')
        self.cursor.execute('BEGIN')

    def _close(self):
    	Speaker.log_insane("Closing Connection...")
	try:
	    self.connection.close()
	except:
	    pass

    def _extract(self):
        c= self.cursor
        # cannot understand why, if no result is fetched,
        # description is not available....
        try:
            desc= c.getdescription()
        except apsw.ExecutionCompleteError:
            # forcing to return no results
            return []

        res= []
        for rec in c:
            drec= {}
            for n, field in enumerate(rec):
                drec[desc[n][0]]= field
            res.append(drec)

        return res

    def _lastrowid(self):
        return self.connection.last_insert_rowid()

    def _execute(self, q, d):
        d= d or {}
        try:
            self.cursor.execute(q, d)
        except Exception, ss:
            Speaker.log_raise('%s', ERR_COL(ss), QueryError)

    def _executemany(self, q, l):

        try:
            self.cursor.executemany(q, l)
        except Exception, ss:
            Speaker.log_raise('%s', ERR_COL(ss), QueryError)

    def _gquery(self, q, d):

        self._execute(q, d)
        return self._extract()
    
    def _qquery(self, q, d):

        self._execute(q, d)

    def _mqquery(self, q, l):

        self._executemany(q, l)

    def _mgquery(self, q, l):

        self._executemany(q, l)
        return self._extract()

    def get_tables(self):
        qry= ("SELECT tbl_name FROM SQLITE_MASTER WHERE type='table'")
        res= self._gquery(qry, {})
        return [d['tbl_name'] for d in res]

    def get_table_fkeys(self, tbl):
        qry= ('pragma foreign_key_list(%s)' % tbl)
        res= self._gquery(qry, {})
        return [(d['from'], d['table'], d['to']) for d in res]

    def get_table_fields(self, tbl):
        qry= ('pragma table_info(%s)' % tbl)
        res= self._gquery(qry, {})
        return [d['name'] for d in res]

    def get_table_pkeys(self, tbl):
        qry= ('pragma table_info(%s)' % tbl)
        res= self._gquery(qry, {})
        return [d['name'] for d in res if d['pk']]



def init_sqlite(vars):
    try:
        _SqliteInfo.dbfile= vars['DB_FILE']
    except:
        Speaker.log_int_raise('Variable %s not specified!', ERR_COL('DB_FILE'))
    
