# file: mothers.py
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


#
##
### MoThEr. Mommas gonna make all of your nightmares come true.
##                                                        PF
#

"""
Where the main Mother Classes and methods are defined:

 * init_mother
 * DbMother
 * MotherManager
 * MotherBox
 * MotherFusion
 * MotherMany
 * MotherSession
 * MotherPoolStatus
 * MotherPoolStratus
"""
            
from mother.speaker import Speaker

#
## Mother Symbols
#

from mother.commons import ERR_COL, INF_COL, OKI_COL
from mother.commons import MO_NOA, MO_DEL, MO_UP, MO_SAVE, MO_LOAD
from mother.commons import MO_BEFORE, MO_AFTER

#
## MoThEr: SQL symbols.
#

from mother.abdbda import DbOne, MoFilter
from mother.abdbda import SQL_DEFAULT, SQL_NULL, SQL_TRUE, SQL_FALSE
from mother.abdbda import _J, _A

#
##
### MoThEr Utils.
##
#

def _do_nothing(*args):
    pass

def init_mother(cfile, fnaming= None):
    """ init_mother(cfile [fnaming= None]) -> None

    Mother Initialization.
    `cfile` is the Mother configuration file. You can obtain a 
    default configuration file using mothermapper (option -C).

    `fnaming` is a function: auto created methods will be named
    with this function. If None, a default function will be used.

    The function has the following synopsis: 
    
        foo(str [,pref= None]) -> str

    The input str is the name of the table. pref is a optional prefix.
    Note that if you want to avoid method names collisions, `pref` has
    to be used inside your function. Ie, your function must have 
    different return values when different prefixes are used.
    """

    if not hasattr(DbMother, '_mo_initialized'):
        Speaker.log_warning("Mother already initialized.")
        return

    d= {}
    import mother.speaker as speaker
    import mother.abdbda as abdbda
    names_dict= speaker.__dict__.copy()
    names_dict.update(abdbda.__dict__)
    execfile(cfile, names_dict, d)

    DB_ENGINE_PGRES= abdbda.DB_ENGINE_PGRES
    db_engine= d.get('DB_ENGINE', DB_ENGINE_PGRES)
    if db_engine == DB_ENGINE_PGRES:
        DbMother._sqlInsert= DbMother._sqlPostgresInsert
        _DbMap._mo_arg_format= '%%(%s)s'

        use_oids= d.get('MOTHER_OIDS', True)
        if not use_oids:
            DbMother._mo_pg_oids= False
            abdbda.DbFly.exported_methods.remove('lastrowid')
            abdbda.DbOne.exported_methods.remove('lastrowid')
        else:
            DbMother._mo_pg_oids= True

    else:
        DbMother._sqlInsert= DbMother._sqlSqliteInsert
        _DbMap._mo_arg_format= ':%s'

    del DB_ENGINE_PGRES

    sname= d.get('MOTHER_SESSION_NAME', 
            DbMother._mo_session_name)
    abdbda.init_abdbda(d)

    del speaker
    del abdbda

    # Load DB map
    momap= d['MOTHER_MAP']
    _DbMap._load_map(momap)

    # Design Mother
    if fnaming:
        Speaker.log_insane("Testing fnaming function...")
        try:
            res_str= fnaming('foo')
            assert isinstance(res_str, str)
        except:
            Speaker.log_warning(
                    "Testing %s. Default fnaming function "
                    "will be used.", ERR_COL('Failed!'))
            fnaming= None
    
    if not fnaming:
        from mother.commons import MotherNaming
        fnaming= MotherNaming

    DbMother.MotherNaming= staticmethod(fnaming)
    DbMother._mo_cfile= cfile
    DbMother.__init__= DbMother.__post_init__
    DbMother._mo_session_name= sname

    # Ohhh, destroying is amazing, isn't it?
    del DbMother.__post_init__
    del DbMother._mo_initialized
    del DbMother._sqlSqliteInsert
    del DbMother._sqlPostgresInsert

def MotherSession(name= None):
    """ MotherSession([name= None, pg_conn= None]) 

    Returns a new Session. Each session is an isolated unit of work.
    The queries made inside a session are automatically transaction'ed.
    The new session has to be released, when his work is finished, with
    session.endSession(). This call commit the queries and, if the Mother
    Pool is used, put the connection inside the pool. """

    from mother.abdbda import MotherPool

    if not name:
        import random
        name= "%s%d" % (DbMother._mo_session_name, random.randint(1,10000))

    return MotherPool.newSession(name) 

def MotherPoolStatus():
    """MotherPoolStatus() -> (pool_type, avail, total, min, max, active)

    pool_type: Limited, Elastic, Growing or -1 if pool is not active
    avail: number of available connections.
    total: number of connection established.
    min: connections established during initialization.
    max: maximum number of connections allowed on the Pool.
    active: number of connections used now."""

    from mother.abdbda import MotherPool

    if not MotherPool._pool_initialized:
        return ('NoPool', -1, -1, -1, -1, -1)
    return MotherPool.status()

def MotherPoolStratus():
    """ MotherPoolStratus() -> string

    This is a wrapper of MotherPoolStatus. 
    Differently form MotherPoolStatus, the return value is human readable."""

    return """
    Pool Type               ~ %s
    Connections Available   ~ %d
    Connections Established ~ %d
    Minimum Connections     ~ %d
    Maximum Connections     ~ %d
    Connections Employed    ~ %s 
    """ % MotherPoolStatus()

