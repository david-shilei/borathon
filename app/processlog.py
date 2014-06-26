import os, re, time
import subprocess
from pprint import pprint, pformat
from mylogger import logger

class LogRecord:
    pass

TIMESTAMP_LENGTH = len("2014-05-09T23:17:00.998Z")

def getEntityPattern(dirs, conf, entities):
    # first step: get logs file who should scan
    for directory in dirs:
        for c in conf:
            log_file = directory + "/var/log/" + c['log_type']
            extractEntities(log_file, c, entities)

def processLog(dirs, conf):

    # entity to logs mapping, return as result of this fuction
    entity_log_mapping = {}

    # all entities
    entities = dict()

    getEntityPattern(dirs, conf, entities)

    # third step: extract all logs related with the entities'
    for entity in entities.keys():
        entries = SearchLog(entity, os.path.dirname(dirs[0]))
        if entity in entity_log_mapping:
            entity_log_mapping.extends(entries)
        else:
            entity_log_mapping[entity] = entries

    result = []
    for entity in entity_log_mapping:
        single_result = { 'name' : entity, 'logs' : []}
        for log in entity_log_mapping[entity]:
            single_result['logs'].append(log)
        result.append(single_result)

    return { 'entities' : result }



def convertTimestampToEpoch(timestamp):
    # standard time stamp 2014-05-09T22:27:22.670Z
    datetime = timestamp[:-5]
    ms = timestamp[-4:].rstrip('Z')
    pattern = "%Y-%m-%dT%H:%M:%S"
    intms = 0
    try:
        intms = int(ms)
    except:
        pass
    epoch = int(time.mktime(time.strptime(datetime, pattern))) * 1000 + intms
    return epoch

def extractLogLines(file, entity, entity_log_mapping):
    with open(file) as f:
        lineNumber = 0
        for line in f:
            # XXX: check if time stamp starts with 2014, should be improved
            if line.find(entity) != -1 and line.startswith('2014'):
                timestamp =  line[0 : TIMESTAMP_LENGTH]
                record = {
                    'content' : line,
                    'source' : file,
                    'line' : lineNumber,
                    'start' : convertTimestampToEpoch(timestamp)
                }
                if entity_log_mapping.get(entity) is None:
                    entity_log_mapping[entity] = [record]
                else:
                    entity_log_mapping[entity].append(record)
            lineNumber += 1

def extractEntities(file, conf, entities):
    with open(file) as f:
        for line in f:
            for c in conf['details']:
               p = re.compile(c['full'])
               m = p.match(line.strip())
               if m:
                   # we allow multiple entities in one line
                   for entity in m.groups():
                      if entity not in entities:
                         entities[entity] = set()
                      entities[entity].add(c['name'])

def dumpLogRecords(records):
    for entity in records.keys():
        for record in records[entity]:
            logger.debug(("%s, %s,%s") % (entity, record.timestamp, record.log))

def getNLines(fileName, lineNum, n):
    start = lineNum + n
    length = 2 * n + 1
    cmd = r"""cat -n %s |head -%d |tail -%d""" % (fileName, start, length)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output

CODESEARCH_ROOT = os.path.abspath(os.path.join(__file__, '../../bin/codesearch-0.01/'))
CINDEX = os.path.join(CODESEARCH_ROOT, 'cindex')
CSEARCH = os.path.join(CODESEARCH_ROOT, 'csearch')

def RunCmd(cmd, env=None):
    print cmd
    p = subprocess.Popen(args=cmd, executable='/bin/bash', stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True, env=env)
    out, err = p.communicate()
    p.poll()
    ret = p.returncode
    return (ret, out, err)

def IndexLog(path):
    indexPath = os.path.abspath(os.path.join(path, '..', '%s.index' % os.path.basename(path)))
    RunCmd('rm -f %s' % indexPath)
    ret, out, err = RunCmd('%s %s' % (CINDEX, path), env={'CSEARCHINDEX': indexPath})
    if ret != 0:
        raise Exception('Cannot index log, stdout: %s, stderr: %s' % (out, err))

def SearchLog(keyword, path):
    indexPath = os.path.abspath(os.path.join(path, '..', '%s.index' % os.path.basename(path)))
    if not os.path.exists(indexPath):
        IndexLog(path)
    ret, out, err = RunCmd('%s -i -n %s' % (CSEARCH, keyword), env={'CSEARCHINDEX': indexPath})
    lineRegex = re.compile('([^:]*):(\d+):(.*)')
    datetimeRegex = re.compile('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
    result = []
    for line in out.split('\n'):
        if line != None and line != '':
            m = lineRegex.match(line)
            if m:
                logLine = m.group(3)
                timestamp =  logLine[0 : TIMESTAMP_LENGTH]
                if not datetimeRegex.match(timestamp):
                    continue
                if 'verbose' in logLine:
                    continue
                left = max(logLine.find(keyword) - 15, 0)
                right = max(left + len(keyword) + 15, len(line))

                record = {
                    'log' : '...%s...' % logLine[left:right],
                    'source' : m.group(1).replace('%s/' % path, ''),
                    'line' : int(m.group(2)),
                    'epoch' : convertTimestampToEpoch(timestamp)
                }
                result.append(record)
    return sorted(result, key=lambda x: x['epoch'])

if __name__ == '__main__':
    print SearchLog('HB-host-10@10888-3e0d543a-cc-fb6f', '/Users/hackerzhou/Downloads/esx-w2-erqa230-2014-05-09--23.23')
