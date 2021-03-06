"""
Copyright (c) 2008-2022, Jesus Cea Avion <jcea@jcea.es>
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

"""TestCases for using the DB.join and DBCursor.join_item methods.
"""

import os

import unittest

from .test_all import db, dbshelve, rmtree, verbose, \
        get_new_environment_path, get_new_database_path

#----------------------------------------------------------------------

ProductIndex = [
    (b'apple', b"Convenience Store"),
    (b'blueberry', b"Farmer's Market"),
    (b'shotgun', b"S-Mart"),              # Aisle 12
    (b'pear', b"Farmer's Market"),
    (b'chainsaw', b"S-Mart"),             # "Shop smart.  Shop S-Mart!"
    (b'strawberry', b"Farmer's Market"),
]

ColorIndex = [
    (b'blue', b'blueberry'),
    (b'red', b'apple'),
    (b'red', b'chainsaw'),
    (b'red', b'strawberry'),
    (b'yellow', b'peach'),
    (b'yellow', b'pear'),
    (b'black', b'shotgun'),
]

class JoinTestCase(unittest.TestCase):
    keytype = ''

    def setUp(self):
        self.filename = self.__class__.__name__ + '.db'
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL | db.DB_INIT_LOCK )

    def tearDown(self):
        self.env.close()
        rmtree(self.homeDir)

    def test01_join(self):
        if verbose:
            print('\n', '-=' * 30)
            print("Running %s.test01_join..." % \
                  self.__class__.__name__)

        # create and populate primary index
        priDB = db.DB(self.env)
        priDB.open(self.filename, "primary", db.DB_BTREE, db.DB_CREATE)
        list(map(lambda t, priDB=priDB: priDB.put(*t), ProductIndex))

        # create and populate secondary index
        secDB = db.DB(self.env)
        secDB.set_flags(db.DB_DUP | db.DB_DUPSORT)
        secDB.open(self.filename, "secondary", db.DB_BTREE, db.DB_CREATE)
        list(map(lambda t, secDB=secDB: secDB.put(*t), ColorIndex))

        sCursor = None
        jCursor = None
        try:
            # lets look up all of the red Products
            sCursor = secDB.cursor()
            # Don't do the .set() in an assert, or you can get a bogus failure
            # when running python -O
            tmp = sCursor.set(b'red')
            self.assertTrue(tmp)

            # FIXME: jCursor doesn't properly hold a reference to its
            # cursors, if they are closed before jcursor is used it
            # can cause a crash.
            jCursor = priDB.join([sCursor])

            if jCursor.get(0) != (b'apple', b'Convenience Store'):
                self.fail("join cursor positioned wrong")
            if jCursor.join_item() != b'chainsaw':
                self.fail("DBCursor.join_item returned wrong item")
            if jCursor.get(0)[0] != b'strawberry':
                self.fail("join cursor returned wrong thing")
            if jCursor.get(0):  # there were only three red items to return
                self.fail("join cursor returned too many items")
        finally:
            if jCursor:
                jCursor.close()
            if sCursor:
                sCursor.close()
            priDB.close()
            secDB.close()


def test_suite():
    suite = unittest.TestSuite()
    for test in (JoinTestCase,):
        test = unittest.defaultTestLoader.loadTestsFromTestCase(test)
        suite.addTest(test)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