class _DbMap(Speaker):
    _map_file=       None
    _map_fields=     None
    _map_pkeys=      None
    _map_children=   None
    _map_rels=       None

    # Mapping actions
    @staticmethod
    def _flag_actions(obj, flag):
        if flag == MO_UP: return obj.update
        if flag == MO_DEL: return obj.delete
        if flag == MO_NOA: return _do_nothing
        if flag == MO_SAVE: return obj.insert
        if flag == MO_LOAD: return obj.load
        obj.log_int_raise("Invalid flag %s", ERR_COL(flag))

    @staticmethod
    def _load_map(map_file):
        from os import path
        if not path.isfile(map_file):
            Speaker.log_int_raise("Mother Map %s does not exist.", ERR_COL(map_file)) 
        
        try:
            fil= open(map_file, 'rb')
        except:
            Speaker.log_int_raise("Unable to open Mother Map %s.", ERR_COL(map_file)) 

        import cPickle
        try:
            map_dicts= cPickle.load(fil)
            _DbMap._map_file= map_file
            _DbMap._map_fields= map_dicts['K']
            _DbMap._map_pkeys= map_dicts['P']
            _DbMap._map_children= map_dicts['C']
            _DbMap._map_rels= map_dicts['R']
        except:
            try:
                fil.close()
            except:
                pass

            Speaker.log_int_raise("Mother Map %s is malformed.", ERR_COL(map_file)) 

        fil.close()

    @staticmethod
    def _table_fields(tbl):
        return _DbMap._map_fields[tbl]

    @staticmethod
    def _table_pkeys(tbl):
        return _DbMap._map_pkeys[tbl]

    @staticmethod
    def _table_children(tbl):
        return _DbMap._map_children[tbl]

    @staticmethod
    def _searchRelation(tbls):

        fz= frozenset(tbls)

        trd= _DbMap._map_rels
        try:
            r_tbl= trd[fz]
            return r_tbl

        except:
            pass

        Speaker.log_insane(\
            "Warning: direct relation for tables %s "
            "is not defined: searching subset...",
            INF_COL(list(fz)))

        rels= [trd[k] for k in trd.keys() if fz< k]

        if len(rels)<>1:
            Speaker.log_int_raise(
                "In _searchRelation: can not choose the "  
                "relation table. There are %s possible "     
                "choices: %s .", ERR_COL(len(rels)), 
                ERR_COL(_J(rels)))

        return rels[0]

    @staticmethod
    def _isChildOf(c, f):
        try:
            return c in _DbMap._map_children[f]
        except:
            return False

    @staticmethod
    def _sqlFreeJoin(otbl, rtbl, jtbl, ord, jrd):

        s= "JOIN %s ON %s" % (rtbl, 
           _A(
            [" %s.%s = %s.%s " % (otbl, k, rtbl, v)
                for k, v in ord.iteritems()]))

        r= "JOIN %s ON %s" % (jtbl, 
           _A(
            [" %s.%s = %s.%s " % (jtbl, k, rtbl, v)
                for k, v in jrd.iteritems()]))

        return s + r

    @staticmethod
    def _sqlJoin(j_tbl, r_tbl, j_key, r_key):
        """ _sqlJoin(j_tbl, r_tbl, j_key, r_key) --> str

        Returns the join query.
        """

        s= "JOIN %s ON %s" % (r_tbl, 
           _A(
            [" %s.%s = %s.%s " % (r_tbl, v, j_tbl, k)
                for k, v in j_key.iteritems()]))

        s+=" WHERE "
        s+=_A(
            ["%s.%s = %s " % (r_tbl, v, _DbMap._mo_arg_format % k)
                for k, v in r_key.iteritems()])

        return s

    def _arg_format(self, k):
        f= _DbMap._mo_arg_format
        return f % k

    def _unvaluedPKeys(self):
        """ _unvaluedPKeys() --> set

        Returns the set of pkeys not valu'ed.
        NOTE: a pkeys is considere NOT VALUED if his value is 
        DEFAULT or NULL.
        """

        s=self._store
        return set([                \
            k for k in self.pkeys   \
            if not s.has_key(k)     \
            or s[k] in self._mo_false_values])

    def _invalidFields(self,fields):
        """ _invalidFields(fields) --> set

        field in fields are returned if they are not present
        in self.fields.
        """

        if type(fields) is not set:
            fields= set(fields)
        return fields - self.fields

    def _fieldsMissing(self):
        """ _fieldsMissing() --> set

        Returns the list of table fields not valu'ed yet.
        """
        return self.fields - set(self._store.keys())

    def _sqlJoinParent(self, builder, j_builder, outer= False):
        """ _sqlJoinParent(self, builder, j_builder [, outer= False]) --> (string, string)

        Returns a filter and the table where filter has to be applied.
        """

        tbl= builder.table_name
        j_tbl= j_builder.table_name

        if not self._isChildOf(j_tbl, tbl):

            try:
                j_tbl= self._searchRelation([tbl, j_tbl])
            except:
                self.log_int_raise('_sqlJoinParent: no way to join |%s| with |%s|.',
                                    ERR_COL(j_tbl), ERR_COL(tbl))

        m_d= self.getChildDeps(j_tbl, builder)

        if outer:
            s=" LEFT OUTER JOIN %s on " % j_tbl
        else:
            s=" JOIN %s on " % j_tbl

        s+=_A([" %(tbl)s.%(k)s = %(j_tbl)s.%(v)s " % locals() 
                                for k, v in m_d.iteritems()])

        return s, j_tbl

    def _getRelationObject(self, builders):
        """ _getRelationObject(builders): --> MotherFly

        builders is a list of table names.
        """
        
        rel_tbl_name= self._searchRelation(builders+ [self.table_name])

        # Return a builder with MotherOnTheFly.
        rel_obj= getMotherObj(rel_tbl_name, session= self.session)
        return rel_obj

    def getChildDeps(self, tbl_name, father= None):
        """ getChildDeps(self, tbl_name [, father= None]) --> dict

        Wich fields in TABLE tbl_name will be inherited from father?
        Returned dict is the mapping_dict.
        If father is None, self is assumed.
        """

        father= father or self
        tbl= father.table_name

        # Load father children.....
        d= self._table_children(tbl)

        # Get the dependencies for child tbl_name
        try:
            dd= d[tbl_name].copy()
        except:
            self.log_int_raise(\
                "Child %s not specified for table %s.",\
                    ERR_COL(tbl_name),ERR_COL(tbl))

        return dd

    def _getDepDict(self, mapping_dict, father= None):
        """_getDepDict(mapping_dict [,father= None]): ---> dict

        Given the dependencies mapping_dict, a new dict is created,
        filled and returned with father values.
        If father is None, self is assumed.
	    Note: mapping_dict is {key_child: key_father}
        """

        father= father or self

        self.log_insane( 
                "Exporting values %s ",
                str(mapping_dict))
                        
        fkeys= set(mapping_dict.keys())

        try:
            d= father.getFields(fkeys)
        except Exception, s:
            self.log_int_raise("Cannot inherit needed values from father: %s.",
                    ERR_COL(list(fkeys)))
            
        new_d={}
        for mapkey, mapped_key in mapping_dict.iteritems():
            #mapped_field= mapped_key
            new_d[mapped_key]= d[mapkey]
            #new_d[mapkey]= d[mapkey]

        return new_d

    def _fillChildDict(self, child_obj, father= None):
        """_fillChildDict(child_obj [,father= None]) --> None
        Given a child object, his store is updatetd with
        father dependencies. If father is None, father= self.
        """
        
        father= father or self
        ct= child_obj.table_name
        
        # Ge dependencies ...
        d= self.getChildDeps(ct,father)
        # Create new dict ...
        new_d= self._getDepDict(d,father)
        # Init child with new_dict
        child_obj.setFields(new_d, safe_mode= False)

        self.log_insane( 
                "Child object(%s) updated with values %s.",\
                OKI_COL(ct),OKI_COL(new_d))
#
##
### The Mother Class
##
#

class DbMother(_DbMap):
    """ The Holy MoThEr 
        An abstract class which represents a db Table.
    """
    _mo_arg_format= None
    _mo_initialized= False
    _mo_cfile= None
    _mo_false_values= [SQL_NULL, SQL_DEFAULT]
    _mo_session_name= "MoSession-"
    _mo_pg_oids= False
    _mo_flags= { 
            MO_NOA: 'MO_NOA', 
            MO_DEL: 'MO_DEL', 
            MO_UP: 'MO_UP', 
            MO_SAVE: 'MO_SAVE', 
            MO_LOAD: 'MO_LOAD', 
            }
        
    def __init__(self, store= {}, flag= MO_NOA, session= None):
        """ __init__(dict_values, flag, session)
        """

        self.log_int_raise(ERR_COL("Mother not Initialized yet."))

    def __post_init__(self, store= {}, flag= MO_NOA, session= None):
        """ __init__(dict_values, flag, session)
        """

        # table_name is needed...
        if not hasattr(self, 'table_name'):
            self.log_int_raise("No table_name defined for this Mother.")

        # Useful var
        tbl= self.table_name

        # Session() ?
        iface= session or DbOne
        iface.export_iface(self)
        self.session= session

        #if hasattr(self._iface_instance, '_mogrify'):
            #self.mogrify= self._iface_instance._mogrify

        # self.fields is a list with TABLE fields.
        # self.pkeys is a list with primary keys for the TABLE.
        # You can set these vars in the child class or let
        # MoThEr assign them dynamically.
        if not hasattr(self, "fields"):
            self.fields = self._table_fields(tbl)
           
        if not hasattr(self, "pkeys"):
            self.pkeys = self._table_pkeys(tbl)

        # Frozeset!
        self.fields= frozenset(self.fields)
        self.pkeys= frozenset(self.pkeys)

        # Storing dict values with some controls depending on the 
        # initialization flag....
        self._initStore(store, flag)
        # ... and enjoy ;)

    def __str__(self):
        """ __str__() --> string 
        """
        u= INF_COL("Unset")
        res= "  Table |%s|\n\n" % self.table_name
        sget= self._store.get
        for k in self.fields:
            val= sget(k,u)
            sep= k in self._moved and '*' or '~'
            res+= ("  %12s %s %s\n" % (k,sep,str(val)))
        return res

    def _initStore(self, store, flag):
        """ _initStore(store, flag) --> None

        Inizialization of self._store depending on flag.
        """

        # Controls: trivial
        setK= set(store.keys())
        accio= self._invalidFields(setK)
        if accio:
            self.log_int_raise("Invalid Fields %s for table |%s|.",\
                                ERR_COL(list(accio)), self.table_name)

        self._moved= set([])
        self._store= store.copy()

        # Signal Mother that passed fields are
        # new fields 
        self._moved= set([k for k in setK if k not in self.pkeys])

        self._flag_actions(self, flag)()

    def _paranoid(self):
        return getattr(self, 'paranoid', False)

    def setParanoia(self):
        setattr(self, 'paranoid', 1)

    def unsetParanoia(self):
        setattr(self, 'paranoid', 0)


