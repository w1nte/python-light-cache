import os
import shutil

from unittest import TestCase
from light_cache import Cache
from time import sleep


class TestCache(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestCache, self).__init__(*args, **kwargs)

        # setup test variables and functions
        self.cache_dir = 'cache'
        self.getFileCount = lambda: len(
            [n for n in os.listdir(self.cache_dir) if os.path.isfile(os.path.join(self.cache_dir, n))])
        self.removeCacheDir = lambda: shutil.rmtree(self.cache_dir) if os.path.isdir(self.cache_dir) else False

    def setUp(self):
        # remove test cache dir
        self.removeCacheDir()

        # create test cache class
        self.cache = Cache(directory=self.cache_dir)

    def tearDown(self):
        self.removeCacheDir()

    def testSet(self):
        files = self.getFileCount()

        # test setter
        set1 = self.cache.set('set1', b'Hello World! Hello World! Hello World!')
        self.assertIsInstance(set1, str)
        set2 = self.cache.set('set2', b'Test')
        self.assertIsInstance(set2, str)

        # overwrite set1
        set1_2 = self.cache.set('set1', b'Hello')
        self.assertIsInstance(set1_2, str)

        set4 = self.cache.set('set4', b'Hello')
        self.assertIsInstance(set4, str)

        # compares the file size of the overwritten set1 and the new set4, it has to be the same
        size_set1_2 = os.path.getsize(set1_2)
        size_set4 = os.path.getsize(set4)
        self.assertEqual(size_set1_2, size_set4, 'unequal file size of two files that should be the same!')

        # checks the count of files in the directory
        self.assertEqual(files, (self.getFileCount() - 3), 'too many files in the cache directory')

    def testGet(self):

        # tests whether the content is the same
        self.cache.set('set1', b'Hello World')
        self.assertEqual(self.cache.get('set1'), b'Hello World', 'the cache file content is corrupted!')

        # overwrites set1
        self.cache.set('set1', b'Hello')
        self.assertEqual(self.cache.get('set1'), b'Hello', 'overwriting; the cache file content is corrupted!')

        # sets the expiration time very short, should return false
        self.cache.set('set2', b'Hello', 0.1)
        sleep(0.5)
        self.assertEqual(self.cache.get('set2'), False, 'expiration time is over, but the file is still present!')

    def testRemove(self):

        self.cache.set('set1', b'Hello World')
        self.cache.set('set2', b'Hello World', 0.1)
        sleep(0.5)
        self.assertEqual(self.getFileCount(), 2)

        self.cache.remove('set1', False)
        self.cache.remove('set2')
        self.assertEqual(self.getFileCount(), 1)

        self.cache.remove('set1', True)
        self.assertEqual(self.getFileCount(), 0)

    def testClear(self):

        self.cache.set('set1', b'Hello World', 0)
        self.cache.set('set2', b'Hello World', 0)
        self.cache.set('set3', b'Hello World', 0)
        self.cache.set('set4', b'Hello World')
        self.cache.set('set5', b'Hello World')
        self.cache.set('set6', b'Hello World')

        sleep(0.5)

        self.cache.clear()

        self.assertEqual(self.getFileCount(), 3)

        # creates a file to check whether only valid files are deleted.
        with open(os.path.join(self.cache_dir, 'test.tmp'), 'w+') as f:
            f.write('42')

        self.cache.clear(True)

        self.assertEqual(self.getFileCount(), 1)