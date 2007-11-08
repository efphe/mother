
from speaker import Speaker
from commons import OKI_COL, INF_COL, ERR_COL
from eccez import QueryError, ConnectionError, BrokenConnection, InvalidFilter

"""
The Mother DB engine.
"""
DB_ENGINE_PGRES  = 1
DB_ENGINE_SQLITE = 2

DB_POOL_LIMITED = 1
DB_POOL_ELASTIC = 2
DB_POOL_GROWING = 3

_J= ', '.join
_A= ' AND '.join

SQL_DEFAULT = "MOTHER_SQL_DEFAULT"
SQL_NULL    =  None
SQL_TRUE    = "True"
SQL_FALSE   = "False"

class _DbInfo:
    iface_builder= None
    arg_format= None
    db_initialized= False

class MoFilter:

    def __init__(self, filter= None, tbl= None, store= None):
        self.locals= {}
        self.strfilter = []
        self.pre_filter = []
        self.post_filter = []

        #if filter and store and tbl:
        self.add_filter(filter, tbl, store)

        #elif filter or store or tbl:
            #Speaker.log_raise('Invalid Filter Args: %s, %s, %s', 
                    #ERR_COL(filter), ERR_COL(store), ERR_COL(tbl), 
                    #InvalidFilter)
        #else:
            #pass

    def _arg_format(self, k):
        return _DbInfo.arg_format % k 

    def return_filter(self):
        pre= self.pre_filter
        post= self.post_filter

        if len(pre) > 1 or len(post) > 1:
            Speaker.log_int_raise('Cannot handle Filter: pre, post= %s, %s', 
                    ERR_COL(pre), ERR_COL(post))

        if pre: f= pre[0]
        else:   f= '' 

        strfilter= self.strfilter
        if len(strfilter):
            strfilter= _A(strfilter)
            strfilter= ('WHERE' in strfilter or 'WHERE' in f )  \
                               and 'AND %s' % strfilter         \
                               or  'WHERE %s' % strfilter
            f= '%s %s' % (f, strfilter)

        if post:
            f= '%s %s' % (f, post[0])

        return f, self.locals

    def add_store(self, d):
        self.locals.update(d)

    def old_return_filter(self):
        s, d= self._return_filter()
        if self.post_filter:
            s= '%s %s' % (s, _J(self.post_filter))
        return s, d

    def return_ftrqry(self, qry):
        f, loc= self.return_filter()
        return '%s %s' % (qry, f), loc

    def add_post(self, filter):
        # XXX accepts also dicts?
        self.post_filter.append(filter)

    def add_filter(self, filter, tbl= None, store= None):

        if not filter:
            return

        def t(tp):
            return isinstance(filter, tp)
            
        if store: 
            self.locals.update(store)

        if t(str):

            if 'JOIN' in filter:
                self.pre_filter.append(filter)
            else:
                self.strfilter.append(filter)
            return

        afrm= self._arg_format

        res= []
        if t(dict):
            for k, v in filter.iteritems():
                if v== SQL_DEFAULT:
                    if tbl:
                        res.append('%s.%s= DEFAULT' % (tbl, k))
                    else:
                        res.append('%s= DEFAULT' %  k)

                elif v == SQL_NULL:
                    if tbl:
                        res.append('%s.%s IS NULL' % (tbl, k))
                    else:
                        res.append('%s IS NULL' %  k)
                else:
                    if tbl:
                        res.append('%s.%s= %s' % (tbl, k, afrm(k)))
                    else:
                        res.append('%s= %s' % (k, afrm(k)))

            self.strfilter.append(_A(res))
            self.locals.update(filter)
            return

        # ToDo: just assume that filter is iterable?
        if t(list) or t(set) or t(frozenset):
            if not store:
                Speaker.log_raise('Invalid Filter: store not provided '
                                  'for iterator filter.', InvalidFilter)
            for k in filter:
                try:
                    v= store[k]
                    self.locals[k]= v
                except:
                    Speaker.log_raise('Invalid Filter: key %s not in store', 
                            ERR_COL(k), InvalidFilter)

                if v== SQL_DEFAULT:
                    if tbl:
                        res.append('%s.%s= DEFAULT' % (tbl, k))
                    else:
                        res.append('%s= DEFAULT' %  k)
                elif v == SQL_DEFAULT:
                    if tbl:
                        res.append('%s.%s IS NULL' % (tbl, k))
                    else:
                        res.append('%s IS NULL' %  k)
                else:
                    if tbl:
                        res.append('%s.%s= %s' % (tbl, k, afrm(k)))
                    else:
                        res.append('%s= %s' % (k, afrm(k)))

            self.strfilter.append(_A(res))
            return
        
        Speaker.log_raise('Invalid Filter: type %s not allowed.', 
                ERR_COL(type(filter)), InvalidFilter)