#
##
### Sql Formatting
##
#

    def _sqlUpdate(self, d):

        res= []
        s= self._store
        tbl= self.table_name
        af= self._arg_format
        for k in d:
            v= s.get(k, SQL_DEFAULT)

            if v== SQL_DEFAULT:
                res.append('%s= DEFAULT' %  k)

            elif v == SQL_DEFAULT:
                res.append('%s = NULL' %  k)

            else:
                res.append('%s= %s' % (k, af(k)))

        pk= self.pkeys

        qry= 'UPDATE %s SET %s' % (self.table_name, _J(res))

        # table without a pkey
        if not pk:
            ftr_keys= [k for k in self._store if k not in d]
            if not ftr_keys:
                self.log_int_raise('There is no key to build '
                                   'the WHERE statement.')
            ftr= MoFilter(ftr_keys, tbl, s)
            self.oc_query(qry, ftr)
            return 

        # table with pkey
        upk= self._unvaluedPKeys()
        if not upk:
            ftr= MoFilter(self.pkeys, tbl, s)
            self.oc_query(qry, ftr)
            return 

        if self._paranoid():
            self.log_int_raise('%s: writing-queries are forbidded '
                               'without the primary key', 
                                ERR_COL('Paranoid Mother Class'))
        ftr_keys= [k for k in self._store if k not in d]
        if not ftr_keys:
            self.log_int_raise('There is no key to build '
                               'the WHERE statement.')
        ftr= MoFilter(ftr_keys, tbl, s)
        self.oc_query(qry, ftr)
        return 

    def _sqlInsertCommon(self):

        s= self._store

        res= []
        for k, v in s.iteritems():

            if v== SQL_DEFAULT:
                res.append('DEFAULT')
            if v== SQL_NULL:
                res.append('NULL')
            else:
                res.append('%s' % self._arg_format(k))

        qry= ("INSERT INTO %s (%s) VALUES (%s) " % 
                (self.table_name, _J(s), _J(res)))

        return qry

    def _sqlPostgresInsert(self):

        qry= self._sqlInsertCommon()
        pk= self.pkeys
        upk= pk and self._unvaluedPKeys() or None
        ftr= self._store
        if not len(pk) or not upk:
            self.oc_query(qry, ftr)
            return

        # we need to recover the pkey
        if not self._mo_pg_oids:
            qry+= 'RETURNING %s' % _J(upk)
            res= self.or_query(qry, ftr)
            self._store.update(res)
            return

        self.oc_query(qry, ftr)
        oid= self.lastrowid()
        res= self.or_query(
                'SELECT (%s) FROM %s WHERE '
                'oid= %d' % (_J(upk), 
                self.table_name, oid))

        self._store.update(res)
        return

    def _sqlSqliteInsert(self):

        qry= self._sqlInsertCommon()
        pk= self.pkeys
        upk= pk and self._unvaluedPKeys() or None
        ftr= self._store
        if not len(pk) or not upk:
            self.oc_query(qry, ftr)
            return

        # we need to recover the pkey
        self.oc_query(qry, ftr)
        oid= self.lastrowid()
        res= self.or_query(
                'SELECT (%s) FROM %s WHERE '
                'oid= %d' % (_J(upk), 
                self.table_name, oid))

        self._store.update(res)
        return

    def _sqlInsert(self):
        self.log_int_raise(
                ERR_COL('!!! Mother Not Initialized !!!'))

    def _sqlDelete(self, params= None):

        pk= self.pkeys
        if not pk:
            if not len(self._store):
                self.log_int_raise('There is no key to build '
                                   'the WHERE statement.')
            ftr= MoFilter(self._store, self.table_name)
            self.oc_query('DELETE FROM %s' % 
                    self.table_name, ftr)
            return

        upk= self._unvaluedPKeys()
        if not upk:
            ftr= MoFilter(pk, self.table_name, self._store)
            self.oc_query('DELETE FROM %s' %
                    self.table_name, ftr)
            return

        if self._paranoid():
            self.log_int_raise(ERR_COL('Paranoid Mother Class: '
                               'writing-queries are forbidded '
                               'without the primary key'))

        if not len(self._store):
            self.log_int_raise('There is no key to build '
                               'the WHERE statement.')
        ftr= MoFilter(self._store, self.table_name)
        self.oc_query('DELETE FROM %s' %
                self.table_name, ftr)
        return

    def _sqlSelect(self, d):

        s= self._store
        if not len(s):
            self.log_int_raise('There is no key to build '
                               'the WHERE statement.')

        tbl= self.table_name
        ftr= MoFilter(self._store, self.table_name)
        d= d or self.fields
        what= ['%s.%s' % (tbl, f) for f in d]

        res= self.or_query("SELECT %s FROM %s " % 
                (_J(what), tbl), ftr)
        self._store.update(res)
        return

#
##
### Core
##
#
    # safe transactions: the behaviour of Mother
    # Sessions is different from the persistent 
    # connections: with the version 0.5.2, commit()
    # are allowed on MotherSessions.
    #
    # A beginTrans, ignored inside sessions, 
    # followed by a commit(), is a little
    # disaster, because if we are inside Sessions,
    # this causes the commit() of the entire session.
    #
    # When we are on the persistent connection, instead,
    # the beginTrans increment the transaction counter
    # and the commit() simply recover the counter.
    #
    # So, we need the following three wrappers to handle
    # the two different situations in the same way.
    #
    # By using them, the result is always the expected
    # result: inside sessions, the commit is not made.
    # With a persistent connection, the counter is 
    # incremented and decremented so that it's always 
    # the user that decides the moment of the commit().
    #
    # Note that these are not public: these wrappers have
    # to be used only inside DbMother.

    def _safeBeginTrans(self):
        if not self.session:
            self.beginTrans()

    def _safeRollback(self):
        if not self.session:
            self.rollback()

    def _safeCommit(self):
        if not self.session:
            self.commit()

    def setField(self, field_name, field_value):
        """ setField(field_name, field_value) --> None

        set field. If field is an invalid field, CRASH.
        """

        # Pkeys cannot be changed! It's a non-sense.
        # If you want insert a new record, create new MoThEr 
        # If you want to load a different record, use refresh()
        if field_name in self.pkeys:
            self.log_int_raise(
                " Safe behaviour: you can not change Pkeys Value. "
                "Want to load a new record? Use refresh() "
                "Want to update a Pkey? Create new and delete old."
                )

        if field_name not in self.fields:
            self.log_int_raise("Mth: cannot setField(): field "
                    "%s is invalid.",ERR_COL(field_name))

        # Ok, new value is good
        self._store[field_name]=field_value
        # Remember that a field is changed.
        self._moved.add(field_name)

    def setFields(self, fdict, safe_mode= True):
        """ setFields(fdict [,safe_mode= True]) --> None

        Update the store with fdict. 
        If `safe_mode`, it will be forbidden to change 
        primary keys value. Really, use safe_mode iff
        you know exactly what are you doing.

        """
        # Is fdict a valid dict?
        new_fields=set(fdict.keys())
        onzo= self._invalidFields(new_fields)
        if onzo:
            self.log_int_raise("Mth: cannot setFields(): "
                    "invalid fields %s.", ERR_COL(str(onzo)))

        # Cannot change pkeys
        if safe_mode:
            sp=self.pkeys
            if sp & new_fields:
                self.log_int_raise(
                    "For your safety, you can not change Pkeys Value. "
                    "Want to load a new record? Use refresh(). "
                    "Want to update a Pkey? Create new and delete old. "
                    "If you know what you do, use safe_mode=False. "
                    )

        # Ok, new values are good.
        self._store.update(fdict)
        # Remember fields changed.
        self._moved |= new_fields

    def getField(self, field, autoload= False):
        """ getField(field [, autoload= False]) --> value 

        Returns the value of the field `field`, if valued.
        If field is not valued yet, and autoload is True,
        the value is loaded from the database automatically.
        Otherwise, if autoload is False, CRASH!
        """

        if field in self._store:
            return self._store[field]

        if field not in self.fields:
            self.log_int_raise('Invalid field %s for table |%s|', 
                    ERR_COL(field), ERR_COL(self.table_name))

        if not autoload:
            self.log_int_raise("Mth: field %s is not valued: use autoload= True "
                               "to load it automatically from the table |%s|.",
                               ERR_COL(field), ERR_COL(self.table_name))

        lfield= [field]
        onzo= self._invalidFields(lfield)
        if onzo:
            self.log_int_raise("Mth: cannot getField(): "
                               "invalid field %s for table |%s|", 
                                ERR_COL(str(field)), ERR_COL(self.table_name))

        self.load(lfield)
        return self._store[field]

    def getFields(self, fields= None, autoload= False):
        """ getFields([fields=None,autoload=False]) --> dict

        Returns stored values.
        If fields is not None, returns values for fields specified.
        If a field is invalid, CRASH.
        If a field is unvalued:
            if autload: load
            if not autoload: CRASH
        """

        if fields is None:
            return self._store.copy()

        onzo= self._invalidFields(fields)
        if onzo:
            self.log_int_raise("Mth: cannot getFields(): "
                    "invalid fields %s.", ERR_COL(str(onzo)))
        newd= {}
        if autoload:
            skeys= set(self._store.keys())
            nkeys= set(fields)
            lkeys= nkeys - skeys
            if len(lkeys):
                self.log_insane("Autoloading fields %s...", INF_COL(lkeys))
                self.load(lkeys)
            
        for f in fields:
            try:
                val= self._store[f]
                newd[f]= val
            except:
                self.log_int_raise(
                    "Mth: field %s is not valued.",
                        ERR_COL(f))
        return newd

    def _insert(self):

        qry= self._sqlInsert()
        self._moved.clear()

    def _update(self, updict= None):

        # Really need to update?
        if not self._moved:
            self.log_info("nothing to update.")
            return

        qry= self._sqlUpdate(self._moved)

        self.log_insane( "Mth: fields %s moved ;)",
                OKI_COL(self._moved))

        # Nothing has to be updated now.
        self._moved.clear()

    def _delete(self):

        qry= self._sqlDelete()

        # Delete all informations...  
        self._moved.clear()
        #self._store.clear()

    def _load(self, fields= None):

        # Which fields we need?
        mf= fields and set(fields) or set(self._fieldsMissing())

        if not mf <= self.fields:
            from mother.eccez import SelectError
            self.log_raise("Invalid Fields %s for table %s.",
                    ERR_COL(list(mf - self.fields)), 
                    self.table_name, SelectError)

        if not len(mf):
            self.log_warning("No field has to be SELECTed: table %s",
                        ERR_COL(self.table_name))
            return self.getFields()

        qry= self._sqlSelect(mf)

        self._moved-= mf

        # Useful return, that's all
        return self.getFields()

    def delete(self):
        """ delete() --> None

        Really do you want to kill me?
        """
        self._delete()
        self.log_info("Action %s.", OKI_COL("completed"))
    
    def load(self, fields= None):
        """ load([fields= None]) --> dict

        Retrieve record values from DB. 
        if fields is not None, only fields specified will
        be loaded.
        """
        res= self._load(fields)
        self.log_info("Action %s.", OKI_COL("completed"))
        return res

    def insert(self):
        """ insert() --> None

        Insert to db the values stored in store.
        For field with no value, SQL_DEFAULT is assumed.
        """
        self._insert()
        self.log_info("Action %s.", OKI_COL("completed"))
        
    def update(self, updict= None):
        """ update([updict= None]) --> None

        Make a UPDATE statement for modified fields and/or updict.
        If updict is None, only fields setted with setField(s) are
        moved. Otherwise, also fields specified in the dict updict 
        are considered.
        """
        if updict:
            self.setFields(updict)

        self._update()
        self.log_info("Action %s.", OKI_COL("completed"))

    def refresh(self, d, flag= MO_NOA):
        """ refresh(d[,flag=MO_NOA]) --> None

        Reinitialize this instance. The session is preserved. 
        """
        # init store.
        self._initStore(d, flag)


