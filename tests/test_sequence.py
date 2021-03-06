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

import unittest
import os

from .test_all import db, rmtree, get_new_environment_path, get_new_database_path


class DBSequenceTest(unittest.TestCase):
    def setUp(self):
        self.int_32_max = 0x100000000
        self.homeDir = get_new_environment_path()
        self.filename = "test"

        self.dbenv = db.DBEnv()
        self.dbenv.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL, 0o666)
        self.d = db.DB(self.dbenv)
        self.d.open(self.filename, db.DB_BTREE, db.DB_CREATE, 0o666)

    def tearDown(self):
        if hasattr(self, 'seq'):
            self.seq.close()
            del self.seq
        if hasattr(self, 'd'):
            self.d.close()
            del self.d
        if hasattr(self, 'dbenv'):
            self.dbenv.close()
            del self.dbenv

        rmtree(self.homeDir)

    def test_get(self):
        self.seq = db.DBSequence(self.d, flags=0)
        start_value = 10 * self.int_32_max
        self.assertEqual(0xA00000000, start_value)
        self.assertEqual(None, self.seq.initial_value(start_value))
        self.assertEqual(None, self.seq.open(key=b'id', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(start_value, self.seq.get(5))
        self.assertEqual(start_value + 5, self.seq.get())

    def test_remove(self):
        self.seq = db.DBSequence(self.d, flags=0)
        self.assertEqual(None, self.seq.open(key=b'foo', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(None, self.seq.remove(txn=None, flags=0))
        del self.seq

    def test_get_key(self):
        self.seq = db.DBSequence(self.d, flags=0)
        key = b'foo'
        self.assertEqual(None, self.seq.open(key=key, txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(key, self.seq.get_key())

    def test_get_dbp(self):
        self.seq = db.DBSequence(self.d, flags=0)
        self.assertEqual(None, self.seq.open(key=b'foo', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(self.d, self.seq.get_dbp())

    def test_cachesize(self):
        self.seq = db.DBSequence(self.d, flags=0)
        cashe_size = 10
        self.assertEqual(None, self.seq.set_cachesize(cashe_size))
        self.assertEqual(None, self.seq.open(key=b'foo', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(cashe_size, self.seq.get_cachesize())

    def test_flags(self):
        self.seq = db.DBSequence(self.d, flags=0)
        flag = db.DB_SEQ_WRAP;
        self.assertEqual(None, self.seq.set_flags(flag))
        self.assertEqual(None, self.seq.open(key=b'foo', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(flag, self.seq.get_flags() & flag)

    def test_range(self):
        self.seq = db.DBSequence(self.d, flags=0)
        seq_range = (10 * self.int_32_max, 11 * self.int_32_max - 1)
        self.assertEqual(None, self.seq.set_range(seq_range))
        self.seq.initial_value(seq_range[0])
        self.assertEqual(None, self.seq.open(key=b'foo', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(seq_range, self.seq.get_range())

    def test_stat(self):
        self.seq = db.DBSequence(self.d, flags=0)
        self.assertEqual(None, self.seq.open(key=b'foo', txn=None,
                                             flags=db.DB_CREATE))
        stat = self.seq.stat()
        for param in ('nowait', 'min', 'max', 'value', 'current',
                      'flags', 'cache_size', 'last_value', 'wait'):
            self.assertTrue(param in stat, "parameter %s isn't in stat info" % param)

    # This code checks a crash solved in Berkeley DB 4.7
    def test_stat_crash(self) :
        d=db.DB()
        d.open(None,dbtype=db.DB_HASH,flags=db.DB_CREATE)  # In RAM
        seq = db.DBSequence(d, flags=0)

        self.assertRaises(db.DBNotFoundError, seq.open,
                key=b'id', txn=None, flags=0)

        self.assertRaises(db.DBInvalidArgError, seq.stat)

        d.close()

    def test_64bits(self) :
        # We don't use both extremes because they are problematic
        value_plus=(1<<63)-2
        self.assertEqual(9223372036854775806,value_plus)
        value_minus=(-1<<63)+1  # Two complement
        self.assertEqual(-9223372036854775807,value_minus)
        self.seq = db.DBSequence(self.d, flags=0)
        self.assertEqual(None, self.seq.initial_value(value_plus-1))
        self.assertEqual(None, self.seq.open(key=b'id', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(value_plus-1, self.seq.get(1))
        self.assertEqual(value_plus, self.seq.get(1))

        self.seq.remove(txn=None, flags=0)

        self.seq = db.DBSequence(self.d, flags=0)
        self.assertEqual(None, self.seq.initial_value(value_minus))
        self.assertEqual(None, self.seq.open(key=b'id', txn=None,
                                             flags=db.DB_CREATE))
        self.assertEqual(value_minus, self.seq.get(1))
        self.assertEqual(value_minus+1, self.seq.get(1))

    def test_multiple_close(self):
        self.seq = db.DBSequence(self.d)
        self.seq.close()  # You can close a Sequence multiple times
        self.seq.close()
        self.seq.close()

def test_suite():
    suite = unittest.TestSuite()
    for test in (DBSequenceTest,):
        test = unittest.defaultTestLoader.loadTestsFromTestCase(test)
        suite.addTest(test)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
