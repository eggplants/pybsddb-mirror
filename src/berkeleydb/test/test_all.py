"""
Copyright (c) 2008-2020, Jesus Cea Avion <jcea@jcea.es>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

    1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

    3. Neither the name of Jesus Cea Avion nor the names of its
    contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
    CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
    BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
            TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
            DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
    TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
    THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
    SUCH DAMAGE.
    """

"""Run all test cases.
"""

import sys
import os
import unittest
import berkeleydb

from berkeleydb import db, dbutils, dbshelve, \
        hashopen, btopen, rnopen, dbobj

from test import support as test_support


try:
    from threading import Thread, current_thread
    del Thread, current_thread
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
    print()
    print('-=' * 38)
    print(db.DB_VERSION_STRING)
    print('berkeleydb.db.version():   %s' % (db.version(), ))
    if db.version() >= (5, 3) :
        print('berkeleydb.db.full_version(): %s' %repr(db.full_version()))
    print('berkeleydb.db.__version__: %s' % db.__version__)

    # Workaround for allowing generating an EGGs as a ZIP files.
    suffix="__"
    print('py module:            %s' % getattr(berkeleydb, "__file"+suffix))
    print('extension module:     %s' % getattr(berkeleydb, "__file"+suffix))

    print('Test working dir:     %s' % get_test_path_prefix())
    import platform
    print('python version:       %s %s' % \
            (sys.version.replace("\r", "").replace("\n", ""), \
            platform.architecture()[0]))
    print('My pid:               %s' % os.getpid())
    print('-=' * 38)


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
        os.makedirs(path,mode=0o700)
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
get_new_path.prefix=os.path.join(os.environ.get("TMPDIR",
    os.path.join(os.sep,"tmp")), "z-Berkeley_DB")
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


import string

# Transparent Encoding
printable_bytes = [i.encode('ascii') for i in string.printable]


class PrintInfoFakeTest(unittest.TestCase):
    def testPrintVersions(self):
        print_versions()


def suite(module_prefix='', timing_check=None):
    test_modules = [
        'test_associate',
        'test_basics',
        'test_dbenv',
        'test_db',
        'test_compare',
        'test_compat',
        'test_cursor_pget_bug',
        'test_dbobj',
        'test_dbshelve',
        'test_dbtables',
        'test_distributed_transactions',
        'test_early_close',
        'test_concurrent_data_store',
        'test_fileid',
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
        # python's Lib/test/test_berkeleydb.
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