class MotherFly(DbMother):

    def __init__(self, tbl):
        self.table_name= tbl

    def __call__(self, d= {}, flag= MO_NOA, session= None):
        DbMother.__init__(self, d, flag, session)
        return self


def getMotherBuilder(tbl):
    """ getMotherBuilder(tbl_name) --> class

    Returns a `MoThEr Builder On The Fly` Class.
    You can init the class with a simple call:

        momma= getMotherBuilder(table)
        momma(mydict, myflag)
    """
    momma= MotherFly(tbl)
    return momma


def getMotherObj(tbl, d={}, flag= MO_NOA, session= None):
    """ getMotherObj(tbl_name[, diz= {}, flag= MO_NOA, session= None]) --> obj

    Initialize and return a `MoThEr On The Fly` Instance.
    """
    momma= getMotherBuilder(tbl)
    momma(d, flag, session)
    return momma

#
##
### The MoThEr Manager
##
#
#
##
###
#
# You can use the manager plugin to handle a set
# of child records, and to handle relations in a 
# magic way
# To use it, specify the dependencies:
#
#   class Foo(DbMother,MotherManager):
#       def __init__(self,.....):
#           DbMother.__init__(self,...
#
# but don't init the manager.
# You will have a set of useful functions.
# If you want more magic, you can run:
#
#   initChildManager(children_list)
#   initRelationManager(children_list)
#
###
##
#



class MotherManager:
    """ Mother Manager-Plugin. Need Mother."""

#
##
### Internal use.
##
#

    def _workChild(self, child_builder, child_dict, flag):
    
        # Build obj...
        new_obj= child_builder(child_dict, session= self.session)
            # Inherit father fields...
        self._fillChildDict(new_obj)
                # Get properly function...
        f= new_obj._flag_actions(new_obj, flag)
                    # Get some debugging vars
        tbl= new_obj.table_name
        sd= str(new_obj.getFields())
        s= self._mo_flags[flag]
                # Execute function....
        f()
            # Debug
        self.log_insane( 
                "%s child %s, values %s",
                s,tbl,sd)

        return new_obj
        # Return ;)

      
