import os, sys, inspect

import processlog
from processlog import *
import unittest
from pprint import pprint
from mylogger import logger

class TestProcessLog(unittest.TestCase):

    def setUp(self):
        pass

    def equalArray(self, ary1, ary2):
        return len(ary1) == len(ary2) and sorted(ary1) == sorted(ary2)

    def test_extractEntities(self):
        file= u'/tmp/esx-w2-erqa230-2014-05-09--23.23/var/log/hostd.log'
        patterns = ['\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ.*/(?P<entity>.*\.vmx).*Failed to load virtual machine: vim.fault.FileNotFound']
        entities = set()
        extractEntities(file, patterns, entities)
        logger.debug(entities)
        self.assertEqual(len(entities), 2)

    def test_extractLogLines(self):
        file= u'/tmp/esx-w2-erqa230-2014-05-09--23.23/var/log/hostd.log'
        entity = "io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx"
        log_records = dict()
        extractLogLines(file,  entity, log_records)
        self.assertEqual(len(log_records[entity]), 33)

    def test_processLog(self):
        dirs = ["/tmp/esx-w2-erqa230-2014-05-09--23.23"]
        supported_logs = ['hostd.log']
        entity_patterns = []
        patterns = {'hostd.log' : ['\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ ' \
                                   '\[(?P<thread>.*?) .*/(?P<entity>.*\.vmx).*' \
                                   'Failed to load virtual machine: vim.fault.FileNotFound']}
        log_records = processLog(dirs, supported_logs, entity_patterns, patterns)
        entity = "io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx"
        self.assertEqual(len(log_records[entity]), 33)

    def test_convertTimestampToEpoch(self):
        timestamp = "2014-05-09T22:27:22.670Z"
        ret = convertTimestampToEpoch(timestamp)
        self.assertEqual(ret, 1399645642670)

    def test_getNLines(self):
       file=u'./test_processlog.py'
       linenum = 15
       n = 5
       lines = getNLines(file, linenum, n).rstrip().split('\n')
       print lines
       self.assertEqual(11, len(lines))
       linenum = 10
       n = 2
       lines = getNLines(file, linenum, n).rstrip().split('\n')
       print lines
       self.assertEqual(5, len(lines))
if __name__ == '__main__':
    unittest.main()

