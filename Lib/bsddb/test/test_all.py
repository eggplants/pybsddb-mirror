"""Run all test cases.
"""

import sys
import os
import unittest
try:
    # For Pythons w/distutils pybsddb
    import bsddb3 as bsddb
except ImportError:
    # For Python 2.3
    import bsddb


if sys.version_info[0] >= 3 :
    class cursor_py3k(object) :
        def __init__(self, db, *args, **kwargs) :
            self._dbcursor = db.cursor(*args, **kwargs)

        def __getattr__(self, v) :
            return getattr(self._dbcursor, v)

        def __next__(self) :
            return getattr(self._dbcursor, "next")()

        def set(self, k) :
            if isinstance(k, str) :
                k = bytes(k, "ascii")
            return self._dbcursor.set(k)

        def get(self, k, flags=0) :
            if isinstance(k, str) :
                k = bytes(k, "ascii")
            v = self._dbcursor.get(k, flags=flags)
            if v != None :
                v = v.decode("ascii")
            return v

    class DB_py3k(object) :
        def __init__(self, *args, **kwargs) :
            args2=[]
            for i in args :
                if isinstance(i, DBEnv_py3k) :
                    i = i._dbenv
                args2.append(i)
            args = tuple(args2)
            for k, v in kwargs.items() :
                if isinstance(v, DBEnv_py3k) :
                    kwargs[k] = v._dbenv

            self._db = bsddb._db.DB_orig(*args, **kwargs)

        def __getitem__(self, k) :
            if isinstance(k, str) :
                k = bytes(k, "ascii")
            v = self._db[k]
            return v.decode("ascii")

        def __setitem__(self, k, v) :
            if isinstance(k, str) :
                k = bytes(k, "ascii")
            if isinstance(v, str) :
                v = bytes(v, "ascii")
            self._db[k] = v

        def __delitem__(self, k) :
            if isinstance(k, str) :
                k = bytes(k, "ascii")
            del self._db[k]

        def __getattr__(self, v) :
            return getattr(self._db, v)

        def __len__(self) :
            return len(self._db)

        def has_key(self, k) :
            if isinstance(k, str) :
                k = bytes(k, "ascii")
            return k in self._db

        def put(self, key, value, flags=0, txn=None) :
            if isinstance(key, str) :
                key = bytes(key, "ascii")
            return self._db.put(key, bytes(value, "ascii"),
                    flags=flags, txn=txn)

        def get(self, key, txn=None) :
            if isinstance(key, str) :
                key = bytes(key, "ascii")
            v=self._db.get(key, txn=txn)
            if v != None : v = v.decode("ascii")
            return v

        def delete(self, key, txn=None) :
            return self._db.delete(bytes(key, "ascii"), txn=txn)

        def keys(self) :
            k = self._db.keys()
            if len(k) and isinstance(k[0], bytes) :
                return [i.decode("ascii") for i in self._db.keys()]
            else :
                return k

        def associate(self, db, *args, **kwargs) :
            return self._db.associate(db._db, *args, **kwargs)

        def cursor(self, txn=None, flags=0) :
            return cursor_py3k(self._db, txn=txn, flags=flags)

    bsddb._db.DB_orig = bsddb._db.DB
    bsddb.DB = bsddb._db.DB = DB_py3k

    class DBEnv_py3k(object) :
        def __init__(self, *args, **kwargs) :
            self._dbenv = bsddb._db.DBEnv_orig(*args, **kwargs)

        def __getattr__(self, v) :
            return getattr(self._dbenv, v)

    bsddb._db.DBEnv_orig = bsddb._db.DBEnv
    bsddb.DBEnv = bsddb._db.DBEnv = DBEnv_py3k

    class DBSequence_py3k(object) :
        def __init__(self, db, *args, **kwargs) :
            self._db=db
            self._dbsequence = bsddb._db.DBSequence_orig(db._db, *args, **kwargs)

        def __getattr__(self, v) :
            return getattr(self._dbsequence, v)

        def open(self, key, *args, **kwargs) :
            return self._dbsequence.open(bytes(key, "ascii"), *args, **kwargs)

        def get_key(self) :
            return  self._dbsequence.get_key().decode("ascii")

        def get_dbp(self) :
            return self._db

    bsddb._db.DBSequence_orig = bsddb._db.DBSequence
    bsddb._db.DBSequence = DBSequence_py3k

    import string
    string.letters=[chr(i) for i in xrange(65,91)]


