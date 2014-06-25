import os, re, time
import subprocess
from pprint import pprint, pformat
from mylogger import logger

class LogRecord:
    pass

TIMESTAMP_LENGTH = len("2014-05-09T23:17:00.998Z")


def findEntity(file, _entity_patterns, log_patterns):
   thread_entities = {}
   entities = set();
   with open(file) as f:
      for line in f:
         for pattern in thread_entity_patterns:
            p = re.match(pattern.strip(), line)
            if p:
               thread_entities[p.group('thread')] = p.group('opid')
         for pattern in patterns:
            p = re.match(pattern.strip(), line.strip())
            if p:
               entities.add(thread_entities[p.group('thread')])
   logger.debbug(pformat(entities))
   return entities

def processLog(dirs, log_types, entity_patterns, log_patterns):

    # entity to logs mapping, return as result of this fuction
    entity_log_mapping = {}
    # all entities
    entities = set()

    # first step: get logs file who should scan
    _log_files = []
    _log_types= []
    for directory in dirs:
        for supported in log_types:
            log_file = directory + "/var/log/" + supported
            _log_files.append(log_file)
            _log_types.append(supported)
    logger.debug(_log_files)
    logger.debug(_log_types)

    # second step: get entities
    for log_file, log_type in zip(_log_files, _log_types):
        _log_patterns = log_patterns[log_type]
        extractEntities(log_file, _log_patterns, entities)
    logger.debug(entities)

    # third step: extract all logs related with the entities
    for log_file in _log_files:
        for entity in entities:
            extractLogLines(log_file, entity, entity_log_mapping)
    return entity_log_mapping

def convertTimestampToEpoch(timestamp):
    # standard time stamp 2014-05-09T22:27:22.670Z
    datetime = timestamp[:-5]
    ms = timestamp[-4:].rstrip('Z')
    pattern = "%Y-%m-%dT%H:%M:%S"
    epoch = int(time.mktime(time.strptime(datetime, pattern))) * 1000 + int(ms)
    return epoch

def extractLogLines(file, entity, entity_log_mapping):
    with open(file) as f:
        lineNumber = 0
        for line in f:
            # XXX: check if time stamp starts with 2014, should be improved
            if line.find(entity) != -1 and line.startswith('2014'):
                record = LogRecord()
                record.timestamp = line[0 : TIMESTAMP_LENGTH]
                record.log = line
                record.source = file
                record.line = lineNumber
                record.epoch = convertTimestampToEpoch(record.timestamp)
                if entity_log_mapping.get(entity) is None:
                    entity_log_mapping[entity] = [record]
                else:
                    entity_log_mapping[entity].append(record)
            lineNumber += 1

def extractEntities(file, patterns, entities):
    with open(file) as f:
        for line in f:
            for pattern in patterns:
               p = re.compile(pattern)
               m = p.match(line.strip())
               if m:
                   # we allow multiple entityes in one line
                   for entity in m.groups():
                       entities.add(entity)

def dumpLogRecords(records):
    for entity in records.keys():
        for record in records[entity]:
            logger.debug(("%s, %s,%s") % (entity, record.timestamp, record.log))

def getNLines(fileName, lineNum, n):
    cmd = r"""grep -n '' %s |head -%d |tail -%d""" % (fileName, lineNum + n, lineNum - n)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output, err = p.communicate()
    return output

