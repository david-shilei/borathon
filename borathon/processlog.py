import os, re, time
import subprocess
from pprint import pprint, pformat
from mylogger import logger
from multiprocessing import Pool

class LogRecord:
    pass

TIMESTAMP_LENGTH = len("2014-05-09T23:17:00.998Z")

entities = dict()
pr = dict()

def getEntityPattern(dirs, conf, entities, pr):
    # first step: get logs file who should scan
    for directory in dirs:
        for c in conf:
            log_file = directory + "/var/log/" + c['log_type']
            extractEntities(log_file, c, entities, pr)

def getBugzillaRecords(entity):
    bugs = []
    if not pr:
       return []
    patterns = pr.get(entity)
    if not patterns:
       return []
    for p in patterns:
       cmd = r"""python bugzilla.py -q txie '%s' -w bug_id,short_desc|grep '|.*\d.*'""" % (p)
       p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
       output, err = p.communicate()
       lines = output.strip().split('\n')
       for l in lines:
          bug_id, summary = l.strip('|').split('|')
          pair = {}
          pair['id'] = bug_id.strip()
          pair['value'] = summary.strip()
          bugs.append(pair)
    return bugs

def SearchLogInt(obj):
    return SearchLog(obj[0], obj[1])

def processLog(dirs, conf, offset=0, limit=1000):
    # entity to logs mapping, return as result of this fuction
    entity_log_mapping = {}

    # all entities
    global entities
    entities = dict()
    entities['host'] = {}
    entities['vm'] = {}
    global pr
    pr = dict()

    getEntityPattern(dirs, conf, entities, pr)

    # third step: extract all logs related with the entities'
    p = Pool(8)
    all_entries = []
    all_keys = []
    for entityType in entities.keys():
        for entity in entities[entityType]:
            all_keys.append([entity, os.path.dirname(dirs[0])])
        #for entity in entities[entityType]:
            #entries = SearchLog(entity, os.path.dirname(dirs[0]))
            #all_entries.extend(entries)
    results = p.map(SearchLogInt, all_keys)
    for result in results:
        all_entries.extend(result)

    all_entries.sort(lambda x, y: cmp(x['start'], y['start']))
    filterEntries = []
    tmp = {}
    for entry in all_entries:
        summary = entry['content']
        if summary in tmp and abs(long(entry['start']) - long(tmp[summary])) <= 60000 * 10:
            continue
        else:
            tmp[summary] = entry['start']
            filterEntries.append(entry)
    if offset >= len(filterEntries):
        offset = len(filterEntries) - 1
    if offset + limit >= len(filterEntries):
        limit = len(filterEntries) - offset
    all_entries = filterEntries[offset:offset + limit]
    for entry in all_entries:
        entity = entry['entity']
        root = None
        if '.vmx' in entity:
            root = entities['vm']
        elif entity.startswith('host-'):
            root = entities['host']
        if entity not in root or isinstance(root[entity], set):
            root[entity] = []
        root[entity].append(entry)

    #result = []
    #for entity in entity_log_mapping:
    #    single_result = { 'name' : entity, 'logs' : []}
    #    for log in entity_log_mapping[entity]:
    #        single_result['logs'].append(log)
    #    result.append(single_result)

    for key in entities.keys():
        for entity in entities[key].keys():
            if entities[key][entity] == []:
                entities[key].pop(entity, None)
                continue
            entities[key][entity].sort(lambda x, y: cmp(x['start'], y['start']))
    if len(entities['vm']) == 0:
        entities.pop('vm', None)
    if len(entities['host']) == 0:
        entities.pop('host', None)
    return entities

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
    epoch = long(time.mktime(time.strptime(datetime, pattern))) * 1000 + intms
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

def extractEntities(file, conf, entities, pr):
    if not os.path.exists(file):
        return
    with open(file) as f:
        for line in f:
            for c in conf['details']:
                p = re.compile(c['full'])
                m = p.match(line.strip())
                if m:
                    # we allow multiple entities in one line
                    for entity in m.groups():
                        root = None
                        if '.vmx' in entity:
                            root = entities['vm']
                        elif entity.startswith('host-'):
                            root = entities['host']

                        if root == None:
                            continue

                        if entity not in root:
                            root[entity] = []
                        if entity not in pr:
                           pr[entity] = set()
                        pr[entity].add(c['name'])

def dumpLogRecords(records):
    for entity in records.keys():
        for record in records[entity]:
            logger.debug(("%s, %s,%s") % (entity, record.timestamp, record.log))

def getNLines(fileName, lineNum, n):
    start = lineNum + n
    length = 2 * n + 1
    cmd = r"""cat -n %s/%s |head -%d |tail -%d""" % (os.path.dirname(__file__), fileName, start, length)
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
                epoch = convertTimestampToEpoch(timestamp)
                left = logLine.find(keyword)
                right = min(left + len(keyword) + 30, len(logLine))
                summary = '%s...' % logLine[left:right]
                className = ''
                if ' error ' in logLine.lower():
                    className = 'error'
                elif ' info ' in logLine.lower():
                    className = 'info'
                elif ' verbose ' in logLine.lower():
                    className = 'verbose'
                elif ' warning ' in logLine.lower():
                    className = 'warning'

                record = {
                    'content' : summary,
                    'source' : m.group(1).replace('%s/' % os.path.dirname(__file__), ''),
                    'line' : int(m.group(2)),
                    'start' : convertTimestampToEpoch(timestamp),
                    'entity': keyword,
                    'className': className
                }
                result.append(record)
    return sorted(result, key=lambda x: x['start'])