#
##
### Public
##
#

    def getChild(self, cbuilder, c_dict):
        """ getChild(cbuilder, c_dict): --> MotherObj
        """
        return self._workChild( 
                                cbuilder,
                                c_dict,
                                MO_LOAD,
                              )
                                    

    def insertChild(self, cbuilder, c_dict):
        """ insertChild(child_builder, c_dict) -> MotherObj
        insert new child object and return it.
        """
        return self._workChild( 
                                cbuilder,
                                c_dict,
                                MO_SAVE,
                              )

    def updateChild(self,cbuilder,c_dict):
        """ updateChild(cbuilder, c_dict): --> MotherObj
        """
        return self._workChild( 
                                cbuilder,
                                c_dict,
                                MO_UP,
                              )
        
    def deleteChild(self,cbuilder,c_dict):
        """ deleteChild(cbuilder, c_dict): --> MotherObj
        """
        return self._workChild( 
                                cbuilder,
                                c_dict,
                                MO_DEL,
                              )
    def handleManyChildren(self, cbuilder, flag, c_dicts, fields= None):

        child_table= cbuilder.table_name
        d= self.getChildDeps(child_table)
        d= self._getDepDict(d)
        for c in c_dicts:
            c.update(d)
        return MotherMany(cbuilder, c_dicts, flag, self.session, fields= fields)

    def deleteChildren(self, cbuilder, filter= None):
        """ deleteChildren(cbuilder [,filter=None]) --> None
        
        Delete a set of children, filtered with filter.
        If filter is None, delete all children.
        cbuilder is a Mother class for the table where records
        wil be deleted.
        """
        child_table= cbuilder.table_name
        d= self.getChildDeps(child_table)
        d= self._getDepDict(d)

        ftr= MoFilter(d, child_table)
        if filter:
            ftr.add_filter(filter, child_table) 

        MotherBox(cbuilder, ftr, MO_DEL, session= self.session)

    def updateChildren(self, cbuilder, d_up, filter= None):
        """ updateChildren(self, cbuilder, d_up [, filter= None]) --> None

        Update children with dict d_up.
        If filter, update only filtered children.
        cbuilder is a Mother class for the table.
        """
        child_table= cbuilder.table_name
        d= self.getChildDeps(child_table)
        d= self._getDepDict(d)

        # Build filter
        ftr= MoFilter(d, child_table)
        if filter is not None:
            ftr.add_filter(filter, child_table) 

        MotherBox(cbuilder, flag=MO_UP, fields= d_up, 
                filter= ftr, session= self.session) 

    def getChildren(self, cbuilder, fields= None, filter= None,\
                    jbuilder= None, jfilter= None,
                    outer= False, order= None):
        " getChildren(cbuilder [,fields= None, filter= None, "\
        " jbuilder= None, jfilter= None, outer= False, order= None])-->box\n" \
        """
        fields = list of fields names
        filter = string or dictionary
        jbuilder = builder class which will be joined
        jfilter = string or dictionary about join table fields
        outer = boolean, will be a left outer join
        order = list(fields)
        """

        child_table= cbuilder.table_name
        # Get dependencies dict...
        d= self.getChildDeps(child_table)
        d= self._getDepDict(d)

        # If a join filter is specified, we need
        # to build the JOIN STATEMENT before the WHERE
        qry_filter, joining_table= jbuilder and               \
            self._sqlJoinParent(cbuilder, jbuilder, outer) or \
                ('', '')

        # Build SQL filter string
        tbl= joining_table or None
        ftr= MoFilter(qry_filter, tbl= tbl)

        # now filter father dependencies
        ftr.add_filter(d, child_table)

        # Filter join condition
        # Note that the filter is used on the joined table
        # that is returned by _sqlJoinParent
        if jbuilder and jfilter:
            ftr.add_filter(jfilter, joining_table)

        # if filter is specified, use it ...
        # the filter `filter` is used on Child Table.
        if filter is not None:
            ftr.add_filter(filter, child_table)

        # Let's use a MotherBox :)
        # If join use DISTINCT
        distinct= (jbuilder is not None)
        mb= MotherBox(cbuilder, filter= ftr, flag= MO_LOAD,
                        fields= fields, order= order, distinct= distinct, 
                        session= self.session)
        # Oh yes, return ;)
        return mb

    def assignRelation_nt(self, builder_list, params= {}):
        """ """

        # Handle given objects ...
        builders= []
        fathers= []
        self.log_insane("Creating auto-relation...")

        for builder, d, flag in builder_list:
            tbl= builder.table_name
            builders.append(tbl)
            flag_str= self._mo_flags[flag]
            self.log_insane(
                    "Working record in %s with "\
                    "values %s and flag=%s...",\
                    INF_COL(tbl),INF_COL(str(d)),flag_str)
            try:
                new_obj= builder(d, flag, session= self.session)
                fathers.append(new_obj)
            except Exception,s:
                es=("Error! %s initialization returned: %s."\
                              " Now Rollback!" % (flag_str,ERR_COL(str(s))))
                self.log_error(es)
                self.log_int_raise("Unable to assign child: %s",es)

        self.log_insane( 
                "%s child(ren) assigned, now work on "\
                "relation...", OKI_COL(len(builders)))

        # create auto relation ...
        # init child object 
            
        # self.table_name is added automatically
        r_obj = self._getRelationObject(builders)

        # Let child take his values from fathers...
        for father in [self]+fathers:
            self._fillChildDict(r_obj, father)
        r_obj.setFields(params, safe_mode=False)

        # store it to DB
        try:
            r_obj.insert()
        except Exception,s:
            self.log_error("Error! insert() returned: %s."\
                                " Now Rollback!",ERR_COL(str(s)))
            self.log_int_raise("Error adding auto-relation.") 

        # All was fine.
        self.log_insane( 
                "Relation %s auto-saved with "\
                "values %s.",r_obj.table_name,\
                OKI_COL(str(r_obj._store)))

        return tuple(fathers)

    def assignRelation(self, builder_list, params= {}):
        """ assignRelation(self, builder_list [,params= {}]) --> Tuple

        assign a Relation.
        builder_list is a list of tuples:

            [(MotherBuilder,dict,flag)...]

        If TABLE A and TABLE B are related with the relation TABLE
        R_AB, you can (pseudo-code):

            me= Mother(A)
            builder_list=[(B, dict, MO_SAVE)]
            me.assignRelation(builder_list)

        With this call, create a record in B and put in R_AB the 
        relation.
        If the relation accept other fields, specify them in params,
        which is a dict.
        """

        self._safeBeginTrans()
        try:
            res= self.assignRelation_nt(builder_list, params)
        except Exception, s:
            self._safeRollback()
            raise Exception(s)

        self._safeCommit()
        return res
            
    def dropRelation(self, builder_list, params= {}):
        """ dropRelation(self, builder_list [,params= {}]) --> list

        Drop relation between father in builder_list.
        builder_list is [(builder,dict,flag),...]
        """
        fathers=[]
        fathers_del=[]
        # Create the list of only builders
        for builder, d, flag in builder_list:
            new_obj= builder(d, session= self.session)
            fathers.append(new_obj)
            if flag == MO_DEL:
                fathers_del.append(new_obj)

        # create auto relation init child object
        t_names= [ o.table_name for o in fathers ]
        r_obj = self._getRelationObject(t_names)
        
        # Let child take his values from fathers...
        for father in [self] + fathers:
            self._fillChildDict(r_obj, father)

        r_obj.setFields(params)
        r_obj.delete()
        self.log_insane("Dropped relation %s",\
                OKI_COL(r_obj.table_name))
        # Destroy all fathers with flag MO_DEL
        for f in fathers_del:
            f.delete()
        return fathers
    
    def dropRelations(self, builder, filter= None, jfilter= None, r_tbl= None, flag= MO_NOA):
        """ dropRelation(builder [,filter=None, r_tbl= None, flag= MO_NOA]):

        drop all related records.
        If r_tbl is specified, use that table to join records,
        otherwise, r_tbl is deduced.

        fIlter is.. a filter. It applies to the relation table.
        jfIlter is.. a filter. It applies to the related table.
        """

        mbox= self.joinRelation(builder, filter= filter, jfilter= jfilter, r_tbl= r_tbl)

        self.log_insane( 
                "%s is dropping %s relation(s) ...",
                INF_COL(self.table_name), INF_COL(len(mbox)))

        ds= mbox.getRecords()
        for d in ds:
            self.dropRelation([(builder, d, flag)])

    def joinRelation(self, builder, fields= [], filter= None, jfilter= None, r_tbl= None, order= None):
        """ joinRelation(self, builder, fields= [], filter= None, jfilter= None, r_tbl= None, order= None) -> Box

        Get related data.
        Builder is the MotherBuilder for data to be searched.

        filter applies to the relation table.
        jfilter applies to the related table.

        r_tbl is the relation table used for the join. If not given,
        r_tbl is obtained automaically.
        if order is not None, the query will be ordered by fields in that list.
        """

        # Useful vars
        s_tbl= self.table_name
        b_tbl= builder.table_name

        # Try to get relation table....
        # If there is ambiguity, CRASH!
        if r_tbl is None:
            r_tbl= self._searchRelation([s_tbl, b_tbl])

        # Ok, the relation table is found
        # Getting the mapping child dicts
        s_d = self.getChildDeps(r_tbl)
        b_d = self.getChildDeps(r_tbl, builder)
        
        # If fields is not specified, fields for the
        # serached table are retrieved 
        if fields== []:
            fields= self._table_fields(b_tbl)

        self.log_insane("Joining %s and %s with relation %s "
                        "and fields %s ...",s_tbl,b_tbl,
                        INF_COL(r_tbl),INF_COL(str(fields)))
                        
        # Make the base filter query ...
        qry_filter = self._sqlJoin(b_tbl, r_tbl, b_d, s_d)
        ftr= MoFilter(qry_filter, store= self._store)

        # If filters are given, apply it.
        if filter:
            ftr.add_filter(filter, r_tbl)
        if jfilter:
            ftr.add_filter(jfilter, b_tbl)

        # get a MotherBox
        mb= MotherBox(builder, ftr, MO_LOAD, fields, order, 
                    distinct= 1, session= self.session)
        return mb

    def relParams(self, related, fields= None, flag_obj= False):
        """ relParams(self, related, [fields= None, flag_obj= False]) -> dict or Mother Object

        Returns, depending on flag_obj, a dict or  a Mother Object representing 
        the relation record between `self' and related records.
        `related' is a list of related records (Mother Objects).
        if `fields' is not None, only these fields will be loaded."""

        btbls= [b.table_name for b in related]

        # self.table_name is added automatically
        r_obj = self._getRelationObject(btbls)

        # Let child take his values from fathers...
        for father in [self] + related:
            self._fillChildDict(r_obj, father)

        r_obj.load(fields= fields)

        if flag_obj: return r_obj
        else: return r_obj.getFields()

    def initManyManager(self, children= None):
        """initManyManager(self [, children= None]) --> None
        
        Calling this method, a family of function will be created
        inside your Mother instance: the ManyManager family.

        `children` is a list or None.
        If None, for each table child the following methods will be created:

            insertMany<Child>
            deleteMany<Child>
            updateMany<Child>
            loadMany<Child>

        `children` can also be a list of table names. For each table
        the same methods will be created.

        Finally, `children` can be a list of DbMother classes: this is
        useful, because it's possible to handle children using your
        custom DbMother classes.

        * NOTE: methods already defined are not overwritten.
        """

        self.log_info("The initManyManager() methods are not tested deeply: if You "\
                      "encounter bugs, don't panic: please, signal them.")

        if not children:
            children= [getMotherBuilder(c) 
                    for c in self._table_children(self.table_name)]
        else:
            children= [isinstance(c, str) and getMotherBuilder(c) 
                        or c for c in children]

        def handle_children(builder, flag):
            def fly_handle_children(dlist, fields= None):
                return self.handleManyChildren(builder, flag, dlist, fields)
            return fly_handle_children

        camel= DbMother.MotherNaming

        map_names= {
                MO_LOAD: 'loadMany', 
                MO_SAVE: 'insertMany', 
                MO_UP: 'updateMany', 
                MO_DEL: 'deleteMany'
                }

        for c in children:
          ctbl= c.table_name
          for flag, name in map_names.iteritems():

            attr_name= camel(ctbl, name)
            if not hasattr(self, attr_name): 

              attr= handle_children(c, flag)
              if flag in [MO_UP, MO_LOAD]:
                attr.__doc__=\
                  " %s(dlist [, fields= None) --> MotherMany instance\n\n"        \
                  "handle many children. dlist is a list of dicts, "              \
                  "fields is a list of strings.\n"                                \
                  "Don't specify the foreign key: it's assigned automatically.\n" \
                      % attr_name
              else:
                attr.__doc__=\
                  " %s(dlist) --> MotherMany instance\n\n"                        \
                  "handle many children. dlist is a list of dicts.\n"             \
                  "Don't specify the foreign key: it's assigned automatically.\n" \
                      % attr_name

              setattr(self, attr_name, attr)

    def initChildManager(self, children= None):
        """initChildManager(self [, children= None]) --> None

        Calling this method, a family of function will be created
        inside your Mother instance: the ChildManager family.

        `children` is a list or None.
        If None, for each table child the following methods will be created:

            insert<Child>
            get<Child>
            deleteMultiple<Child>
            updateMultiple<Child>
            getMultiple<Child>

        `children` can also be a list of table names. For each table
        the same methods will be created.

        Finally, `children` can be a list of DbMother classes: this is
        useful, because it's possible to handle children using your
        custom DbMother classes.

        * NOTE: methods already defined are not overwritten.
        """

        if not children:
            children= [getMotherBuilder(c) 
                    for c in self._table_children(self.table_name)]
        else:
            children= [isinstance(c, str) and getMotherBuilder(c) 
                        or c for c in children]

        def insert_child(builder):
            def fly_insert_child(d):
                return self.insertChild(builder, d)
            return fly_insert_child

        def delete_children(builder):
            def fly_delete_children(filter= None):
                return self.deleteChildren(builder, filter)
            return fly_delete_children

        def get_child(builder):
            def fly_get_child(d):
                return self.getChild(builder, d)
            return fly_get_child

        def get_children(builder):
            def fly_get_children(fields= None, filter= None, 
                    jbuilder= None, jfilter= None, 
                    outer= False, order= None):
                return self.getChildren(builder, fields, 
                        filter, jbuilder, jfilter, 
                        outer, order)
            return fly_get_children
        
        def update_children(builder):
            def fly_update_children(d_up, filter= None):
                return self.updateChildren(builder, d_up, filter)
            return fly_update_children


        camel= DbMother.MotherNaming

        for c in children:
            ctbl= c.table_name

            attr_name= camel(ctbl, 'insert')
            if not hasattr(self, attr_name): 

                attr= insert_child(c)
                attr.__doc__=\
                        " %s(dict) --> child\n\n"                                       \
                        "insert a child. dict contains the fields values.\n"            \
                        "Don't specify the foreign key: it's assigned automatically.\n" \
                            % attr_name

                setattr(self, attr_name, attr)

            attr_name= camel(ctbl, 'deleteMultiple')
            if not hasattr(self, attr_name): 
                
                attr= delete_children(c)
                attr.__doc__=\
                        " %s(filter= None) --> None\n\n"                                \
                        "delete children. if filter is None, delete ALL children.\n"    \
                        "Don't specify the foreign key: it's assigned automatically.\n" \
                            % attr_name

                setattr(self, attr_name, attr)

            attr_name= camel(ctbl, 'getMultiple')
            if not hasattr(self, attr_name): 
                
                attr= get_children(c)
                attr.__doc__=\
                        " %s([fields= None, filter= None, jbuilder= None, "                     \
                        "jfilter, outer= None, order= None) --> MotherBox\n\n"                  \
                        "retrieve a set of children. filter is used for the children table.\n"  \
                        "jbuilder and jfilter are used to do advanced filtering.\n"             \
                        "If outer is True, an outer join is performed.\n"                       \
                        "order is a list of fields names.\n"                                    \
                        "Don't specify the foreign key: it's assigned automatically.\n"         \
                        % attr_name

                setattr(self, attr_name, attr)

            attr_name= camel(ctbl, 'get')
            if not hasattr(self, attr_name): 
                
                attr= get_child(c)
                attr.__doc__=\
                        " %s(dict) --> DbMother\n\n"                                    \
                        "retrieve a unique child.\n"                                    \
                        "Here dict acts has a filter and does not have to contain\n"    \
                        "the primary key for your record.\n"                            \
                        "If a unique record is not found, an exception will be raised." \
                        "Don't specify the foreign key: it's assigned automatically.\n" \
                        % attr_name

                setattr(self, attr_name, attr)

            attr_name= camel(ctbl, 'updateMultiple')
            if not hasattr(self, attr_name): 
                
                attr= update_children(c)
                attr.__doc__=\
                        " %s(d_up, filter= None) --> None\n\n"                                      \
                        "update children. the dict d_up contains the fields (and their values)\n"   \
                        "to be updated. The filter is a usual filter.\n"                            \
                        "Don't specify the foreign key: it's assigned automatically.\n"             \
                        % attr_name

                setattr(self, attr_name, attr)

    def initRelationManager(self, rels):

        """initRelationManager(self, rels) --> None

        Calling this method, a family of function will be created
        inside your Mother instance: the RelationManager family.

        `rels` is a list of DbMother classes or table names.
        For each related table, the following methods will be created:

            assign<Rel>
            join<Rel>
            drop<Rel>
            dropMultiple<Rel>
            updateMultiple<Rel>
            parmas<Rel>

        `children` can be a list of DbMother classes: this is
        useful, because it's possible to handle related records using your
        custom DbMother classes.

        * NOTE: methods already defined are not overwritten.
        """
       
        rels= [isinstance(c, str) and getMotherBuilder(c) 
                    or c for c in rels]

        def assign_rel(builder):
            def fly_assign_rel(d, flag= MO_NOA, params= {}):
                return self.assignRelation([(builder, d, flag)], params)[0]
            return fly_assign_rel

        def drop_rel(builder):
            def fly_drop_rel(d, flag= MO_NOA, params= {}):
                return self.dropRelation((builder, d, flag), params)[0]
            return fly_drop_rel

        def drop_rels(builder):
            def fly_drop_rels(filter= None, jfilter= None, r_tbl= None, flag= MO_NOA):
                return self.dropRelations(builder, filter, jfilter, r_tbl, flag)
            return fly_drop_rels

        def join_rels(builder):
            def fly_join_rels(fields= [], filter= None, jfilter= None, r_tbl= None, order= None):
                return self.joinRelation(builder, fields, filter, jfilter, r_tbl, order)
            return fly_join_rels

        def rel_params(builder):
            def fly_rel_params(d, fields= None, flag_obj= False):
                if not isinstance(d, DbMother):
                    d= builder(d, session= self.session)
                return self.relParams([d], fields, flag_obj)
            return fly_rel_params


        camel= DbMother.MotherNaming
        stbl= self.table_name

        for rel in rels:
            rtbl= rel.table_name
            rel_tbl= self._searchRelation([rtbl, stbl])

            attr_name= camel(rtbl, 'assign')
            if not hasattr(self, attr_name):
                attr= assign_rel(rel)
                attr.__doc__=\
                    " %s(dict[,flag= MO_NOA, params= {}]) --> DbMother instance\n\n"    \
                    "Handle the Mother object with dict and flag on the table |%s|,\n"  \
                    "and, after, insert a record on the relation table |%s|.\n"         \
                    "Don't specify the foreign key: it's assigned automatically.\n"     \
                    "Return the Mother Object."                                         \
                     % (attr_name, rtbl, rel_tbl)

                setattr(self, attr_name, attr)

            attr_name= camel(rtbl, 'dropMultiple')
            if not hasattr(self, attr_name):
                attr= drop_rels(rel)
                attr.__doc__=\
                    " %s([filter, r_tbl, flag]) --> None\n\n"                           \
                    "Drop a set of relations.\n"                                        \
                    "If flag is specified, do also this action on related records.\n"   \
                    "if r_tbl is specified, use that table to make the join, \n"        \
                    "otherwise use the table |%s|.\n"                                   \
                    "Don't specify the foreign key: it's assigned automatically.\n"     \
                     % (attr_name, rel_tbl)

                setattr(self, attr_name, attr)

            attr_name= camel(rtbl, 'join')
            if not hasattr(self, attr_name):
                attr= join_rels(rel)
                attr.__doc__=\
                    " %s([fields, filter, jfilter, r_tbl, order]) --> MotherBox\n\n"          \
                    "Do a join with records in |%s|.\n"                                       \
                    "If filter is specified, apply it on the relation table.\n"               \
                    "If jfilter is specified, apply it on the related table.\n"               \
                    "If r_tbl is specified, use that as relation table to make the join,\n"   \
                    "otherwise the table |%s| will be used.\n"                                \
                    "If fields is specified, load only these fields from the joined table.\n" \
                    "Don't specify the foreign key: it's assigned automatically.\n"           \
                    "Return a MotherBox object."                                              \
                     % (attr_name, rtbl, rel_tbl)

                setattr(self, attr_name, attr)

            attr_name= camel(rtbl, 'params')
            if not hasattr(self, attr_name):
                attr= rel_params(rel)
                attr.__doc__=                                                               \
                    " %s(obj [,fields= None, flag_obj= False]) --> dict Mother Object\n\n"  \
                    "Returns, depending on flag_obj,  a dict or a Mother Object that\n"     \
                    "represents the relation between `self' and the record on the table\n"  \
                    "|%s|, which is represented by obj (a dict or a Mother Object).\n"      \
                    "If `fields' is specified, load only these fields."                     \
                    % (attr_name, rtbl)

                setattr(self, attr_name, attr)



