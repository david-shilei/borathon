import os, sys, inspect
# realpath() with make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# use this if you want to include modules from a subforder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../lib")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

import processlog
from processlog import extractLogLines,  extractEntity, processLog, dumpLogRecords

import unittest
from pprint import pprint

class TestProcessLog(unittest.TestCase):

    def setUp(self):
        pass

    def equalArray(self, ary1, ary2):
        return len(ary1) == len(ary2) and sorted(ary1) == sorted(ary2)

    def test_extractEntity(self):
        file= u'/tmp/esx-w2-erqa230-2014-05-09--23.23/var/log/hostd.log'
        patterns = ['\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ.*/(?P<entity>.*\.vmx).*Failed to load virtual machine: vim.fault.FileNotFound']
        entities = extractEntity(file, patterns)
        pprint(entities)
        self.assertEqual(len(entities), 2)

    def test_extractLogLines(self):
        file= u'/tmp/esx-w2-erqa230-2014-05-09--23.23/var/log/hostd.log'
        entity = "io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx"
        log_records = extractLogLines(file,  entity)
        self.assertEqual(len(log_records), 33)

    def test_processLog(self):
        dirs = ["/tmp/esx-w2-erqa230-2014-05-09--23.23"]
        supported_logs = ['hostd.log']
        patterns = {'hostd.log' : ['\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ.*/(?P<entity>.*\.vmx).*Failed to load virtual machine: vim.fault.FileNotFound']}
        log_records = processLog(dirs, supported_logs, patterns) 
        #dumpLogRecords(log_records)
        entity = "io-10.139.130.110-vsanDatastore-rhel6-64-vmwpv-lc-0028.vmx"
        self.assertEqual(len(log_records[entity]), 33)

if __name__ == '__main__':
    unittest.main()

