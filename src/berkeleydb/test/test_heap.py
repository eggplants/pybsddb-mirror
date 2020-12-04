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

"""TestCase for reseting File ID.
"""

import os, sys
import shutil
import unittest

from .test_all import db, test_support, get_new_environment_path, get_new_database_path

@unittest.skipIf(db.version() < (5, 3),
                 'Oracle Berkeley DB 4.8 has no HEAP access method support')
class HeapTestCase(unittest.TestCase):
    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL |
                                    db.DB_INIT_LOG | db.DB_INIT_TXN)
        self.db = db.DB(self.env)

    def tearDown(self):
        self.db.close()
        self.env.close()
        test_support.rmtree(self.homeDir)

    def test_heapsize(self):
        self.assertEqual((0, 0), self.db.get_heapsize())
        self.db.set_heapsize(12, 3456789)
        self.assertEqual((12, 3456789), self.db.get_heapsize())

    def test_heap_regionsize(self):
        self.assertEqual(0, self.db.get_heap_regionsize())
        self.db.set_heap_regionsize(123456789)
        self.assertEqual(123456789, self.db.get_heap_regionsize())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HeapTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