#
##
### The MotherBox
##
#

class MotherBox(DbOne):

    def __init__(self, builder, filter= None, flag= MO_NOA, 
                    fields= None, order= None, session= None, 
                    distinct= False):

        iface= session or DbOne
        iface.export_iface(self)
        self.session= session

        self.builder= isinstance(builder, str) \
                and getMotherBuilder(builder) or builder

        self.momma= builder(session= session)
    
        if filter:
            if not isinstance(filter, MoFilter):
                filter= MoFilter(filter)
        else:
            filter= MoFilter()

        self._store= []

        if flag==MO_LOAD:
            self.loadBox(filter, fields, order, distinct)

        elif flag==MO_DEL:
            self.deleteBox(filter)

        elif flag==MO_UP:
            if not fields:
                self.log_int_raise(
                        "No fields specified to update %s.", 
                        ERR_COL(self.builder.table_name))
            self.updateBox(filter, fields)

        elif flag== MO_NOA:
            return

        else:
            self.log_int_raise("Invalid Flag %s for MotherBox", 
                    ERR_COL(flag))

        del self.momma


    def __len__(self):

        return len(self._store)

    def __iter__(self):
        for d in self._store:
            yield d

    def loadBox(self, filter, fields, order, distinct):

        tbl= self.builder.table_name

        distinct= distinct and 'DISTINCT' or ''

        sel="SELECT %(distinct)s %(what)s FROM %(tbl)s "

        if fields is None:
            what= _J(['%s.%s' % (tbl, f) for f in self.momma.fields])
        else:
            ifields= set(fields) - self.momma.fields
            if len(ifields):
                self.log_int_raise("Invalid Fields for table %s: %s",
                    tbl, ERR_COL(list(ifields)))
            what= _J(['%s.%s' % (tbl, f) for f in fields])

        qry= sel % locals()

        if order:
            filter.add_post("ORDER BY %s" % _J(order))

        self._store= self.mr_query(qry, filter)

        self.log_debug("Loaded %s records on %s",\
                OKI_COL(len(self._store)), tbl)

        self.log_info("Action %s.", OKI_COL("completed"))


    def updateBox(self, filter, d):
        """ updateBox(self, filter, d): --> None

        Update a set of records.
        """

        table= self.builder.table_name

        # sometime we have:
        #   set foo= %{foo}s where foo= %{foo}s
        # this is a problem, because %{foo}s should
        # be traslated differently.
        # This is a dirty hack to avoid the problem.
        # Just change a key name:
        #   set foo= %{up_foo}s where foo= %{foo}s

        newd= {}
        res= []
        for k, v in d.iteritems():
            newk= 'up_%s' % k
            newd[newk] = v
            if v== SQL_DEFAULT:
                res.append('%s= DEFAULT' % k)
            if v== SQL_NULL:
                res.append('%s= NULL' % k)
            else:
                res.append('%s= %s' % (k, self.momma._arg_format(newk)))

        if not filter:
            filter= MoFilter()
        filter.add_store(newd)

        what= _J(res)
        tbl= self.builder.table_name

        qry= 'UPDATE %(tbl)s SET %(what)s ' % locals()

        self.oc_query(qry, filter)
        self.log_insane("Box: Updatetd records.")

        self.log_info("Action %s.", OKI_COL("completed"))

    def deleteBox(self, filter=None):
        """ deleteBox(self, filter= None, stored= False) --> None

        delete from DB.
        If stored is True, delete stored object.
        """

        self.log_insane("Mbox: deleting with filter=%s", INF_COL(filter))

        tbl= self.builder.table_name

        self.oc_query('DELETE FROM %s' % tbl, filter)
        self.log_insane("Records deleted.")

        self.log_info("Action %s.", OKI_COL("completed"))

    def getRecords(self, flag_obj= False):
        """ getRecords(self, flag_obj= False) -> list(dict) or list(Mothers)

        The return value depends on flag_obj.
        """
        if flag_obj:
            b= self.builder
            session= self.session
            return [b(d, MO_NOA, session) for d in self._store]
        else:
            return self._store


