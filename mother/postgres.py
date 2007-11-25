# file: postgres.py
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

import psycopg2
from mother.speaker import Speaker
from mother.commons import ERR_COL

from mother.eccez import QueryError, BrokenConnection

class _PostgresInfo:
    dbuser= None
    dbpasswd= None
    dbname= None
    dbport= 5432
    dbhost= 'localhost'

    @staticmethod
    def _connect_str():

        dbhost= _PostgresInfo.dbhost
        dbname= _PostgresInfo.dbname
        dbpasswd= _PostgresInfo.dbpasswd
        dbuser= _PostgresInfo.dbuser

        # Unix Sockets?
        if not dbhost:
            return "dbname=%s user=%s password=%s" % (dbname, dbuser, dbpasswd)

        dbport= _PostgresInfo.dbport
    
        return ( "dbname=%s user=%s host=%s password=%s port=%d" 
            % (dbname, dbuser, dbhost, dbpasswd, dbport) )

class MotherPostgres:
    
    def __init__(self):
        self._connect()

    def _connect(self):

        Speaker.log_insane('Initializing postgres connection...')
        try:
            s= _PostgresInfo._connect_str()
            self.connection= psycopg2.connect(s)
            self.cursor= self.connection.cursor()
        except Exception, ss:
            Speaker.log_raise('Unable to establish a connection '
                    'with the database: %s', ERR_COL(ss), 
                    BrokenConnection)

    def _rollback(self):
        self.connection.rollback()

    def _commit(self):
        self.connection.commit()

    def _close(self):
    	Speaker.log_insane("Closing Connection...")
        try:
            self.connection.close()
        except:
            pass

    def _extract(self):

        c= self.cursor
        cres= c.fetchall()
        desc= c.description
        res= []

        for rec in cres:
            drec= {}
            for n, field in enumerate(rec):
                drec[desc[n][0]]= field
            res.append(drec)

        return res

    def _lastrowid(self):
        return self.cursor.lastrowid

    def _execute(self, q, d):
        d= d or None
        try:
            self.cursor.execute(q, d)
        except psycopg2.OperationalError:
            Speaker.log_raise('Connection is broken...', BrokenConnection)
        except Exception, ss:
            Speaker.log_raise('%s', ERR_COL(ss), QueryError)

    def _executemany(self, q, l):

        try:
            self.cursor.executemany(q, l)
        except psycopg2.OperationalError:
            Speaker.log_raise('Connection is broken...', BrokenConnection)
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

    def _mogrify(self, q, d):

        return self.cursor.mogrify(q, d)

    def get_tables(self):
        qry= ("SELECT table_name from information_schema.tables "
              "WHERE table_schema='public'")
        res= self._gquery(qry, {})
        return [d['table_name'] for d in res]

    def get_table_fkeys(self, tbl):
        qry= (
            "SELECT pt.tgargs, pt.tgnargs, pt.tgdeferrable, pt.tginitdeferred,"
            "pg_proc.proname, pg_proc_1.proname FROM pg_class pc,"
            "pg_proc pg_proc, pg_proc pg_proc_1, pg_trigger pg_trigger,"
            "pg_trigger pg_trigger_1, pg_proc pp, pg_trigger pt "
            "WHERE  pt.tgrelid = pc.oid AND pp.oid = pt.tgfoid "
            "AND pg_trigger.tgconstrrelid = pc.oid "
            "AND pg_proc.oid = pg_trigger.tgfoid "
            "AND pg_trigger_1.tgfoid = pg_proc_1.oid "
            "AND pg_trigger_1.tgconstrrelid = pc.oid "
            "AND ((pc.relname= '%s') "
            "AND (pp.proname LIKE '%%ins') "
            "AND (pg_proc.proname LIKE '%%upd') "
            "AND (pg_proc_1.proname LIKE '%%del') "
            "AND (pg_trigger.tgrelid=pt.tgconstrrelid)) " % tbl)

        mykeys=[]
        result= []
        res= self._gquery(qry, {})

        for d in res:
            buf=d['tgargs']
            s= str(buf)
            l= s.split("\x00")
            mykey= l[4]
            if mykey in mykeys:
                continue
            tbl= l[2]
            key= l[5]
            result.append((mykey, tbl, key))
            mykeys.append(mykey)
        return result 

    def get_table_fields(self, tbl):
        qry= ("SELECT column_name from information_schema.columns "
                "WHERE table_name='%s'" % tbl)
        res= self._gquery(qry, {})
        return [d['column_name'] for d in res]

    def get_table_pkeys(self, tbl):
        qry= ("SELECT column_name from information_schema.key_column_usage "
            "JOIN information_schema.table_constraints on "
            "information_schema.key_column_usage.constraint_name="
            "information_schema.table_constraints.constraint_name "
            "WHERE information_schema.key_column_usage.table_name='%s' and "
            "information_schema.table_constraints.constraint_type='PRIMARY KEY'" % tbl)
        res= self._gquery(qry, {})
        return [d['column_name'] for d in res]



def init_postgres(vars):
    try:
        _PostgresInfo.dbuser= vars['DB_USER']
    except:
        Speaker.log_int_raise('Variable %s not specified!', ERR_COL('DB_USER'))
    try:
        _PostgresInfo.dbname= vars['DB_NAME']
    except:
        Speaker.log_int_raise('Variable %s not specified!', ERR_COL('DB_NAME'))
    
    _PostgresInfo.dbpasswd= vars.get('DB_PASSWD', '')
    _PostgresInfo.dbhost= vars.get('DB_HOST', 'localhost')
    _PostgresInfo.dbport= vars.get('DB_PORT', 5432)