try:
    # For Pythons w/distutils pybsddb
    from bsddb3 import db, dbtables, dbutils, dbshelve, \
            hashopen, btopen, rnopen, dbobj
except ImportError:
    # For Python 2.3
    from bsddb import db, dbtables, dbutils, dbshelve, \
            hashopen, btopen, rnopen, dbobj

try:
    from bsddb3 import test_support
except ImportError:
    from test import test_support


try:
    from threading import Thread, currentThread
    del Thread, currentThread
    have_threads = True
except ImportError:
    have_threads = False

verbose = 0
if 'verbose' in sys.argv:
    verbose = 1
    sys.argv.remove('verbose')

if 'silent' in sys.argv:  # take care of old flag, just in case
    verbose = 0
    sys.argv.remove('silent')


def print_versions():
    print
    print '-=' * 38
    print db.DB_VERSION_STRING
    print 'bsddb.db.version():   %s' % (db.version(), )
    print 'bsddb.db.__version__: %s' % db.__version__
    print 'bsddb.db.cvsid:       %s' % db.cvsid
    print 'py module:            %s' % bsddb.__file__
    print 'extension module:     %s' % bsddb._bsddb.__file__
    print 'python version:       %s' % sys.version
    print 'My pid:               %s' % os.getpid()
    print '-=' * 38


def get_new_path(name) :
    get_new_path.mutex.acquire()
    try :
        import os
        path=os.path.join(get_new_path.prefix,
                name+"_"+str(os.getpid())+"_"+str(get_new_path.num))
        get_new_path.num+=1
    finally :
        get_new_path.mutex.release()
    return path

def get_new_environment_path() :
    path=get_new_path("environment")
    import os
    try:
        os.makedirs(path,mode=0700)
    except os.error:
        test_support.rmtree(path)
        os.makedirs(path)
    return path

def get_new_database_path() :
    path=get_new_path("database")
    import os
    if os.path.exists(path) :
        os.remove(path)
    return path


# This path can be overriden via "set_test_path_prefix()".
import os, os.path
get_new_path.prefix=os.path.join(os.sep,"tmp","z-Berkeley_DB")
get_new_path.num=0

def get_test_path_prefix() :
    return get_new_path.prefix

def set_test_path_prefix(path) :
    get_new_path.prefix=path

def remove_test_path_directory() :
    test_support.rmtree(get_new_path.prefix)

if have_threads :
    import threading
    get_new_path.mutex=threading.Lock()
    del threading
else :
    class Lock(object) :
        def acquire(self) :
            pass
        def release(self) :
            pass
    get_new_path.mutex=Lock()
    del Lock



class PrintInfoFakeTest(unittest.TestCase):
    def testPrintVersions(self):
        print_versions()


# This little hack is for when this module is run as main and all the
# other modules import it so they will still be able to get the right
# verbose setting.  It's confusing but it works.
if sys.version_info[0] < 3 :
    import test_all
    test_all.verbose = verbose
else :
    import sys
    print >>sys.stderr, "Work to do!"


def suite(module_prefix='', timing_check=None):
    test_modules = [
        'test_associate',
        'test_basics',
        'test_compare',
        'test_compat',
        'test_cursor_pget_bug',
        'test_dbobj',
        'test_dbshelve',
        'test_dbtables',
        'test_distributed_transactions',
        'test_early_close',
        'test_get_none',
        'test_join',
        'test_lock',
        'test_misc',
        'test_pickle',
        'test_queue',
        'test_recno',
        'test_replication',
        'test_sequence',
        'test_thread',
        ]

    alltests = unittest.TestSuite()
    for name in test_modules:
        #module = __import__(name)
        # Do it this way so that suite may be called externally via
        # python's Lib/test/test_bsddb3.
        module = __import__(module_prefix+name, globals(), locals(), name)

        alltests.addTest(module.test_suite())
        if timing_check:
            alltests.addTest(unittest.makeSuite(timing_check))
    return alltests


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PrintInfoFakeTest))
    return suite


if __name__ == '__main__':
    print_versions()
    unittest.main(defaultTest='suite')