#
##
### The Modern MotherFusion
##
#

class MotherFusion(_DbMap):

    def __init__(self, builderA, builderB, filter= None, fields= None,
                    order= None, session= None, distinct= False, 
                    rtbl= None, params= False, jfilter= None, side= ""):

        self.direct= None
        self.side= side

        builderA, builderB, fields= self.swap(builderA, builderB, fields)

        iface= session or DbOne
        iface.export_iface(self)
        self.session= session

        if filter:
            if not isinstance(filter, MoFilter):
                filter= MoFilter(filter)
        else:
            filter= MoFilter()
        self.filter= filter

        self.jfilter= jfilter

        if order:
            self.filter.add_post('ORDER BY %s' % _J(order))

        self.distinct= distinct
        self._store= []
        self.rtbl= None
        self.params= params

        self.builderA= builderA
        self.builderB= builderB
        self.tblA= ta= builderA.table_name
        self.tblB= tb= builderB.table_name

        if fields:
            self.fields= fields
        else:
            self.fields= (self._table_fields(ta), self._table_fields(tb))

        if self.direct:
            self.directJoin()
        else:
            self.rtbl= rtbl
            self.joinBuilders()

    def __iter__(self):
        for d in self._store:
            yield d

    def swap(self, a, b, fields):

        ta= a.table_name
        tb= b.table_name

        if self._isChildOf(ta, tb):

            self.direct= True

            if fields and isinstance(fields, tuple):
                fields= (fields[1], fields[0])

            return b, a, fields

        if self._isChildOf(tb, ta):
            self.direct= True

        return a, b, fields

    def __len__(self):
        return len(self._store)

    def _selectWhat(self, fields, tbl= None):

        if isinstance(fields, list):
            if tbl: 
                return _J(['%s.%s' % (tbl, f) for f in fields])
            return _J(fields)
        
        if isinstance(fields, dict):
            if tbl:
                return _J(['%s.%s AS %s' % (tbl, k, v) 
                    for k, v in fields.iteritems()])
            return _J(['%s AS %s' % (k, v) 
                for k, v in fields.iteritems()])

        # recursion
        sw= self._selectWhat

        fa= fields[0]
        fb= fields[1]

        a= fa and sw(fa, self.tblA) or '%s.*' % self.tblA
        b= fb and sw(fb, self.tblB) or '%s.*' % self.tblB

        if len(fields) == 3:
            fr= fields[2]
            r= fr and sw(fr, self.rtbl) or '%s.*' % self.rtbl
            
            return _J([a, b, r])

        return _J([a, b])


    def joinBuilders(self):

        self.log_insane('MotherFusion: join relation')
        # useful vars
        ba= self.builderA
        bb= self.builderB
        ta= ba.table_name
        tb= bb.table_name
        r_tbl= self.rtbl

        # Try to get relation table....
        # If there is ambiguity, CRASH!
        if r_tbl is None:
            self.rtbl= r_tbl= self._searchRelation([ta, tb])

        # Ok, the relation table is found
        # Getting the mapping child dicts
        a_d = self.getChildDeps(r_tbl, ba)
        b_d = self.getChildDeps(r_tbl, bb)
        
        self.log_insane("Joining %s and %s with relation %s ",
                         ta, tb, r_tbl)
                        
        # Make the base filter query ...
        qry_filter = self._sqlFreeJoin(ta, r_tbl, tb, a_d, b_d)
        ftr= self.filter
        ftr.add_filter(qry_filter)
        if self.jfilter:
            ftr.add_filter(self.jfilter, self.rtbl)

        params= self.params
        if params:
            if isinstance(params, list) or isinstance(params, dict):
                self.fields = self.fields[0], self.fields[1], params
            else:
                # exclude redundant params...
                params= [p for p in self._table_fields(r_tbl) 
                        if p not in a_d.keys() + b_d.keys()]
                # ... and add them
                self.fields = self.fields[0], self.fields[1], params

        what= self._selectWhat(self.fields)
        distinct= self.distinct and 'DISTINCT' or ''
        side= self.side
        qry= 'SELECT %(distinct)s %(what)s FROM %(ta)s %(side)s' % locals()

        self._store= self.mr_query(qry, ftr)

    def directJoin(self):

        # useful vars
        ba= self.builderA
        bb= self.builderB
        ta= ba.table_name
        tb= bb.table_name
        self.log_insane('MotherFusion: direct join: %s father, '
                        '%s child', INF_COL(ta), INF_COL(tb))

        what= self._selectWhat(self.fields)
        jfilter, joining_table= self._sqlJoinParent(ba, bb)

        distinct= self.distinct and 'DISTINCT' or ''
        side= self.side
        qry= 'SELECT %(distinct)s %(what)s FROM %(ta)s ' \
                '%(side)s %(jfilter)s' % locals()
        self._store= self.mr_query(qry, self.filter)

    def getRecords(self, flag_obj= False):

        if not flag_obj:
            return self._store

        fa= self._table_fields(self.tblA)
        fb= self._table_fields(self.tblB)
        ba= self.builderA
        bb= self.builderB
        s= self.session

        dla= []
        dlb= []
        dlr= []
        for rec in self._store:
            da= {}
            db= {}
            dr= {}

            for k, v in rec.iteritems():

                if k in fa:
                    da[k]= v
                elif k in fb:
                    db[k]= v
                else:
                    dr[k]= v

                dla.append(da)
                dlb.append(db)
                if dr:
                    dlr.append(dr)

        rt= self.rtbl
        if not rt or not dlr:
            return [(ba(a, session= s), bb(b, session= s)) 
                for a, b in zip(dla, dlb)]
        return [(ba(a, session= s), getMotherObj(rt, rd, session= s), 
                bb(b, session= s))
            for a, r, b in zip(dla, dlr, dlb)]


