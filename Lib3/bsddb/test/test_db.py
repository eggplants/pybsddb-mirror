import unittest
import os, glob

from .test_all import db, test_support, get_new_environment_path, \
        get_new_database_path

#----------------------------------------------------------------------

class DB(unittest.TestCase):
    import sys
    if sys.version_info[:3] < (2, 4, 0):
        def assertTrue(self, expr, msg=None):
            self.failUnless(expr,msg=msg)

    def setUp(self):
        self.path = get_new_database_path()
        self.db = db.DB()

    def tearDown(self):
        self.db.close()
        del self.db
        test_support.rmtree(self.path)

class DB_general(DB) :
    if db.version() >= (4, 2) :
        def test_lorder(self) :
            self.db.set_lorder(1234)
            self.assertEqual(1234, self.db.get_lorder())
            self.db.set_lorder(4321)
            self.assertEqual(4321, self.db.get_lorder())
            self.assertRaises(db.DBInvalidArgError, self.db.set_lorder, 9182)

class DB_hash(DB) :
    if db.version() >= (4, 2) :
        def test_h_ffactor(self) :
            for ffactor in [4, 16, 256] :
                self.db.set_h_ffactor(ffactor)
                self.assertEqual(ffactor, self.db.get_h_ffactor())

        def test_h_nelem(self) :
            for nelem in [1, 2, 4] :
                nelem = nelem*1024*1024  # Millions
                self.db.set_h_nelem(nelem)
                self.assertEqual(nelem, self.db.get_h_nelem())

        def test_pagesize(self) :
            for i in range(9, 17) :  # From 512 to 65536
                i = 1<<i
                self.db.set_pagesize(i)
                self.assertEqual(i, self.db.get_pagesize())

            # The valid values goes from 512 to 65536
            # Test 131072 bytes...
            self.assertRaises(db.DBInvalidArgError, self.db.set_pagesize, 1<<17)
            # Test 256 bytes...
            self.assertRaises(db.DBInvalidArgError, self.db.set_pagesize, 1<<8)

class DB_recno(DB) :
    if db.version() >= (4, 2) :
        def test_re_pad(self) :
            for i in [' ', '*'] :  # Check chars
                self.db.set_re_pad(i)
                self.assertEqual(ord(i), self.db.get_re_pad())
            for i in [97, 65] :  # Check integers
                self.db.set_re_pad(i)
                self.assertEqual(i, self.db.get_re_pad())

class DB_queue(DB) :
    if db.version() >= (4, 2) :
        def test_re_len(self) :
            for i in [33, 65, 300, 2000] :
                self.db.set_re_len(i)
                self.assertEqual(i, self.db.get_re_len())

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(DB_general))
    suite.addTest(unittest.makeSuite(DB_hash))
    suite.addTest(unittest.makeSuite(DB_recno))
    suite.addTest(unittest.makeSuite(DB_queue))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