class DbOne(Speaker):

    trans_level= 0
    _db_initialized= False
    _iface_instance= None
    _iface_attrs = [
            '_connect',
            '_rollback',
            '_commit',
            '_gquery',
            '_qquery',
            '_mqquery',
            '_mgquery'
            ]

    _exported_methods= [
            'lastrowid',
            'oc_query',
            'ov_query',
            'mr_query',
            'or_query',
            'mq_query',
            'mg_query',
            'beginTrans',
            'commit',
            'rollback',
            ]

    @staticmethod
    def _import_iface():
        iface= DbOne._iface_instance= _DbInfo.iface_builder()
        for attr in DbOne._iface_attrs:
            setattr(DbOne, attr, getattr(iface, attr))
        if hasattr(iface, '_mogrify'):
            DbOne.mogrify= staticmethod(iface._mogrify)

    @staticmethod
    def export_iface(where):

        if not DbOne._db_initialized:
            err= ERR_COL('!!!No Session Available!!!')
            self.log_int_raise("%s You are using the Db Pool, you "
                               "have disabled the persistent connection, "
                               "but no session was used to initialize this "
                               "Mother class (table= %s)", err, ERR_COL(tbl))

        for attr in DbOne._exported_methods:
            setattr(where, attr, getattr(DbOne, attr))

        mog= getattr(DbOne, 'mogrify', None)
        if mog:
            setattr(where, 'mogrify', mog)

    @staticmethod
    def beginTrans():
        DbOne.trans_level+= 1
        Speaker.log_debug(
                'Incremented transaction level: %s', 
                INF_COL(DbOne.trans_level))

    @staticmethod
    def rollback():
        if not DbOne.trans_level:
            Speaker.log_warning(
                    "Nothing to rollback: "
                    "nested rollback?")
            return

        DbOne._rollback()
        DbOne.trans_level= 0

        return

    @staticmethod
    def commit():
        lvl= DbOne.trans_level
        if not lvl:
            Speaker.log_warning(
                    "Nothing to commit: "
                    "nested commit?")
            return

        if lvl== 1:
            DbOne._commit()
            DbOne.trans_level-= 1
            Speaker.log_debug(
                    "Queries committed.")
            return

        DbOne.trans_level-= 1
        Speaker.log_debug(
                "Decremented transaction: now %s",
                INF_COL(DbOne.trans_level))
        return

    @staticmethod
    def lastrowid():
        return DbOne._iface_instance._lastrowid()

    @staticmethod
    def _safe_execute(execattr, s, d):

        try:
            return execattr(s, d)

        except BrokenConnection, e:

            Speaker.log_info('Connection to DB seems broken, '
                               'now reconnecting...')
            try:
                DbOne._connect()
            except:
                Speaker.log_raise('Cannot re-establish connection', BrokenConnection)

            # if we are inside a trans, we have to signal 
            # the broken transaction -> exception.
            # otherwise, the query is tried once more
            if DbOne.trans_level:
                Speaker.log_raise('Connection re-established: transaction is lost.', 
                        ConnectionError)
        
            return execattr(s, d)

        except QueryError, e:
            DbOne._rollback()
            Speaker.log_raise('%s queries: %s.', 
                    ERR_COL('Rollbacked'), ERR_COL(e), QueryError)

    @staticmethod
    def _do_query(s, filter= None, result= True):

        execattr= result and DbOne._gquery or DbOne._qquery

        if not filter:
            d= {}
        elif isinstance(filter, MoFilter):
            s, d= filter.return_ftrqry(s)
        elif isinstance(filter, dict):
            d= filter
        else:
            Speaker.log_int_raise('Invalid Filter Type: %s', 
                    ERR_COL(type(filter)))

        # logging info...
        mogrify= getattr(DbOne._iface_instance, '_mogrify', None)
        if mogrify is not None:
            Speaker.log_info("QSQL- %s", mogrify(s, d))
        else:
            Speaker.log_info("QSQL- %s, Filter= %s" % (s, d))

        return DbOne._safe_execute(execattr, s, d)

    @staticmethod
    def _get_query(s, filter= None):

        res= DbOne._do_query(s, filter, True)
        if not DbOne.trans_level:
            DbOne._commit()
        return res

    @staticmethod
    def _quiet_query(s, filter= None):

        DbOne._do_query(s, filter, False)
        if not DbOne.trans_level:
            DbOne._commit()

    @staticmethod
    def oc_query(s, filter= None):
        """ One Commit Query: no returns."""
        DbOne._quiet_query(s, filter)

    @staticmethod
    def mr_query(s, filter= None):
        """ Multiple Records Query: return a dict list."""
        return DbOne._get_query(s, filter)

    @staticmethod
    def or_query(s, filter= None):
        """ One Record Query: returns a dict."""

        res= DbOne.mr_query(s, filter)
        
        if len(res)<> 1:
            Speaker.log_raise(
                    "Query returned %s records instead of 1." % 
                    ERR_COL(len(res)), QueryError)

        return res[0]

    @staticmethod
    def ov_query(s, filter):
        """ One Value Query: returns a unique value."""
        
        res= DbOne.or_query(s, filter)

        res= res.values()
        if len(res)<> 1:
            Speaker.log_raise(
                    "Query returned %s values instead of 1." % 
                    ERR_COL(len(res)), QueryError)

        return res[0]

    @staticmethod
    def mq_query(s, l):
        """ Multiple Quiet Query: execute a multiple, quiet query."""

        Speaker.log_debug("Executing Massive Query...")

        DbOne._safe_execute(DbOne._mqquery, s, l)

        if not DbOne.trans_level:
            DbOne._commit()

    @staticmethod
    def mg_query(s, l):
        """ Multiple Get Query: execute a multiple, get query."""

        Speaker.log_debug("Executing Massive Query...")

        res= DbOne._safe_execute(DbOne._mgquery, s, l)

        if not DbOne.trans_level:
            DbOne._commit()

        return res