class MotherMany(_DbMap):

    def __init__(self, builder, store= None, flag= MO_NOA, 
                    session= None, fields= None):

        self.log_info("The MotherMany class is not tested deeply: if You "\
                      "encounter bugs, don't panic: please, signal them.")
        if isinstance(builder, str):
            self.builder= None
            self.table_name= builder
        else:
            self.builder= builder
            self.table_name= builder.table_name

        iface= session or DbOne
        iface.export_iface(self)
        self.session= session

        if isinstance(store, dict):
            store= [store]

        self.store= store
        self._act_fields= fields

        f= self._flag_actions(self, flag)
        f()

    def __len__(self):

        return len(self._records)

    def __iter__(self):

        for d in self.store:
            yield d

    def addRows(self, rows):

        try:
            self.store.extend(rows)

        except:
            if not isinstance(rows, dict):
                self.log_int_raise("Invalid rows type: %s", ERR_COL(rows))
            self.store.append(rows)

        self._records= self.store

    def insert(self):

        s= self.store
        if not s:
            self.log_info("MotherMany.insert(): empty store. Skipping")
            return 

        af= self._arg_format

        f= s[0].keys()
        fields= _J(f)
        table= self.table_name
        values= _J([af(k) for k in f])

        qry= 'INSERT INTO %(table)s (%(fields)s) VALUES (%(values)s)' % locals()
        self.log_info("MotherMany: Inserting on %s %s row(s) (template= `%s`)...", 
                        INF_COL(table), INF_COL(len(s)), INF_COL(qry))
        self.mq_query(qry, s)

        self._records= self.store


    def delete(self):

        s= self.store
        if not s:
            self.log_info("MotherMany.delete(): empty store. Skipping")
            return 

        af= self._arg_format

        fields= s[0].keys()
        table= self.table_name
        filter= _A([ "%s = %s" % (j, af(j)) for j in fields])

        qry= 'DELETE FROM %(table)s WHERE %(filter)s' % locals()

        self.log_info("MotherMany: Deleting on %s with %s filter(s) "
                      "(template= `%s`)...", table, INF_COL(len(s)), INF_COL(qry))

        self.mq_query(qry, s)
        self._records= self.store

    def update(self):

        s= self.store
        if not s:
            self.log_info("MotherMany.update(): empty store. Skipping")
            return 

        table= self.table_name
        fields= s[0].keys()
        act= self._act_fields
        if not act:
            act= [f for f in fields if f not in self._table_pkeys(table)]
        if not act or len(act) == len(fields):
            self.log_int_raise('MotherMany.update(): cannot understand what '
                                'has to be updated.')

        af= self._arg_format

        upup= _J(['%s= %s' % (f, af(f)) for f in act])
        filter= _A(['%s= %s' % (f, af(f)) for f in fields if f not in act])

        qry= 'UPDATE %(table)s SET %(upup)s WHERE %(filter)s' % locals()

        self.log_info("MotherMany: Updating %s with %s filter(s) "
                      "(template= `%s`)...", table, INF_COL(len(s)), INF_COL(qry))

        self.mq_query(qry, s)
        self._records= self.store

    def load(self):

        s= self.store
        if not s:
            self.log_info("MotherMany.select(): empty store. Skipping")
            return 

        af= self._arg_format
        fields= s[0].keys()
        table= self.table_name
        act= self._act_fields
        what= act and _J(act) or '*'
        filter= _A([ "%s = %s" % (j, af(j)) for j in fields])

        qry= 'SELECT %(what)s FROM %(table)s WHERE %(filter)s' % locals()

        self.log_info("MotherMany: Loading on %s with %s filter(s) "
                      "(template= `%s`)...", table, INF_COL(len(s)), INF_COL(qry))

        self._records= self.mg_query(qry, s)

    def getRecords(self, flag_obj= False):
        """ getRecords(self, flag_obj= False) -> list(dict) or list(Mothers)

        The return value depends on flag_obj.
        """
        if flag_obj:
            b= self.builder or getMotherBuilder(self.table_name)
            session= self.session
            return [b(d, MO_NOA, session) for d in self._records]
        else:
            return self._records
