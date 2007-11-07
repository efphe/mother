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
        self.connection= None

    def _extract(self):
        c= self.cursor
        rec_descr= c.getdescription()

        res= []
        for rec in c:
            drec= {}
            for n, field in enumerate(rec):
                drec[rec_descr[n][0]]= field
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

    def _gquery(self, q, d):

        self._execute(q, d)
        return self._extract()
    
    def _qquery(self, q, d):

        self._execute(q, d)

    def _mqquery(self, q, l):
        try:
            self.cursor.executemany(q, l)
        except Exception, ss:
            Speaker.log_raise('%s', ERR_COL(ss), QueryError)

        return None

    def _mgquery(self, q, l):
        try:
            self.cursor.executemany(q, l)
        except Exception, ss:
            Speaker.log_raise('%s', ERR_COL(ss), QueryError)

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
    