class DbFly(Speaker):

    # Iface methods
    # _connect()  
    # _rollback()
    # _commit()
    # _get_query(qry, filter)
    # _quiet_query(qry, filter)
    # _close()

    _default_session= 'DbFly'

    _iface_attrs = [
            '_connect',
            '_rollback',
            '_commit',
            '_gquery',
            '_qquery',
            '_mqquery',
            '_mgquery',
            '_close'
            ]

    _exported_methods= [
            'lastrowid',
            'oc_query',
            'ov_query',
            'mr_query',
            'or_query',
            'mq_query',
            'mg_query',
            'beginTrans',
            'commit',
            'rollback',
            'endSession',
            ]

    def __init__(self, name= None):

        self.session_name= name or self._default_session
        self._import_iface()
        #self._connect()
        self._queries_n= 0

    def _import_iface(self):

        iface= self._iface_instance= _DbInfo.iface_builder()

        for attr in self._iface_attrs:
            setattr(self, attr, getattr(iface, attr))

        if hasattr(self._iface_instance, '_mogrify'):
            self.mogrify= self._iface_instance._mogrify

    def export_iface(self, where):

        for attr in self._exported_methods:
            setattr(where, attr, getattr(self, attr))

        mog= getattr(self, 'mogrify', None)
        if mog:
            setattr(where, 'mogrify', mog)


    def lastrowid(self):
        return self._iface_instance._lastrowid()

    def beginTrans(self):
        self.log_noise('"Transactions is the default '
                    "inside Sessions (session= %s).",
                    INF_COL(self.session_name))

    def rollback(self):
        self.log_debug("Rollbacking queries for Session %s", 
                self.session_name)
        self._rollback()
        self._queries_n= 0

    def commit(self):
        try:
            self.log_info("Syncing (%s) queries for Session %s.", 
                    OKI_COL(self._queries_n), OKI_COL(self.session_name))
            self._commit()
            self._queries_n= 0
            return 0
        except Exception, ss: 
            return ss

    def endSession(self):
        self.log_info("Terminating Session %s",
                OKI_COL(self.session_name))

        if not hasattr(self, '_pool_queue'):
            self.log_insane("No Pool: Session %s will be closed.", 
                    OKI_COL(self.session_name))
            self.commit()
            self._close()
            return

        res= self.commit()

        if res <> 0:
            MotherPool.discard(self)
            self.log_error("Session %s, unable to commit queries(): "
                        "%s. Broken session removd from the pool.", 
                        ERR_COL(self.session_name), ERR_COL(res))

        MotherPool.backHome(self)

    def _safe_execute(self, execattr, s, d):

        try:
            res= execattr(s, d)
            self._queries_n+= 1
            return res

        except BrokenConnection, e:

            self.log_info('Connection to DB seems broken, '
                               'now reconnecting...')
            try:
                self._connect()
            except:
                self.log_raise('Cannot re-establish connection', BrokenConnection)

            # DbFly are always in transaction state, so
            # we have to raise an exception.
            self.log_raise('Connection re-established: transaction is lost.', 
                        ConnectionError)
        
            #return execattr(s, d)

        except QueryError, e:
            self._rollback()
            self.log_raise('%s queries: %s.', ERR_COL('Rollbacked'), 
                    ERR_COL(e), QueryError)

    def _do_query(self, s, filter= None, result= True):

        execattr= result and self._gquery or self._qquery

        if not filter:
            d= {}
        elif isinstance(filter, MoFilter):
            s, d= filter.return_ftrqry(s)
        elif isinstance(filter, dict):
            d= filter
        else:
            self.log_int_raise('Invalid Filter Type: %s', 
                    ERR_COL(type(filter)))

        mogrify= getattr(self._iface_instance, '_mogrify', None)
        if mogrify is not None:
            self.log_info("%s: QSQL- %s", INF_COL(self.session_name), mogrify(s, d))
        else:
            self.log_info("%s: QSQL- %s, Filter= %s" , INF_COL(self.session_name), s, d)

        return self._safe_execute(execattr, s, d)

    def _get_query(self, s, filter= None):

        return self._do_query(s, filter, True)

    def _quiet_query(self, s, filter= None):

        self._do_query(s, filter, False)

    def oc_query(self, s, filter= None):
        """ One Commit Query: no returns."""
        self._quiet_query(s, filter)

    def mr_query(self, s, filter= None):
        """ Multiple Records Query: return a dict list."""
        return self._get_query(s, filter)

    def or_query(self, s, filter= None):
        """ One Record Query: returns a dict."""

        res= self.mr_query(s, filter)
        
        if len(res)<> 1:
            self.log_raise(
                    "Query returned %s records instead of 1." % 
                    ERR_COL(len(res)), QueryError)

        return res[0]

    def ov_query(self, s, filter= None):
        """ One Value Query: returns a unique value."""
        
        res= DbOne.or_query(s, filter)

        res= res.values()
        if len(res)<> 1:
            self.log_raise(
                    "Query returned %s values instead of 1." % 
                    ERR_COL(len(res)), QueryError)

        return res[0]

    def mq_query(self, s, l):
        """ Multiple Quiet Query: execute a multiple quiet query."""

        Speaker.log_debug("%s: Executing Massive Query...", 
                        INF_COL(self.session_name))

        res= self._safe_execute(self._mqquery, s, l)
        # len(l) - 1: because a query is added by safe_execute
        self._queries_n+= len(l) - 1

    def mg_query(self, s, l):
        """ Multiple Get Query: execute a multiple get query."""

        Speaker.log_debug("%s: Executing Massive Query...", 
                        INF_COL(self.session_name))

        res= self._safe_execute(self._mgquery, s, l)
        # len(l) - 1: because a query is added by safe_execute
        self._queries_n+= len(l) - 1
        return res

