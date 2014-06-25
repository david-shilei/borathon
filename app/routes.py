import os, sys, inspect

from flask import Flask, render_template, url_for, request, jsonify, session, abort
from download import downloadFiles, processUrl, extractFiles
from pprint import pprint
from jsonpickle import encode
from processlog import processLog, getNLines
from mylogger import logger

app = Flask(__name__)

LOG_PATTERN_FILE = "log_patterns.txt"
ENTITY_PATTERN_FILE = "entity_patterns.txt"
THREAD_ENTITY_FILE = "thread_entity.txt"
log_types = ["hostd.log"]
# note: array stores all entity patterns we are interested, but not used now
entity_patterns = []
# note: hash, key is entity, value is an array of logs for that entity
log_patterns = dict()

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/submit', methods=['GET'])
def submit():
    url=request.args.get('url', '')

    # download and extract support bundles
    urls = processUrl(url.strip())
    local_paths = downloadFiles(urls)
    extracted_dirs = extractFiles(local_paths)

    session['extracted_dirs'] = extracted_dirs
    mapping = processLog(extracted_dirs, log_types, entity_patterns, log_patterns)
    #pprint(mapping)
    return encode(mapping)

@app.route('/testsession')
def testsession():
    #pprint(session['local_paths'])
    return "You have uploaded these support bundles <br>" +  \
           '<br>'.join(session['extracted_dirs'])

@app.route('/raw')
def raw():
    _check_required_fields(request, 'file', 'linenum')
    file_name = request.args.get('file')
    line_num = int(request.args.get('linenum'))
    default_n = 5
    n = int(request.args.get('n')) if request.args.get('n') is not None else default_n
    return getNLines(file_name, line_num, n)

def _check_required_fields(request, *fields):
    if request.args is None:
       logger.info('No args fields.')
       abort(400)
    for field in fields:
       if request.args.get(field) is None:
          logger.info('Missing required args.')
          abort(400)

def loadPatterns():
    global log_patterns
    global entity_patterns
    log_patterns = { log_type : [] for log_type in log_types }

#    with open(ENTITY_PATTERN_FILE) as f:
#        content = f.readlines()
#    f.close()
#    for line in content:
#        line.strip()
#        prefix = log_type + ":"
#        if line.startswith(prefix):
#            entity_patterns.append(line.lstrip(prefix))

    with open(LOG_PATTERN_FILE) as f:
        content = f.readlines()
    f.close()
    for line in content:
        for log_type in log_types:
            prefix = log_type + ":"
            if line.startswith(prefix):
                print line
                log_patterns[log_type].append(line.strip().lstrip(prefix))
                break

if __name__ == '__main__':
    loadPatterns()
    logger.debug(log_patterns)
    app.run(debug=True)
