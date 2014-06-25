import os, sys, inspect

import download
from download import processUrl, downloadFile
import unittest
from pprint import pprint
from mylogger import logger

class TestUtil(unittest.TestCase):

    def setUp(self):
        pass

    def equalArray(self, ary1, ary2):
        return len(ary1) == len(ary2) and sorted(ary1) == sorted(ary2)

    def test_processUrl(self):
        # make sure the extended urls for tgz files are correct
        url = "1249097/*.tgz"
        output = processUrl(url)
        expected = [
         u'http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/esx-w2-erqa230-2014-05-09--23.23.tgz',
         u'http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/esx-w2-erqa231-2014-05-09--23.23.tgz',
         u'http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/esx-w2-erqa232-2014-05-09--23.23.tgz',
         u'http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/esx-w2-erqa233-2014-05-09--23.23.tgz']
        self.assertTrue(self.equalArray(output, expected))

    def test_downloadUrl(self):
        # make sure all the tgz files for a url is downloaded correctly
        url = "http://engweb.eng.vmware.com/bugs/files/0/1/2/4/9/0/9/7/esx-w2-erqa230-2014-05-09--23.23.tgz"
        local_path = downloadFile("/tmp/", url)
        logger.debug(local_path)
        self.assertEqual(os.path.getsize(local_path), 162180210)


if __name__ == '__main__':
    unittest.main()