class MotherPool:

    from Queue import Empty as _empty_queue

    _pool_initialized= False

    _pool_max= 10
    _pool_min= 4
    _pool_timeout= 15
    _pool_current= 0
    _pool_orphans= {}
    _pool_queue= None
    _pool_type= DB_POOL_LIMITED
    _pool_calm= False

    import threading

    _pool_current_mutex= threading.Lock()
    _pool_get_mutex= threading.Lock()
    _pool_orphans_mutex= threading.Lock()

    del threading

    @staticmethod
    def _pool_type_str(ptype):

        if ptype == DB_POOL_LIMITED:
            return 'Limited'
        elif ptype == DB_POOL_ELASTIC: 
            return 'Elastic'
        else:
            return 'Growing'

    @staticmethod
    def _add_orphan(sname, db):
        m= MotherPool._pool_orphans_mutex
        m.acquire()
        MotherPool._pool_orphans[id(db)]= sname
        m.release()

    @staticmethod
    def _del_orphan(db):
        m= MotherPool._pool_orphans_mutex
        m.acquire()
        MotherPool._pool_orphans.pop(id(db))
        m.release()

    @staticmethod
    def _full():

        ptype= MotherPool._pool_type

        if ptype in [DB_POOL_ELASTIC, DB_POOL_GROWING]:
            return False

        # Db Pool is Limited
        m= MotherPool._pool_current_mutex
        m.acquire()
        res= MotherPool._pool_current== MotherPool._pool_max
        m.release()
        return res

    @staticmethod
    def status():
        """ status() -> (pool_type, available, total, min, max, orphaned)
        """

        mc= MotherPool._pool_current_mutex
        mg= MotherPool._pool_get_mutex
        mo= MotherPool._pool_orphans_mutex
        mc.acquire()
        mg.acquire()
        mo.acquire()
        total= MotherPool._pool_current
        available= MotherPool._pool_queue.qsize()
        orphaned= MotherPool._pool_orphans.values()
        mo.release()
        mg.release()
        mc.release()
        min= MotherPool._pool_min
        max= MotherPool._pool_max

        ptype= MotherPool._pool_type
        sptype= MotherPool._pool_type_str(ptype)

        return (sptype, available, total, min, max, orphaned)

    @staticmethod
    def _add_conn(n=1):
        """ Never call me directly: use _addConnection!"""

        cur= MotherPool._pool_current
        max= MotherPool._pool_max 

        Speaker.log_info(
                "Adding %s new connection(s) (max= %s, cur= %s)",
                OKI_COL(n), OKI_COL(max), OKI_COL(cur))

        for i in xrange(n):
            p= DbFly()
            q= MotherPool._pool_queue
            p._pool_queue= q
            q.put(p)

        MotherPool._pool_current+= n

        return n

    ##
    # Note that this function could be called by:
    #  init_pool() -> no problem with mutexes
    #  newSession() -> no problem with mutexes, coz
    #                  lock is acquired.
    ##
    @staticmethod
    def _addConnection(n=1):
        """ 
        Don't call me directly, use newSession() instead!
        """
        m= MotherPool._pool_current_mutex
        m.acquire()
        MotherPool._add_conn(n)
        m.release()


    @staticmethod
    def _init_pool(n= None, pg_conn= None):

        n= n or MotherPool._pool_min

        Speaker.log_info("Initializing connection Pool ...")
        from Queue import Queue
        MotherPool._pool_queue= Queue()
        MotherPool._addConnection(n)

        MotherPool._pool_initialized= True

    @staticmethod
    def _get_session():
        """ Never call me directly: use newSession!"""

        db_pool= MotherPool._pool_queue

        try:
            db= db_pool.get_nowait()
            return db
        except MotherPool._empty_queue:
            pass

        full= MotherPool._full()
        calm= MotherPool._pool_calm

        # Wait or create immediately a new connection?
        if calm or full:
            
            # wait.
            ptimeout= MotherPool._pool_timeout
            Speaker.log_info(
                "MotherPool: waiting for a free connection "
                "(timeout= %s) ...", INF_COL(ptimeout))

            # If full, wait and hope.
            if full:
                return db_pool.get(True, ptimeout)

            # If calm, wait only
            try:
                return db_pool.get(True, ptimeout)
            except MotherPool._empty_queue:
                pass
        
        # Ok, here the pool is not full.
        # Moreover, we have already waited.
        MotherPool._addConnection()
        return db_pool.get_nowait()

    @staticmethod
    def newSession(name= None):

        Speaker.log_info("Initializing session %s", INF_COL(name))

        if not MotherPool._pool_initialized:
            return DbFly(name)

        m= MotherPool._pool_get_mutex
        m.acquire()

        try:
            session= MotherPool._get_session()

        except Exception, ss:
            m.release()
            Speaker.log_int_raise(
                    "Cannot retrieve Session from Pool (%s). FATAL.", 
                    ERR_COL(ss))

        sname= name or DbFly._default_session

        MotherPool._add_orphan(sname, session)

        m.release()
        session.session_name= sname 

        return session

    @staticmethod
    def backHome(dbfly):

        q= MotherPool._pool_queue
        m= MotherPool._pool_current_mutex
        sname= dbfly.session_name

        m.acquire()

        if MotherPool._pool_type == DB_POOL_ELASTIC and \
           MotherPool._pool_current > MotherPool._pool_min:
                MotherPool._ns_discard(dbfly)
                Speaker.log_info("Elastic Pool: session %s "
                                 "closed and removed.", OKI_COL(sname))
                m.release()
                return

        try:
            q.put_nowait(dbfly)
        except Exception, ss:
            Speaker.log_warning(
                    "Removing connection %s from Pool: %s.", 
                    ERR_COL(dbfly.session_name), ERR_COL(ss))
            MotherPool._ns_discard(dbfly)
            m.release()
            return

        MotherPool._del_orphan(dbfly)
        Speaker.log_info('Session %s back to the Pool.', OKI_COL(sname))
        m.release()
        return

    @staticmethod
    def _ns_discard(dbfly):

        MotherPool._pool_current-= 1
        MotherPool._del_orphan(dbfly)
        try:
            dbfly._close()
        except Exception, ss:
            Speaker.log_error("Unable to close connection: %s", ERR_COL(ss))

    @staticmethod
    def discard(dbfly):

        m= MotherPool._pool_current_mutex

        m.acquire()
        MotherPool._ns_discard(dbfly)
        m.release()
        Speaker.log_warning("Connection %s dropped from Pool.", 
                ERR_COL(dbfly.session_name))



