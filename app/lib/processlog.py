import os
import re
from pprint import pprint

class LogRecord:
    pass

timestamp_pattern = "^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\dZ"
timestamp_regex = re.compile(timestamp_pattern)
timestamp_length = len("2014-05-09T23:17:00.998Z")


def findEntity(file, patterns, thread_entity_patterns):
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
   pprint(entities)
   return entities

def processLog(dirs, supported_logs, patterns, thread_entity_patterns):

    # first step: get logs file who should scan
    log_files = []
    log_types = []
    for directory in dirs:
        for supported in supported_logs:
            log_file = directory + "/var/log/" + supported
            log_files.append(log_file)
            log_types.append(supported)
    #pprint(log_files)
    #pprint(log_types)

    entities = set()
    # second step: get entities
    for log_file, log_type in zip(log_files, log_types):
        _patterns = patterns[log_type]
        _thread_entity_patterns = thread_entity_patterns[log_type]
        #_entities = extractEntity(log_file, _patterns)
        _entities = findEntity(log_file, _patterns, _thread_entity_patterns)

        entities.union(_entities)

    # third step: extract all logs related with the entities
    log_records = dict()
    for log_file in log_files:
        for entity in entities:
            logs = extractLogLines(log_file, entity)
            log_records[entity] = logs
    return log_records

def extractLogLines(file, entity):
    log_records = []
    with open(file) as f:
        for line in f:
            # check if time stamp starts with 2014, trick here
            if line.find(entity) != -1 and line.startswith('2014'):
                record = LogRecord()
                record.timestamp = line[0 : timestamp_length-1]
                record.log = line
                record.source = file
                log_records.append(record)
    return log_records


def extractEntity(file, patterns):
    entities = []
    with open(file) as f:
        for line in f:
            for pattern in patterns:
               p = re.compile(pattern)
               m = p.match(line.strip())
               if m:
                entities.append(m.group('entity'))
    # remove duplicates
    return list(set(entities))

def dumpLogRecords(records):
    for entity in records.keys():
        for record in records[entity]:
            print ("%s, %s,%s") % (entity, record.timestamp, record.log)