def init_abdbda(conf, forced= {}):

    if _DbInfo.db_initialized:
        Speaker.log_warning('AbDbDa already initialized.')
        return

    err= None
    if not isinstance(conf, dict):
        import speaker
        loc= {}
        names_dict= speaker.__dict__.copy()
        names_dict.update(globals())
        try:
            execfile(conf, names_dict, loc)
        except Exception, ss:
            err= "Unable to read Mother configuration "  \
                 "file %s: %s" % (ERR_COL(conf), ss)
    else:
        loc= conf

    loc.update(forced)

    if hasattr(Speaker, '_spkr_initialized'):
        from speaker import init_speaker
        init_speaker(loc)

    # now that speaker is up, error is printable
    if err:
        Speaker.log_int_raise(err)

    # set the right db engine
    db_engine= loc.get('DB_ENGINE', DB_ENGINE_PGRES)
    if db_engine == DB_ENGINE_PGRES:
        from mother.postgres import MotherPostgres as _builder, \
                                     init_postgres as init_engine
        _DbInfo.arg_format= '%%(%s)s'
    elif db_engine == DB_ENGINE_SQLITE:
        from mother.sqlite import MotherSqlite as _builder, \
                                   init_sqlite as init_engine
        _DbInfo.arg_format= ':%s'

    init_engine(loc)
    _DbInfo.iface_builder= _builder

    pool= loc.get('DB_POOL', False)
    db_one= loc.get('DB_PERSISTENT_ONE', False)

    if not pool or db_one:
        DbOne._import_iface()
        #DbOne._connect()
        DbOne._db_initialized= True

    if not pool:
        _DbInfo.db_initialized= True
        return

    pool_to= loc.get('DB_POOL_TIMEOUT', MotherPool._pool_timeout)
    pool_min= loc.get('DB_POOL_MIN', MotherPool._pool_min)
    pool_max= loc.get('DB_POOL_MAX', MotherPool._pool_max)
    pool_calm= loc.get('DB_POOL_PATIENT', False)
    pool_type= loc.get('DB_POOL_TYPE', MotherPool._pool_type)

    if pool_type == DB_POOL_LIMITED and pool_min> pool_max:
        Speaker.log_int_raise("Invalid configuration file: %s",
                ERR_COL("DB_POOL_MIN > DB_POOL_MAX !!!"))

    MotherPool._pool_min= pool_min
    if pool_type in  [DB_POOL_ELASTIC, DB_POOL_GROWING]:
        MotherPool._pool_max= -1
    else:
        MotherPool._pool_max= pool_max

    MotherPool._pool_timeout= pool_to
    MotherPool._pool_type= pool_type
    MotherPool._pool_calm= pool_calm

    MotherPool._init_pool()
    _DbInfo.db_initialized= True

    return


